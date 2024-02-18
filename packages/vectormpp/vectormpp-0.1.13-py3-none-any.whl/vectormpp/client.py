import yaml, time, pyhelm3, asyncio, logging, subprocess

logger = logging.getLogger(__name__)

def msg(cmd, out, err):
    message = out + '\n' + err
    return ' '.join(cmd) + ": " + message.strip()

class CommandError(Exception):
    def __init__(self, cmd, result):
        super().__init__(msg(cmd, result.stdout.strip(), result.stderr.strip()))

class KubectlError(Exception):
    def __init__(self, cmd, out, err):
        super().__init__(msg(cmd, out, err))

class Command:
    def run(self, cmd, host = None, exceptionOnFail = False):
        _cmd = cmd.split() if isinstance(cmd, str) else cmd
        if not host:
            cmd = _cmd
        elif host['type'] == 'deployment':
            name = f"deployment/{host['name']}"
            cmd = ["kubectl", "exec", name, "--namespace", host['namespace'], '--']
            cmd.extend(_cmd)
        elif host['type'] == 'pod':
            cmd = ["kubectl", "exec", host['name'], "--namespace", host['namespace'], '--']
            cmd.extend(_cmd)
        else:
            raise Exception(f"Unsupport host type: {host['type']}")
        logger.info(f"{' '.join(cmd)}: start...")
        if "|" in cmd:
            _cmd = ' '.join(cmd)
            result = subprocess.run(_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True, shell = True)
        else:
            result = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
        if result.returncode != 0:
            if exceptionOnFail:
                raise CommandError(cmd, result)
            logger.info(f"{' '.join(cmd)}: return {result.returncode}.")
        else:
            logger.info(f"{' '.join(cmd)}: succeed.")
        logger.debug(f"{msg(cmd, result.stdout.strip(), result.stderr.strip())}.")
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def runs(self, cmds, host = None, exceptionOnFail = False):
        for cmd in cmds:
            if self.run(cmd, host, exceptionOnFail)[0] != 0:
                return False
        return True

class Kubectl(Command):
    def serialize_labels(self, labels):
        selectors = []
        for k, v in labels.items():
            if isinstance(v, list):
                selectors.append(f"{k} in ({','.join(v)})")
            elif isinstance(v, str):
                selectors.append(f"{k}={v}")
            else:
                raise Exception(f"Unkown Label Structure {labels}")
        return ','.join(selectors)

    def wait_for_beacon(self, beacon, wait_for):
        cmd = ['kubectl', 'wait', beacon.get('target', 'pod'), f"--for={wait_for}"]
        if 'namespace' in beacon:
            cmd.extend(['--namespace', beacon['namespace']])
        else:
            cmd.append('-A')
        if 'labels' in beacon:
            label_selector = self.serialize_labels(beacon['labels'])
            cmd.extend(['-l', label_selector])
        cmd.extend(['--timeout', beacon.get('timeout', '5m')])
        code, out, err = self.run(cmd)
        if code != 0:
            if wait_for == 'delete' and "the server doesn't have a resource type" in err:
                logger.info(f"The CRD of {beacon['target']} Not Found.")
                return
            raise KubectlError(cmd, out, err)

    def wait_for_readiness(self, beacon):
        self.wait_for_beacon(beacon, 'condition=Ready')

    def wait_for_deletion(self, beacon):
        self.wait_for_beacon(beacon, 'delete')

    def wait_for_desire(self, beacon):
        timeout = int(beacon.get('timeout', '300'))
        start_time = time.time()
        archived = False
        while time.time() - start_time < timeout:
            cmd = ["kubectl", "get", beacon["name"], "--namespace", beacon['namespace'], '-o', f"jsonpath='{beacon['jsonpath']}'"]
            code, out, err = self.run(cmd)
            if code == 0:
                state = out.strip("'")
                if state == beacon["desire"]:
                    logger.info(f"{' '.join(cmd)}: achieve desired: {state}.")
                    archived = True
                    break
                logger.info(f"{' '.join(cmd)}: Current state: '{state}', continue waiting for desire state {beacon['desire']}...")
            else:
                if "NotFound" in err or "not found" in err:
                    logger.info(f"{' '.join(cmd)}: {beacon['name']} not found yet.")
                else:
                    raise KubectlError(cmd, out, err)
            time.sleep(20)
        if not archived:
            raise Exception(f"Timeout: {' '.join(cmd)}: not achieve desired: {beacon['desire']}.")

    def should_install_or_upgrade(self, yamlFiles):
        yamls = {file: 0 for file in yamlFiles}
        for f in yamls:
            cmd = ["kubectl", "diff", "-f", f]
            code, out, err = self.run(cmd)
            if code == 0:
                logger.info(f"{' '.join(cmd)}: no difference.")
            elif code == 1:
                logger.info(f"{' '.join(cmd)}: Changed.")
                yamls[f] += 1
            else:
                raise KubectlError(cmd, out, err)
        return sum(yamls.values()) > 0

    def install_or_upgrade(self, yamlFiles):
        for f in yamlFiles:
            cmd = ['kubectl', 'apply', '-f', f]
            self.run(cmd, exceptionOnFail = True)

    def uninstall(self, yamlFiles):
        for f in yamlFiles:
            cmd = ['kubectl', 'delete', '-f', f]
            code, out, err = self.run(cmd)
            if code == 0:
                logger.info(f"{' '.join(cmd)}: uninstall successfully.")
                return
            if 'resource mapping not found' in err and 'ensure CRDs are installed first' in err:
                logger.info(f"{' '.join(cmd)}: CRD not found.")
                return
            if 'NotFound' in err:
                logger.info(f"{' '.join(cmd)}: resources not found.")
                return
            raise KubectlError(cmd, out, err)

