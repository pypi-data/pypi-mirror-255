import os, time, json, base64, logging, traceback, multiprocessing
from abc import ABC, abstractmethod
from vectormpp.loggers import initWorkerLogger
from vectormpp.client import command, kubectl, helm

logger = logging.getLogger(__name__)

class Task(ABC):
    def __init__(self, r, resources):
        self.r = r
        self.resources = resources
        self.resource = resources[r]

    def perform(self, action):
        if action == "install_or_upgrade":
            self.install_or_upgrade()
        elif action == "uninstall":
            self.uninstall()
        self.wait_for_completion(action)
        if action == "install_or_upgrade":
            self.collect_information()

    @abstractmethod
    def install_or_upgrade(self):
        pass

    @abstractmethod
    def uninstall(self):
        pass

    def wait_for_completion(self, action):
        for bc in self.resource.get("beacon", []):
            if "jsonpath" in bc:
                if action == "install_or_upgrade":
                    kubectl.wait_for_desire(bc)
            else:
                if action == "install_or_upgrade":
                    kubectl.wait_for_readiness(bc)
                elif action == "uninstall":
                    kubectl.wait_for_deletion(bc)

    def collect_information(self):
        for k, v in self.resource.get('supply', {}).items():
            if not isinstance(v, str):
                self.resource['supply'][k] = command.run(v['command'], self.resource.get('host'), exceptionOnFail = True)[1]

class YAMLTask(Task):
    def install_or_upgrade(self):
        need = self.resource.get('isNamespace') or kubectl.should_install_or_upgrade(self.resource['yamlFiles'])
        if not need:
            logger.info(f"Resource {self.r} is up to date.")
            return
        kubectl.install_or_upgrade(self.resource['yamlFiles'])
        logger.info(f"Resource {self.r} is installed/upgraded successfully.")

    def uninstall(self):
        if self.resource.get('isNamespace'):
            logger.info(f"Ingore Namespace {self.r}")
            return
        kubectl.uninstall(self.resource['yamlFiles'])
        logger.info(f"Resource {self.r} not found or uninstalled successfully.")

class ChartTask(Task):
    def install_or_upgrade(self):
        chart = self.resource["chart"]
        release = self.resource["release"]
        release["currentRevision"] = helm.get_current_revision(release["name"], release["namespace"])
        if "additionalValues" in release:
            def fill_additinal_values(additionalValues):
                res = []
                for adv in additionalValues:
                    if isinstance(adv["value"], dict):
                        _r = adv["value"]["resource"]
                        _k = adv["value"]["key"]
                        value = self.resources[_r]["supply"][_k]
                        adv['value'] = value
                    res.append(adv)
                return res
            release['additionalValues'] = fill_additinal_values(release["additionalValues"])
        need = False
        if not release["currentRevision"]:
            logger.info(f"Resource {self.r} not found.")
            need = True
        elif helm.should_install_or_upgrade(release, chart):
            logger.info(f"Resource {self.r} out of date.")
            need = True
        if need == False:
            logger.info(f"Release {release['name']} in namespace {release['namespace']} is up to date.")
            return
        helm.install_or_upgrade(release, chart)

    def uninstall(self):
        release = self.resource["release"]
        release["currentRevision"] = helm.get_current_revision(release["name"], release["namespace"])
        if not release["currentRevision"]:
            logger.info(f"Resource {self.r} not found.")
            return
        logger.info(f"Revision of Release {release['name']} in namespace {release['namespace']}: {release['currentRevision'].revision}.")
        logger.info(f"Start to uninstall Release {release['name']} (Revision {release['currentRevision'].revision}) in namespace {release['namespace']}.")
        helm.uninstall(release)
        logger.info(f"Resource {self.r} uninstalled successfully.")

class CommandTask(Task):
    def install_or_upgrade(self):
        if self.resource.get('doneSigns') and command.runs(self.resource['doneSigns'], self.resource.get('host')):
            logger.info(f"Resource {self.r} of Type {self.resource['type']} is done before.")
        elif self.resource.get('commands'):
            command.runs(self.resource['commands'], self.resource.get('host'), exceptionOnFail = True)

    def uninstall(self):
        logger.info(f"Ingore Resource {self.r} of Type {self.resource['type']}")

