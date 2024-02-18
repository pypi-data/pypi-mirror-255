import os, re, glob, yaml, logging, multiprocessing

logger = logging.getLogger(__name__)

class Manifest:
    def __init__(self, workdir, rundir, settings):
        self.workdir = workdir
        self.resources_file = os.path.join(workdir, 'resources.yaml')
        self.config_file = os.path.join(workdir, 'config.yaml')
        self.yaml_folder = os.path.join(workdir, 'yaml')
        self.values_folder = os.path.join(workdir, 'values')
        self.secret_folder = os.path.join(workdir, 'secret')
        self.rundir = rundir
        self.effective_resources_file = os.path.join(rundir, 'resources.yaml')
        self.effective_yaml_folder = os.path.join(rundir, 'yaml')
        self.effective_values_folder = os.path.join(rundir, 'values')
        self.effective_secret_folder = os.path.join(rundir, 'secret')
        self.resources = None
        self.settings = {k: v for k,v in settings} if settings else {}

    def apply_config_yaml(self):
        def replace_placeholders(line, config):
            unmatched = set()
            matches = re.findall(r'__CONFIG__\.([\w\.]+)', line)
            for match in matches:
                keys = match.split('.')
                replacement_value = config
                for key in keys:
                    if key not in replacement_value:
                        replacement_value = None
                        unmatched.add(match)
                        break
                    replacement_value = replacement_value[key]
                if replacement_value is not None:
                    line = line.replace(f'__CONFIG__.{match}', str(replacement_value))
            return line, unmatched
        with open(self.config_file) as fo:
            config = yaml.safe_load(fo)
        yaml_files = os.path.join(self.yaml_folder, '*.yaml')
        values_files = os.path.join(self.values_folder, '*.yaml')
        source_file_list = glob.glob(yaml_files) + glob.glob(values_files) + glob.glob(self.resources_file)
        os.makedirs(os.path.join(self.rundir, 'yaml'), exist_ok = True)
        os.makedirs(os.path.join(self.rundir, 'values'), exist_ok = True)
        unmatched = set()
        for source_file in source_file_list:
            target_file = source_file.replace(self.workdir, self.rundir)
            with open(source_file) as fhr, open(target_file, 'w') as fhw:
                for line in fhr:
                    rendered_line, _unmatched = replace_placeholders(line, config)
                    unmatched |= _unmatched
                    fhw.write(rendered_line)
        return unmatched

    def apply_settings(self):
        unknown_settings = set()
        for k, v in self.settings.items():
            keys = k.split('.')
            _resources = self.resources
            for key in keys[:-1]:
                if key not in _resources:
                    unknown_settings.add(k)
                    _resources = None
                    break
                _resources = _resources[key]
            if _resources is not None:
                if keys[-1] not in _resources:
                    unknown_settings.add(k)
                else:
                    _resources[keys[-1]] = v
        return unknown_settings

    def validate_dependencies(self):
        for r in self.resources:
            for d in self.resources[r].get("dependsOn", []):
                if d not in self.resources:
                    logger.error(f"Non-existing resource '{d}' existing in depdends of {r}")
                    return False
        return True

    def set_effective_path(self):
        for r in self.resources:
            if self.resources[r]['type'] == 'yaml':
                yamlFiles = self.resources[r]['yamlFiles']
                self.resources[r]['yamlFiles'] = []
                for f in yamlFiles:
                    self.resources[r]['yamlFiles'].append(os.path.join(self.effective_yaml_folder, f))
            elif self.resources[r]['type'] == 'chart':
                self.resources[r]['release']['valuesFile'] = os.path.join(self.effective_values_folder, self.resources[r]['release']['valuesFile'])
            elif self.resources[r]['type'] == 'secret':
                if 'file' in self.resources[r]['secret']:
                    self.resources[r]['secret']['file'] = os.path.join(self.secret_folder, self.resources[r]['secret']['file'])
                self.resources[r]['yamlFolder'] = self.effective_secret_folder

    def initialise(self):
        if not os.path.isfile(self.resources_file):
            logger.error(f"resources.yaml not existing in {self.workdir}, exit.")
            return False
        if not os.path.isfile(self.config_file):
            logger.error(f"config.yaml not existing in {self.workdir}, exit.")
            return False
        if not os.path.isdir(self.yaml_folder):
            logger.error(f"yaml folder not existing in {self.workdir}, exit.")
            return False
        if not os.path.isdir(self.values_folder):
            logger.error(f"values folder not existing in {self.workdir}, exit.")
            return False

        missing = self.apply_config_yaml()
        if missing:
            for m in missing:
                logger.error(f"Missing config: {m}")
            return False

        with open(self.effective_resources_file) as fo:
            self.resources = yaml.safe_load(fo)

        if not self.validate_dependencies():
            return False

        self.set_effective_path()

        unknown_settings = self.apply_settings()
        if unknown_settings:
            for s in unknown_settings:
                logger.error(f"Unknown setting: {s}")
            return False

        return True

    def print_graph(self):
        logger.info("To generate Dependency Graph, graphviz and graphviz python package is required.")
        from graphviz import Digraph
        dot = Digraph(comment = 'The Dependency Graph')
        for r in self.resources:
            dot.node(r, r)
            for dep in self.resources[r].get("dependsOn", []):
                dot.edge(dep, r)
        folder_path = os.path.join(self.rundir, "graph")
        os.makedirs(folder_path, exist_ok = True)
        file_path = os.path.join(folder_path, "resources")
        dot.render(file_path, format = 'pdf', view = False)
        logger.info(f"{file_path}.pdf generated.")

    def reverse_dependencies(self):
        deps = {}
        for r in self.resources:
            if "dependsOn" in self.resources[r]:
                deps[r] = self.resources[r]["dependsOn"]
                del self.resources[r]["dependsOn"]
        for r in deps:
            for d in deps[r]:
                if "dependsOn" not in self.resources[d]:
                    self.resources[d]["dependsOn"] = []
                self.resources[d]["dependsOn"].append(r)

    def set_targets(self, targets):
        if 'all' in targets:
            return True
        unknown = [target for target in targets if target not in self.resources]
        if unknown:
            logger.error(f"Unknown resource: {unknown}")
            return False
        def reduce(chosen):
            _resources = {}
            def add_with_dependencies(key):
                if key not in _resources:
                    _resources[key] = self.resources[key]
                    for dep in _resources[key].get('dependsOn', []):
                        add_with_dependencies(dep)
            for key in chosen:
                add_with_dependencies(key)
            logger.debug(f"Targeting Resources: {list(_resources.keys())}")
            return _resources
        self.resources = self.reduce(targets)

    def generate_shared_resources(self):
        if not hasattr(self, "shared_resources"):
            def shareable(d, m):
                sd = m.dict()
                for k, v in d.items():
                    if isinstance(v, dict):
                        sd[k] = shareable(v, m)
                    else:
                        sd[k] = v
                return sd
            manager = multiprocessing.Manager()
            self.shared_resources = shareable(self.resources, manager)
        return self.shared_resources
