# pyright: reportMissingImports=false
# pylint: disable=import-error, bare-except
import os, sys
import yaml
from typing import Optional

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy
from conan.tools.env import VirtualBuildEnv
from conans.client.loader_txt import ConanFileTextLoader


toolchain_available:bool = False
sys.path.insert(0, os.path.dirname(__file__))

try:
    from zetsubou.conan import from_conan
    from zetsubou.conan import deployer
    toolchain_available = True
except Exception as ex:
    print(f"Failed to import 'from_conan' {ex}")
try:
    import from_conan
    import deployer
    toolchain_available = True
except Exception as ex:
    print(f"Failed to import 'from_conan' {ex}")


# ZetsubouToolchain
# Provides methods to extract dependency information from project.yml
# Can generate the project files and build it
class _toolchain(object):
    project_file: str
    conanfile: ConanFile
    platform_file = None

    _project_template = None
    _conan_dependencies = None

    def _load_project_template(self, project_yml:str):
        if not os.path.exists(project_yml):
            raise ConanException(f"Project file '{project_yml}' not found! Ensure that it is added to both 'export' and 'export_sources' in conan recipe!")
        if self._project_template is None:
            with open(project_yml, mode='r') as in_proj:
                self._project_template = yaml.load(in_proj, yaml.SafeLoader)
        return self._project_template

    def _load_conan_ini(self, conan_ini:Optional[str], project_yml:str):
        if conan_ini is None:
            return None

        conan_ini = os.path.join(os.path.dirname(project_yml), conan_ini)

        if not os.path.exists(conan_ini) or not os.path.isfile(conan_ini):
            raise ConanException(f"Dependency file '{conan_ini}' not found! Ensure that it is added to both 'export' and 'export_sources' in conan recipe!")

        with open(conan_ini, mode='r') as in_ini:
            conan_ini_content = in_ini.read()
            print(f"Loaded: {os.path.abspath(conan_ini)}")
            return ConanFileTextLoader(conan_ini_content)

    def _load_conan_dependencies(self, project_yml:str):
        if self._conan_dependencies is None:
            proj = self._load_project_template(project_yml)
            if proj is None:
                return None

            conan_data = proj.get('conan', None)
            if conan_data is None:
                return None

            tools_req_file = conan_data.get('build_tools', None)
            req_file = conan_data.get('dependencies', None)

            result = {}

            tools_ini = self._load_conan_ini(tools_req_file, project_yml)
            if tools_ini is not None:
                result['tool_requirements'] = tools_ini.tool_requirements

            main_ini = self._load_conan_ini(req_file, project_yml)
            if main_ini is not None:
                result['requirements'] = main_ini.requirements

            self._conan_dependencies = result
        return self._conan_dependencies

    def fill_requirements(self, conanfile:ConanFile, project_yml:str):
        deps = self._load_conan_dependencies(project_yml)
        if deps is None:
            return
        for entry in deps.get('requirements', []):
            if not any(filter(lambda r : r.ref.matches(entry, is_consumer=False), conanfile.requires.values())):
                conanfile.requires(entry)

    def fill_tool_requirements(self, conanfile:ConanFile, project_yml:str):
        deps = self._load_conan_dependencies(project_yml)
        if deps is None:
            return
        for entry in deps.get('tool_requirements', []):
            if not any(filter(lambda r : r.ref.matches(entry, is_consumer=False), conanfile.requires.values())):
                conanfile.requires.tool_require(entry)

    def profile_filename(self, dir:str):
        return os.path.join(dir, 'conan_profile.yml')

    def init(self, conanfile:ConanFile, project_file:str="project.yml"):
        self.conanfile = conanfile
        self.project_file = project_file

    def configure(self):
        if not self.conanfile:
            raise ValueError('Zetsubou not initialized! call self.zetsubou.init(self) before using!')

        if toolchain_available:
            profile_file = self.profile_filename(self.conanfile.folders.generators_folder)
            if not from_conan.export_profile(self.conanfile, profile_file):
                raise ConanException('Unable to generate profile file!')

            # Previously, we were calling zetsubou config, but we shouldn't call install from within conan
            # Instead we generate virtual env here
            venv = VirtualBuildEnv(self.conanfile)
            venv.generate()

            # And generate .yml files for conan dependencies here
            deployer.generate(self.conanfile)

            # And consume it by just generating the project files
            self.conanfile.run(f'zetsubou gen {self.project_file} --profile={profile_file} --nologo --ide')
        else:
            raise ConanException('Unable to start Zetsubou, failed imports!')

    def build(self):
        if not self.conanfile:
            raise ValueError('Zetsubou not initialized! call self.zetsubou.init(self) before using!')

        if not toolchain_available:
            raise ConanException('Unable to start Zetsubou, failed imports!')

        profile_file = self.profile_filename(self.conanfile.folders.generators_folder)
        if not os.path.exists(profile_file) or not os.path.isfile(profile_file):
            raise ConanException(f"Unable to find '{profile_file}' profile file! Did you forget to run install first?")

        self.conanfile.run(f'zetsubou build {self.project_file} --profile={profile_file} --nologo --ide')

# Conanfiles using Zetsubout should use this class as a base
# It's purpose is to read project.yml file and inject dependencies 
# Into conanfile, without a need to setup it in two places
class ZetsubouBase(object):
    _zetsubou: _toolchain = _toolchain()
    _project_yml: str = ''

    @property
    def zetsubou(self):
        if self._zetsubou is None:
            print("Zetsubou not initialized!")
        return self._zetsubou

    # This is unfortunately a hack
    # We store dependency data outside conanfile.py and need to read and setup them here
    # What makes life harder is a fact that folder paths are being setuped after dependency graph
    # So we need to guess where hardcoded project.yml is based on recipe path
    # Additionaly, project.yml and dependency.ini files must be added to export and export_sources of the recipe
    # Such files are not downloaded because source is called after requirements()
    @property
    def default_project(self):
        if self._project_yml == '':
            from_recipe_folder = os.path.join(self.recipe_folder, 'project.yml')

            if os.path.exists(from_recipe_folder) and os.path.isfile(from_recipe_folder):
                self._project_yml = from_recipe_folder
                print(f"From recipe folder: {from_recipe_folder}")

            elif self.recipe_folder.endswith('e'):
                from_export = os.path.normpath(os.path.join(self.recipe_folder, '..', 'es', 'project.yml'))
                if os.path.exists(from_export) and os.path.isfile(from_export):
                    self._project_yml = from_export
                    print(f"From export folder: {from_export}")

        return self._project_yml

    def requirements(self):
        self.zetsubou.fill_requirements(self, self.default_project)

    def build_requirements(self):
        self.zetsubou.fill_tool_requirements(self, self.default_project)


class ZetsubouGeneratorPackage(ConanFile):
    name = "zetsubougen"
    version = "0.8.0"
    license = "MIT"
    description = 'Zetsubou yml files generator'
    url = "https://github.com/BentouDev/Zetsubou"
    package_type = "python-require"

    # Must be placed at the root of the source
    # Conan no longer allows referencing parent directory in relative paths
    def export(self):
        exports = [
            "conanfile.py",
            "conan/from_conan.py",
            "conan/deployer.py",
            "project/model/toolchain_profile.py",
            "project/model/platform_enums.py",
            "project/model/configuration_enums.py",
            "project/model/toolchain_enums.py",
            "project/model/runtime_library.py",
            "project/model/kind.py",
            "utils/yaml_simple_writer.py",
        ]

        for e in exports:
            copy(self, e, self.recipe_folder, self.export_folder, keep_path=False)