class SecretTask(Task):
    def __init__(self, r, resources):
        super().__init__(r, resources)
        self.folder = resources[r]['yamlFolder']
        os.makedirs(self.folder, exist_ok = True)

    def create_docker_registry_yaml(self, secret):
        auth = base64.b64encode(f"{secret['username']}:{secret['password']}".encode("utf-8")).decode("utf-8")
        config_dict = {
            "auths": {
                secret['registry']: {
                    "username": secret['username'],
                    "password": secret['password'],
                    "email": "",
                    "auth": auth,
                }
            }
        }
        encoded_json = base64.b64encode(json.dumps(config_dict).encode("utf-8")).decode("utf-8")
        secret_yaml = f"""
apiVersion: v1
kind: Secret
metadata:
    name: {secret['name']}
    namespace: {secret['namespace']}
data:
    .dockerconfigjson: {encoded_json}
type: kubernetes.io/dockerconfigjson
""".strip()
        yaml_file = os.path.join(self.folder, f"{secret['namespace']}-{secret['name']}.yaml")
        with open(yaml_file, 'w') as fo:
            fo.write(secret_yaml)
        return yaml_file

    def create_generic_from_file_yaml(self, secret):
        with open(secret['file'], 'rb') as fo:
            file_content = fo.read()
        encoded_content = base64.b64encode(file_content).decode()
        file_name = os.path.basename(secret['file'])
        secret_yaml = f"""
apiVersion: v1
kind: Secret
metadata:
    name: {secret['name']}
    namespace: {secret['namespace']}
data:
    {file_name}: {encoded_content}
type: Opaque
""".strip()
        yaml_file = os.path.join(self.folder, f"{secret['namespace']}-{secret['name']}.yaml")
        with open(yaml_file, 'w') as fo:
            fo.write(secret_yaml)
        return yaml_file

    def install_or_upgrade(self):
        methods = {
                "docker-registry": self.create_docker_registry_yaml,
                "generic-file": self.create_generic_from_file_yaml,
                }
        yaml_file = methods[self.resource['secretType']](self.resource["secret"])
        if not kubectl.should_install_or_upgrade([yaml_file]):
            logger.info(f"Resource {self.r} is up to date.")
            return
        kubectl.install_or_upgrade([yaml_file])
        logger.info(f"Resource {self.r} is installed/upgraded successfully.")

    def uninstall(self):
        logger.info(f"Ingore Resource {self.r} of Type {self.resource['type']}")

TaskMapping = {
        'yaml': YAMLTask,
        'chart': ChartTask,
        'command': CommandTask,
        'secret': SecretTask,
        }

class Executor:
    def __init__(self, shared_resources, lock, event, logger_queue, loglevel):
        self.resources = shared_resources
        self.lock = lock
        self.event = event
        self.logger_queue = logger_queue
        self.loglevel = loglevel

    def start(self, action):
        try:
            initWorkerLogger(self.logger_queue, self.loglevel)
            logger.info(f"{multiprocessing.current_process().name} starts.")
            sleep_counter = 0
            while True:
                if self.event.is_set():
                    logger.error(f"{multiprocessing.current_process().name} Exit: Exception detected in another process.")
                    return
                resource_to_execute = None
                with self.lock:
                    if all((v.get("isDone") == True or v.get("isExecuting") == True) for v in self.resources.values()):
                        break
                    for name, resource in self.resources.items():
                        if all(self.resources[dep].get("isDone") == True for dep in resource.get("dependsOn", [])) and not resource.get("isExecuting") and not resource.get("isDone"):
                            resource_to_execute = name
                            self.resources[name]["isExecuting"] = True
                            break
                if not resource_to_execute:
                    if sleep_counter % 20 == 0:
                        logger.info(f"{multiprocessing.current_process().name} Waiting for valid task...")
                    time.sleep(1)
                    sleep_counter += 1
                    continue
                logger.info(f"{multiprocessing.current_process().name} works on <============ {resource_to_execute} ============>")
                TaskMapping[self.resources[resource_to_execute]['type']](resource_to_execute, self.resources).perform(action)
                with self.lock:
                    self.resources[resource_to_execute]["isDone"] = True
            logger.info(f"{multiprocessing.current_process().name} ends.")
        except Exception as e:
            logger.error(f"Receive Exception:\n{traceback.format_exc().strip()}")
            logger.error(f"{multiprocessing.current_process().name} Exit.")
            self.event.set()
