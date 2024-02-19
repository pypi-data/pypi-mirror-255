#!/usr/bin/env python

import os
import logging


########################################################################################################################


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def get_release_version(title):
    """try to get a valid Semantic Versioning from last part of the Release-Please pull request title"""
    if not title:
        return
    version = str(title).split()[-1].strip(".").strip("v")
    for i in version.split("."):
        try:
            int(i)
        except:
            return
    return version


class GeneratePyproject(object):
    """
    Generates the needed pyproject.toml files for setuptools
    https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
    in order to build the package, which then may be distributed to
    pypi.org using twine.

    ...

    Attributes
    ----------
    project_dir : str
        path to the directory which contains the project
    version : str
        the version the package will have
    toml_filename : str
        prefix to the project name (default pyproject.toml)
    project_name : str
        name of the project (on pypi.org)
    src_dir : str
        full path to the 'src' dir within project_dir
    src_items : list
        a list of all the items in the 'src' dir
    code_dir_name : str
        name of dir within the 'src' dir which contains the python code and __init__.py file
    init_file : str
        full path to the __init__.py file within the code dir of 'src'
    license_file : str
        the licence file within the 'src' dir
    readme_file : str
        the readme file within the 'src' dir
    requirements_file : str
        the 'requirements.txt' file within the 'src' dir
    description : str
        the content of the __description__ attribute in the __init__.py file

    Methods
    -------
    verify_project()
        Check if the project dir exists and contains a 'src' dir.
        Creates a list of all the items in the 'src' dir.
        Then calls the set_ methods:
            set_requirements_file()
            set_readme_file()
            set_license_file()
            set_init_file()
            set_description()
    set_requirements_file()
        Set requirements_file attribute to requirements.txt (if found in 'src' dir)
    set_readme_file()
        Set readme_file attribute to the filename of the readme file within the project dir.
        The file must start with 'readme.' (case-insensitive).
    set_license_file()
        Set license_file attribute to the filename of the license file within the project dir.
        The file must start with 'license' (case-insensitive).
    set_init_file()
        Set init_file attribute.
        Set code_dir_name attribute.
    set_description()
        Set description attribute
    write_config_files()
        Calls the set_ methods and then the write_ methods
    write_setup_file()
        Writes the 'setup.py' file to the 'src' dir.
    write_toml_file()
        Writes the 'pyproject.toml' file to the 'src' dir.
    """

    def __init__(self,
                 project_name,
                 version,
                 project_dir=".",
                 toml_filename="pyproject.toml"):
        self.project_name = project_name
        self.version = version
        self.project_dir = project_dir
        self.toml_filename = toml_filename

        self.src_dir = ""
        self.src_items = []
        self.project_dir_items = []
        self.code_dir_name = ""
        self.init_file = ""
        self.license_file = ""
        self.readme_file = ""
        self.requirements_file = ""
        self.description = ""

    def verify_project(self):
        """check if the project dir contains the necessary 'src' dir and code files

        If the project dir exists and that it contains a 'src' dir.
        Creates a list of all the items in the 'src' dir.

        """

        if not os.path.isdir(self.project_dir):
            logging.error(f"'{self.project_dir}' directory does not exists.")
            return

        src_dir = os.path.join(self.project_dir, "src")
        if not os.path.isdir(src_dir):
            logging.error(f"'src' dir does not exists in '{self.project_dir}' directory.")
            return

        self.src_items = os.listdir(src_dir)                   # items in the 'src' dir
        self.project_dir_items = os.listdir(self.project_dir)  # items in the project dir
        self.src_dir = src_dir                                 # the 'src' dir including path

        return True

    def set_requirements_file(self):
        """try to set requirements_file attribute to requirements.txt """
        if "requirements.txt" in self.src_items:
            self.requirements_file = "requirements.txt"
            return

        logging.warning("'src' dir in project dir does not contain a 'requirements.txt' file."
                        f" It should be present in '{self.src_dir}' directory")

    def set_readme_file(self):
        """set readme_file attribute to the filename of the readme file within the 'src' dir

        The file must start with 'readme' (case-insensitive).
        """

        for item in self.project_dir_items:
            if item.lower().startswith("readme."):
                self.readme_file = item
                return

        logging.warning(f"'{self.project_dir} dir does not contain a readme file. ")

    def set_license_file(self):
        """set license_file attribute to the filename of the license file within the 'src' dir

        The file must start with 'license' (case-insensitive).
        """
        for item in self.project_dir_items:
            if item.lower().startswith("license"):
                self.license_file = item
                return

        logging.warning(f"'{self.project_dir} dir does not contain a licence file. ")

    def set_init_file(self):
        """set init_file attribute and the code_dir_name attribute

        The full path to the __init__.py file within the code dir of 'src'
        """
        # The first folder found within the 'src' dir which contains a '__init__.py' file
        # will be considered the code dir.
        for item in self.src_items:
            item_path = os.path.join(self.src_dir, item)
            if os.path.isdir(item_path):
                code_files = os.listdir(item_path)
                if "__init__.py" in code_files:
                    self.init_file = os.path.join(item_path, "__init__.py")
                    self.code_dir_name = item
                    break

        if not self.code_dir_name:
            logging.error(f"No code directory found in the '{self.src_dir}' directory.")
            return

        if not self.init_file:
            logging.error(f"Code directory must include a __init__.py file")
            return

    def set_description(self):
        """set description attribute

        The content of the __description__ attribute in the __init__.py file.
        """
        # Search through the '__init__.py' file.
        # When a line starts with '__description__' it will be split on '='.
        # Keep only the text to the right for the '=' and strip away spaces
        # and hidden characters (linebreak).
        with open(self.init_file) as f:
            for line in f.readlines():
                if line.startswith("__description__"):
                    self.description = line.split("=")[-1].replace('"', '').strip()
                    return

        logging.warning(f"__init__.py file should include a description")

    def write_config_files(self):
        """writes the 'pyproject.toml' file and the 'setup.py' to the 'src' dir

        Before it calls the write methods to generates the files, the set_ methods are called
        (in order to set the required attributes):
            set_requirements_file()
            set_readme_file()
            set_license_file()
            set_init_file()
            set_description()
        """

        if not self.verify_project():
            logging.error("verification failed.")
            return

        # Call all the set methods and write file methods
        self.set_requirements_file()
        self.set_readme_file()
        self.set_license_file()
        self.set_init_file()
        self.set_description()
        self.write_setup_file(os.path.join(self.src_dir, "setup.py"))
        self.write_toml_file(os.path.join(self.src_dir, self.toml_filename))

    def write_setup_file(self, file_):
        # Set the content of the 'setup.py'
        # This is static content. It is the content of the 'pyproject.toml'
        # that matters.
        data = """#!/usr/bin/env python3

from setuptools import setup

setup()
"""
        # Write the content to the 'setup.py' file
        with open(file_, 'w') as f:
            f.write(data)

    def write_toml_file(self, file_):
        # Set the content of the 'pyproject.toml'
        # The values should already be set by the
        # set_ methods
        data = f"""[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.project_name}"
description = "{self.description}"
license = {{file = "{self.license_file}"}}
version = "{self.version}"
dynamic = ["readme", "dependencies"]

[tool.setuptools.dynamic]
readme = {{file = "{self.readme_file}", content-type = "text/markdown"}}
dependencies = {{file = ["{self.requirements_file}"]}}
"""
        # Write the content to the 'pyproject.toml' file
        with open(file_, 'w') as f:
            f.write(data)


########################################################################################################################


def main():
    if not PROJECT_NAME:
        logging.error("PROJECT_NAME not set.")
        exit(2)

    version = get_release_version(VERSION)
    if not version:
        logging.error(f"Unable to get a valid version for {str(VERSION)}.")
        exit(2)

    gp = GeneratePyproject(PROJECT_NAME, version)
    gp.write_config_files()


########################################################################################################################


if __name__ == '__main__':
    VERSION = os.getenv("VERSION")
    PROJECT_NAME = os.getenv("PROJECT_NAME")
    main()
