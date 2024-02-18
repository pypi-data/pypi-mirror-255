"""Python Package File Generator"""


# Standard libraries
from typing import Literal
import re
import textwrap

# Non-standard libraries
import pyserials
from actionman.logger import Logger

from repodynamics.path import PathManager
from repodynamics.datatype import DynamicFile
from repodynamics.control.content import ControlCenterContentManager
from repodynamics import file_io


class PythonPackageFileGenerator:
    def __init__(
        self,
        content_manager: ControlCenterContentManager,
        path_manager: PathManager,
        logger: Logger,
    ):
        self._ccm = content_manager
        self._ccs = content_manager.settings
        self._pathman = path_manager
        self._logger = logger

        self._package_dir_output: tuple[DynamicFile, str] | None = None
        self._test_package_dir_output: tuple[DynamicFile, str] | None = None
        return

    def generate(self) -> list[tuple[DynamicFile, str]]:
        self._package_dir_output, self._test_package_dir_output = self._directories()
        return (
            self.requirements()
            + self.init_docstring()
            + self.pyproject()
            + self.pyproject_tests()
            + [self._package_dir_output, self._test_package_dir_output]
            + self.python_files()
            + self.typing_marker()
            + self.manifest()
        )

    def typing_marker(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package PEP 561 Typing Marker")
        file_info = self._pathman.package_typing_marker(package_name=self._ccm["package"]["import_name"])
        file_content = (
            "# PEP 561 marker file. See https://peps.python.org/pep-0561/\n"
            if self._ccm["package"].get("typed")
            else ""
        )
        self._logger.info(message="File info:", code=str(file_info))
        self._logger.debug(message="File content:", code=file_content)
        self._logger.section_end()
        return [(file_info, file_content)]

    def requirements(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package Requirements File")
        file_info = self._pathman.package_requirements
        file_content = ""
        if self._ccm["package"].get("core_dependencies"):
            for dep in self._ccm["package"]["core_dependencies"]:
                file_content += f"{dep['pip_spec']}\n"
        if self._ccm["package"].get("optional_dependencies"):
            for dep_group in self._ccm["package"]["optional_dependencies"]:
                for dep in dep_group["packages"]:
                    file_content += f"{dep['pip_spec']}\n"
        self._logger.info(message="File info:", code=str(file_info))
        self._logger.debug(message="File content:", code=file_content)
        self._logger.section_end()
        return [(file_info, file_content)]

    def _directories(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package and Test-Suite Directories")
        out = []
        for title, name, sub_path, func in (
            (
                "Package",
                self._ccm["package"]["import_name"],
                self._ccm["path"]["dir"]["source"],
                self._pathman.package_dir
            ),
            (
                "Test-Suite",
                self._ccm["package"]["testsuite_import_name"],
                f'{self._ccm["path"]["dir"]["tests"]}/src',
                self._pathman.package_tests_dir
            ),
        ):
            self._logger.section(title)
            rel_path = f"{sub_path}/{name}"
            path = self._pathman.root / rel_path
            if path.exists():
                self._logger.info(title=f"Path exists", message=path)
                file_info = func(path, path)
                out.append((file_info, ""))
                self._logger.info(message="File info:", code=str(file_info))
                continue
            self._logger.info(f"Path '{rel_path}' does not exist; looking for package directory.")
            package_dirs = (
                [
                    subdir
                    for subdir in [content for content in path.parent.iterdir() if content.is_dir()]
                    if "__init__.py"
                    in [sub_content.name for sub_content in subdir.iterdir() if sub_content.is_file()]
                ]
                if path.parent.is_dir()
                else []
            )
            count_dirs = len(package_dirs)
            if count_dirs > 1:
                self._logger.critical(
                    title=f"More than one package directory found in '{path}'",
                    message="\n".join([str(package_dir) for package_dir in package_dirs]),
                )
            if count_dirs == 1:
                self._logger.info(
                    title=f"Rename package directory to '{name}'",
                    message=f"Old Path: '{package_dirs[0]}', New Path: '{path}'",
                )
                file_info = func(name, old_path=package_dirs[0], new_path=path)
                out.append((file_info, ""))
                self._logger.info(message="File info:", code=str(file_info))
                continue
            self._logger.info(title="No package directory found", message=f"create directory '{path}'.")
            file_info = func(old_path=None, new_path=path)
            out.append((file_info, ""))
            self._logger.info(message="File info:", code=str(file_info))
            self._logger.section_end()
        self._logger.section_end()
        return out

    def python_files(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package and Test-Suite Source Files")
        out = []
        mapping = {}
        package_dir = self._package_dir_output[0]
        test_package_dir = self._test_package_dir_output[0]
        for dir_ in (package_dir, test_package_dir):
            if dir_.alt_paths and dir_.alt_paths[0] != dir_.path:
                mapping[dir_.alt_paths[0].name] = dir_.path.name
        if mapping:
            for filepath in self._pathman.root.glob("**/*.py"):
                self._logger.section(f"File '{filepath.relative_to(self._pathman.root)}'")
                if package_dir.alt_paths and filepath.is_relative_to(package_dir.alt_paths[0]):
                    new_path = package_dir.path / filepath.relative_to(package_dir.alt_paths[0])
                elif test_package_dir.alt_paths and filepath.is_relative_to(test_package_dir.alt_paths[0]):
                    new_path = test_package_dir.path / filepath.relative_to(test_package_dir.alt_paths[0])
                else:
                    new_path = filepath
                file_info = self._pathman.python_file(new_path)
                file_content = self.rename_imports(module_content=filepath.read_text(), mapping=mapping)
                out.append((file_info, file_content))
                self._logger.info(message="File info:", code=str(file_info))
                self._logger.debug(message="File content:", code=file_content)
                self._logger.section_end()
        if not test_package_dir.alt_paths:
            # test-suite package must be created
            for testsuite_filename in ["__init__.txt", "__main__.txt", "general_tests.txt"]:
                self._logger.section(f"Test-Suite File '{testsuite_filename}'")
                filepath = file_io.get_package_datafile(
                    f"template/testsuite/{testsuite_filename}", return_content=False
                )
                file_info = self._pathman.python_file(
                    (test_package_dir.path / testsuite_filename).with_suffix(".py")
                )
                file_content = pyserials.update.templated_data_from_source(
                    templated_data=filepath.read_text(), source_data=self._ccm.as_dict
                )
                out.append((file_info, file_content))
                self._logger.info(message="File info:", code=str(file_info))
                self._logger.debug(message="File content:", code=file_content)
                self._logger.section_end()
        self._logger.section_end()
        return out

    # def _package_dir(self, tests: bool = False) -> list[tuple[DynamicFile, str]]:
    #     self._logger.h4("Update path: package")
    #     package_name = self._meta["package"]["name"]
    #     name = package_name if not tests else f"{package_name}_tests"
    #     sub_path = (
    #         self._meta["path"]["dir"]["source"] if not tests else f'{self._meta["path"]["dir"]["tests"]}/src'
    #     )
    #     path = self._out_db.root / sub_path / name
    #     func = self._out_db.package_tests_dir if tests else self._out_db.package_dir
    #     if path.exists():
    #         self._logger.skip(f"Package path exists", f"{path}")
    #         out = [(func(name, path, path), "")]
    #         return out
    #     self._logger.info(f"Package path '{path}' does not exist; looking for package directory.")
    #     package_dirs = (
    #         [
    #             subdir
    #             for subdir in [content for content in path.parent.iterdir() if content.is_dir()]
    #             if "__init__.py"
    #             in [sub_content.name for sub_content in subdir.iterdir() if sub_content.is_file()]
    #         ]
    #         if path.parent.is_dir()
    #         else []
    #     )
    #     count_dirs = len(package_dirs)
    #     if count_dirs > 1:
    #         self._logger.error(
    #             f"More than one package directory found in '{path}'",
    #             "\n".join([str(package_dir) for package_dir in package_dirs]),
    #         )
    #     if count_dirs == 1:
    #         self._logger.success(
    #             f"Rename package directory to '{name}'",
    #             f"Old Path: '{package_dirs[0]}'\nNew Path: '{path}'",
    #         )
    #         out = [(func(package_name, old_path=package_dirs[0], new_path=path), "")]
    #         package_old_name = package_dirs[0].name
    #         for filepath in (self._out_db.root.glob("**/*.py") if not tests else path.glob("**/*.py")):
    #             new_content = self.rename_imports(
    #                 module_content=filepath.read_text(), old_name=package_old_name, new_name=name
    #             )
    #             out.append((self._out_db.python_file(filepath), new_content))
    #         return out
    #     self._logger.success(f"No package directory found in '{path}'; creating one.")
    #     out = [(func(name, old_path=None, new_path=path), "")]
    #     if tests:
    #         for testsuite_filename in ["__init__.txt", "__main__.txt", "general_tests.txt"]:
    #             filepath = _util.file.datafile(f"template/testsuite/{testsuite_filename}")
    #             text = _util.dict.fill_template(filepath.read_text(), metadata=self._meta.as_dict)
    #             out.append((self._out_db.python_file((path / testsuite_filename).with_suffix(".py")), text))
    #     return out

    def init_docstring(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package __init__.py File")
        docs_config = self._ccm["package"].get("docs", {})
        if "main_init" not in docs_config:
            self._logger.info("No docstring set in package.docs.main_init; skipping.")
            self._logger.section_end()
            return []
        file_info = self._pathman.package_init(self._ccm["package"]["import_name"])
        docstring_text = textwrap.fill(
            docs_config["main_init"].strip(),
            width=self._ccm["package"].get("dev_config", {}).get("max_line_length", 100),
            replace_whitespace=False,
        )
        docstring = f'"""{docstring_text}\n"""  # noqa: D400\n'

        package_dir_info = self._package_dir_output[0]
        current_dir_path = (
            package_dir_info.alt_paths[0] if package_dir_info.alt_paths else package_dir_info.path
        )
        filepath = current_dir_path / "__init__.py"
        if filepath.is_file():
            with open(filepath, "r") as f:
                file_content = f.read().strip()
        else:
            file_content = """__version_details__ = {"version": "0.0.0"}
__version__ = __version_details__["version"]"""
        pattern = re.compile(
            r'^((?:[\t ]*#.*\n|[\t ]*\n)*)("""(?:.|\n)*?"""(?:[ \t]*#.*)?(?:\n|$))', re.MULTILINE
        )
        match = pattern.match(file_content)
        if not match:
            # If no docstring found, add the new docstring at the beginning of the file
            file_content = f"{docstring}\n\n{file_content}".strip() + "\n"
        else:
            # Replace the existing docstring with the new one
            file_content = re.sub(pattern, rf"\1{docstring}", file_content)
        self._logger.info(message="File info:", code=str(file_info))
        self._logger.debug(message="File content:", code=file_content)
        self._logger.section_end()
        return [(file_info, file_content)]

    def manifest(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package Manifest File")
        file_info = self._pathman.package_manifest
        file_content = "\n".join(self._ccm["package"].get("manifest", []))
        self._logger.info(message="File info:", code=str(file_info))
        self._logger.debug(message="File content:", code=file_content)
        self._logger.section_end()
        return [(file_info, file_content)]

    def pyproject(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Package pyproject.toml File")
        file_info = self._pathman.package_pyproject
        pyproject = self._ccm["package"]["pyproject"]
        project = pyproject.setdefault("project", {})
        for key, val in self.pyproject_project().items():
            if key not in project:
                project[key] = val
        file_content = pyserials.write.to_toml_string(data=pyproject, sort_keys=True)
        self._logger.info(message="File info:", code=str(file_info))
        self._logger.debug(message="File content:", code=file_content)
        self._logger.section_end()
        return [(file_info, file_content)]

    def pyproject_tests(self) -> list[tuple[DynamicFile, str]]:
        self._logger.section("Test Suite pyproject.toml File")
        file_info = self._pathman.test_package_pyproject
        file_content = pyserials.write.to_toml_string(
            data=self._ccm["package"]["pyproject_tests"], sort_keys=True
        )
        self._logger.info(message="File info:", code=str(file_info))
        self._logger.debug(message="File content:", code=file_content)
        self._logger.section_end()
        return [(file_info, file_content)]

    def pyproject_project(self) -> dict:
        data_type = {
            "name": ("str", self._ccm["package"]["name"]),
            "dynamic": ("array", ["version"]),
            "description": ("str", self._ccs.project.intro.tagline),
            "readme": ("str", self._pathman.readme_pypi.rel_path),
            "requires-python": ("str", f">= {self._ccm['package']['python_version_min']}"),
            "license": (
                "inline_table",
                {"file": self._pathman.license.rel_path} if self._ccm["license"] else None,
            ),
            "authors": ("array_of_inline_tables", self.pyproject_project_authors),
            "maintainers": ("array_of_inline_tables", self.pyproject_project_maintainers),
            "keywords": ("array", self._ccs.project.intro.keywords),
            "classifiers": ("array", self._ccm["package"].get("trove_classifiers")),
            "urls": ("table", self._ccm["package"].get("urls")),
            "scripts": ("table", self.pyproject_project_scripts),
            "gui-scripts": ("table", self.pyproject_project_gui_scripts),
            "entry-points": ("table_of_tables", self.pyproject_project_entry_points),
            "dependencies": ("array", self.pyproject_project_dependencies),
            "optional-dependencies": ("table_of_arrays", self.pyproject_project_optional_dependencies),
        }
        project = {}
        for key, (dtype, val) in data_type.items():
            if val:
                project[key] = pyserials.format.to_toml_object(data=val, toml_type=dtype)
        return project

    @property
    def pyproject_project_authors(self):
        return self._get_authors_maintainers(role="authors")

    @property
    def pyproject_project_maintainers(self):
        return self._get_authors_maintainers(role="maintainers")

    @property
    def pyproject_project_dependencies(self):
        if not self._ccm["package"].get("core_dependencies"):
            return
        return [dep["pip_spec"] for dep in self._ccm["package"]["core_dependencies"]]

    @property
    def pyproject_project_optional_dependencies(self):
        return (
            {
                dep_group["name"]: [dep["pip_spec"] for dep in dep_group["packages"]]
                for dep_group in self._ccm["package"]["optional_dependencies"]
            }
            if self._ccm["package"].get("optional_dependencies")
            else None
        )

    @property
    def pyproject_project_scripts(self):
        return self._scripts(gui=False)

    @property
    def pyproject_project_gui_scripts(self):
        return self._scripts(gui=True)

    @property
    def pyproject_project_entry_points(self):
        return (
            {
                entry_group["group_name"]: {
                    entry_point["name"]: entry_point["ref"] for entry_point in entry_group["entry_points"]
                }
                for entry_group in self._ccm["package"]["entry_points"]
            }
            if self._ccm["package"].get("entry_points")
            else None
        )

    def _get_authors_maintainers(self, role: Literal["authors", "maintainers"]):
        """
        Update the project authors in the pyproject.toml file.

        References
        ----------
        https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#authors-maintainers
        """
        people = []
        target_people = (
            self._ccm["maintainer"].get("list", [])
            if role == "maintainers"
            else self._ccm["author"]["entries"]
        )
        for person in target_people:
            if not person["name"]:
                self._logger.warning(
                    f'One of {role} with username \'{person["username"]}\' '
                    f"has no name set in their GitHub account. They will be dropped from the list of {role}."
                )
                continue
            user = {"name": person["name"]}
            email = person.get("email")
            if email:
                user["email"] = email
            people.append(user)
        return people

    def _scripts(self, gui: bool):
        cat = "gui_scripts" if gui else "scripts"
        return (
            {script["name"]: script["ref"] for script in self._ccm["package"][cat]}
            if self._ccm["package"].get(cat)
            else None
        )

    @staticmethod
    def rename_imports(module_content: str, mapping: dict[str, str]) -> str:
        """
        Rename the old import name to the new import name in the provided module content.

        Parameters
        ----------
        module_content : str
            The content of the Python module as a string.
        mapping : dict[str, str]
            A dictionary mapping the old import names to the new import names.

        Returns
        -------
        new_module_content : str
            The updated module content as a string with the old names replaced by the new names.
        """
        updated_module_content = module_content
        for old_name, new_name in mapping.items():
            # Regular expression patterns to match the old name in import statements
            patterns = [
                rf"^\s*from\s+{re.escape(old_name)}(?:.[a-zA-Z0-9_]+)*\s+import",
                rf"^\s*import\s+{re.escape(old_name)}(?:.[a-zA-Z0-9_]+)*",
            ]
            for pattern in patterns:
                # Compile the pattern into a regular expression object
                regex = re.compile(pattern, flags=re.MULTILINE)
                # Replace the old name with the new name wherever it matches
                updated_module_content = regex.sub(
                    lambda match: match.group(0).replace(old_name, new_name, 1), updated_module_content
                )
        return updated_module_content