class Helm(Command):
    client = pyhelm3.Client()
    charts = {}

    @classmethod
    def get_chart(cls, chart):
        async def _get_chart(chart):
            return await Helm.client.get_chart(chart["name"], repo=chart["repo"], version=chart["version"])
        if chart['name'] not in Helm.charts:
            Helm.charts[chart['name']] = asyncio.run(_get_chart(chart))
            logger.debug(f"Chart {chart['name']} retrieved.")

    def get_current_revision(self, release_name, namespace):
        async def _get_current_revision(release_name, namespace):
            return await Helm.client.get_current_revision(release_name, namespace=namespace)
        try:
            revision = asyncio.run(_get_current_revision(release_name, namespace))
        except pyhelm3.ReleaseNotFoundError:
            logger.debug(f"Release {release_name} not Found.")
            return None
        logger.debug(f"Current revision of {release_name}: {revision.revision}")
        return revision

    def should_install_or_upgrade(self, release, chart):
        async def _should_install_or_upgrade(revision, chart, values):
            logger.debug(f"Check Whether Release {revision.release.name} needs to upgrade.")
            return await Helm.client.should_install_or_upgrade_release(revision, chart, values)
        async def _should_install_or_upgrade_oci(revision, chart, values):
            if revision.status != pyhelm3.ReleaseRevisionStatus.DEPLOYED:
                logger.info(f"The Status of Release {release['name']}: {revision.status}")
                return True
            revision_chart = await revision.chart_metadata()
            if revision_chart.name != chart["oci"].split('/')[-1]:
                logger.info(f"Old Chart: {revision_chart.name}, New Chart: {chart['oci']}")
                return True
            if revision_chart.version != chart["version"]:
                logger.info(f"Old Version: {revision_chart.version}, New Version: {chart['version']}")
                return True
            revision_values = await revision.values()
            if revision_values != values:
                logger.debug(f"Old Values:\n{revision_values}")
                logger.debug(f"New Values:\n{values}")
                logger.info("Values Changed")
                return True
            return False
        values = {}
        if "valuesFile" in release:
            with open(release["valuesFile"]) as fo:
                values = yaml.safe_load(fo)
        if "additionalValues" in release:
            for adv in release['additionalValues']:
                keys = adv['name'].split('.')
                temp = values
                for key in keys[:-1]:
                    temp = temp[key]
                temp[keys[-1]] = adv["value"]
        if 'oci' in chart:
            need = asyncio.run(_should_install_or_upgrade_oci(release['currentRevision'], chart, values))
        elif 'folder' in chart:
            need = True
        else:
            Helm.get_chart(chart)
            need = asyncio.run(_should_install_or_upgrade(release['currentRevision'], Helm.charts[chart['name']], values))
        if need:
            logger.debug(f"Release {release['name']} needs to upgrade.")
        else:
            logger.debug(f"Release {release['name']} is up to date.")
        return need

    def install_or_upgrade(self, release, chart):
        async def _install_or_upgrade(release_name, chart, values, namespace, timeout):
            logger.debug(f"Start to install/upgrade {release['name']}")
            return await Helm.client.install_or_upgrade_release(release_name, chart, values, namespace=namespace, create_namespace = True, atomic = True, wait = True, timeout = timeout)
        values = {}
        if "valuesFile" in release:
            with open(release["valuesFile"]) as fo:
                values = yaml.safe_load(fo)
        if "additionalValues" in release:
            for adv in release['additionalValues']:
                keys = adv['name'].split('.')
                temp = values
                for key in keys[:-1]:
                    temp = temp[key]
                temp[keys[-1]] = adv["value"]
            with open(release["valuesFile"], 'w') as fo:
                yaml.dump(values, fo, default_flow_style=False, sort_keys=False, indent=2)
        if "oci" in chart:
            cmd = ["helm", "upgrade", "--install", release['name'], chart['oci'], '--version', chart['version'], '--values', release['valuesFile'], "--namespace", release['namespace'], '--wait', '--timeout', "5m"]
            self.run(cmd, exceptionOnFail = True)
            logger.info(f"Successfully install/upgrade Release {release['name']} of Chart {chart['oci']}.")
        elif "folder" in chart:
            cmd = ["helm", "upgrade", "--install", release['name'], chart['folder'], '--values', release['valuesFile'], "--namespace", release['namespace'], '--wait', '--timeout', "5m"]
            self.run(cmd, exceptionOnFail = True)
            logger.info(f"Successfully install/upgrade Release {release['name']} of Chart {chart['folder']}.")
        else:
            Helm.get_chart(chart)
            revision = asyncio.run(_install_or_upgrade(release["name"], Helm.charts[chart['name']], values, release["namespace"], "5m"))
            logger.info(f"Successfully install/upgrade Release {release['name']} of Chart {chart['name']}.")
            logger.info(f"Revision of Release {release['name']} in namespace {release['namespace']}: {revision.revision}.")

    def uninstall(self, release):
        async def _uninstall(release_name, namespace):
            await Helm.client.uninstall_release(release_name, namespace=namespace, wait = True)
        asyncio.run(_uninstall(release["name"], release["namespace"]))

command = Command()
helm = Helm()
kubectl = Kubectl()
