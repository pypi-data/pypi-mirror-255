#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author  : nickdecodes
@Email   : nickdecodes@163.com
@Usage   :
@FileName: dependency_scanner.py
@DateTime: 2024/1/29 11:13
@SoftWare:
"""

import os
import re
import requests
import asyncio
import aiohttp
from typing import List, Set, Dict, Coroutine, Any
from stdlib_list import stdlib_list


class DependencyScanner:
    @classmethod
    def write_requirements(cls, packages: Set[str], file_path: str = "requirements.txt") -> None:
        """
        Writes the provided set of packages to a requirements.txt file.

        This method takes a set of package names and writes them into a specified file,
        sorted alphabetically. If no filename is specified, 'requirements.txt' is used by default.
        This is commonly used to create a requirements file for Python projects, listing all external packages.

        Args:
            packages (Set[str]): A set of package names to be written to the requirements file.
            file_path (str, optional): The name of the file to write the requirements to. Defaults to "requirements.txt".

        Returns:
            None
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            for imp in sorted(packages):
                file.write(imp + '\n')
        print(f"Requirements written to {file_path}")

    @classmethod
    async def find_pypi_package_name(cls, package_name: str) -> bool:
        """
        Asynchronously checks if the given package name exists on PyPI.

        Args:
            package_name (str): The package name to check.

        Returns:
            bool: True if the package exists on PyPI, False otherwise.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pypi.org/pypi/{package_name}/json') as response:
                return response.status == 200

    @classmethod
    def find_python_files(cls, directory: str) -> List[str]:
        """
        Recursively find all Python files (.py) in the given directory.

        Args:
            directory (str): The directory path to search in.

        Returns:
            List[str]: A list of paths to Python files found within the directory.
        """
        py_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    @classmethod
    def extract_imports(cls, file_path: str, python_version: str) -> Set[str]:
        """
        Extracts import statements from a specified Python file and filters out packages that are part of the
        Python standard library. Only considers lines where 'from' or 'import' are at the beginning.

        Args:
            file_path (str): The path to the Python file to analyze.
            python_version (str): The target Python version used to determine which packages are part of the standard
                                  library.

        Returns:
            Set[str]: A set of non-standard library package names extracted from the file.
        """
        imports = set()
        stdlib_modules = set(
            stdlib_list(python_version))  # Get the standard library list for the specified Python version

        # Adjusted regex to match 'import module' and 'from module import something' forms at the start of a line
        pattern = re.compile(r'^\s*(from\s+(\S+)|import\s+((?:\S+\s*,\s*)*\S+))')

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    # Extract module names
                    module = match.group(2) or match.group(3)
                    if module:
                        module_names = module.replace(' ', '').split(',')
                        for name in module_names:
                            # Filter out module that start with a dot.
                            if name.startswith('.'):
                                continue
                            # Take the root name of the module and check if it's not in the standard library
                            root_module = name.split('.')[0]
                            if root_module not in stdlib_modules:
                                imports.add(root_module)
        return imports

    @staticmethod
    def group_files_by_package_name(files: List[str]) -> Dict[str, List[str]]:
        """
        Groups a list of file paths by their package names.

        Args:
            files (List[str]): A list of file paths.

        Returns:
            Dict[str, List[str]]: A dictionary where each key is a package name and its value is a list of files
                                  belonging to that package.

        Note:
            This function assumes that the file name (excluding the extension) represents its package name,
            except for '__init__.py' files, where the parent directory's name is considered the package name.
        """
        package_files_group = {}
        for file_path in files:
            # Special handling for '__init__.py' files
            if os.path.basename(file_path) == '__init__.py':
                # Use the parent directory's name as the package name
                package_name = os.path.basename(os.path.dirname(file_path))
            else:
                # Use os.path.splitext to obtain the file name without the extension as the package name
                package_name, _ = os.path.splitext(os.path.basename(file_path))

            # Add the file to the list associated with its package name
            package_files_group.setdefault(package_name, []).append(file_path)
        return package_files_group

    @classmethod
    async def async_scan_project(cls, project_directory: str, python_version: str = "3.8") -> Dict[str, Any]:
        """
        Asynchronously scans a project directory to identify Python packages used,
        differentiating between project-specific and external packages, and checks
        which of the external packages are available on PyPI.

        :param project_directory: The path to the project directory to be scanned.
        :type project_directory: str
        :param python_version: The version of Python used in the project, defaults to "3.8".
        :type python_version: str
        :return: A dictionary containing sets/lists of all packages, packages found on PyPI,
                 packages not found on PyPI, and project-specific packages grouped by package name.
        :rtype: Dict[str, Any]  # Ideally, specify more detailed types for return values if possible.
        """
        py_files = cls.find_python_files(project_directory)  # Assume this returns a list of file paths.
        project_package_group = cls.group_files_by_package_name(py_files)  # Assume this returns a dict mapping package names to file paths.
        all_package: Set[str] = set()
        project_package: Set[str] = set()

        for file in py_files:
            file_imports = cls.extract_imports(file, python_version)  # Assume this returns a set of import package names.
            for import_package in file_imports:
                if import_package in project_package_group:
                    project_package.add(import_package)
                else:
                    all_package.add(import_package)

        # Asynchronously check all packages for availability on PyPI.
        check_tasks: List[Coroutine] = [cls.find_pypi_package_name(package) for package in all_package]  # Assume this returns a coroutine.
        results = await asyncio.gather(*check_tasks)

        found_in_pypi: Set[str] = {pkg for pkg, found in zip(all_package, results) if found}
        not_found_in_pypi: Set[str] = all_package - found_in_pypi

        scan_result: Dict[str, Any] = {
            'all_package': all_package,
            'found_in_pypi': found_in_pypi,
            'not_found_in_pypi': not_found_in_pypi,
            'project_package': {
                package: files for package, files in project_package_group.items() if package in project_package
            }
        }
        return scan_result

    @classmethod
    async def get_installed_packages(cls) -> List[str]:
        """
        Asynchronously run the `pip freeze` command and return a list of installed package names and versions.
        """
        proc = await asyncio.create_subprocess_shell(
            'pip freeze',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        # Remove the last empty element that results from splitting the output
        package_versions = stdout.decode().strip().split('\n')
        return package_versions

    @classmethod
    async def get_package_dependencies(cls, package_name: str) -> List[str]:
        """
        Asynchronously run the `pip show` command to get dependencies of a specified package and
        return a list of dependency package names.
        """
        proc = await asyncio.create_subprocess_shell(
            f'pip show {package_name}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        # Use regex to find the dependencies listed after 'Requires:'
        requires_match = re.search(r'^Requires: (.+)$', stdout.decode(), re.MULTILINE)
        if requires_match:
            # Split the dependencies string into a list, strip whitespace from each dependency name
            dependencies = [dep.strip() for dep in requires_match.group(1).split(',')]
        else:
            # If there are no dependencies, return an empty list
            dependencies = []
        return dependencies

    @classmethod
    async def analyze_dependencies(cls) -> Dict[str, List[str]]:
        """Asynchronously analyze and return the dependency relationships of all installed packages."""
        dependencies_dict = {}
        package_versions = await cls.get_installed_packages()
        # Extract package names from the package_version strings
        packages = [pkg.split('==')[0] for pkg in package_versions]
        tasks = [cls.get_package_dependencies(package) for package in packages]
        dependencies_list = await asyncio.gather(*tasks)

        for package_version, dependencies in zip(package_versions, dependencies_list):
            dependencies_dict[package_version] = dependencies

        # Remove packages that are dependencies of other packages, keeping only primary packages
        all_dependencies = set(dep for deps in dependencies_list for dep in deps)
        primary_packages = {
            pkg: deps for pkg, deps in dependencies_dict.items() if pkg.split('==')[0] not in all_dependencies
        }

        return primary_packages

    @classmethod
    def scan_project(cls, project_directory: str, python_version: str = "3.8") -> Dict[str, Any]:
        """
        Synchronous wrapper for the asynchronous scan_project method.

        :param project_directory: Path to the project directory.
        :type project_directory: str
        :param python_version: Python version, defaults to 3.8.
        :type python_version: str
        :return: A dictionary containing the scan results.
        :rtype: Dict[str, Any]
        """
        return asyncio.run(cls.async_scan_project(project_directory, python_version))

    @classmethod
    def scan_pipenv(cls) -> Dict[str, List[str]]:
        """
        Synchronously scan the current environment managed by pipenv to determine the dependency relationships
        of all installed packages and return a dictionary mapping package names (with versions) to lists of their
        dependencies.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are package names with their versions, and values are lists
                                  of package names (dependencies) that the key package depends on.
        """
        dependencies = asyncio.run(cls.analyze_dependencies())
        return dependencies
