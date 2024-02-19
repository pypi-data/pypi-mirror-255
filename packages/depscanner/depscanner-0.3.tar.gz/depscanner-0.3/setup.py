#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author  : nickdecodes
@Email   : nickdecodes@163.com
@Usage   :
@FileName: setup.py
@DateTime: 2024/1/28 18:50
@SoftWare: 
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='depscanner',
    version='0.3',
    keywords=['depscanner', 'python', 'dependency'],
    package_data={"": ["LICENSE", "NOTICE"]},
    include_package_data=True,
    packages=find_packages(),
    author="nickdecodes",
    author_email="nickdecodes@163.com",
    description="Python Dependency Scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=[
        'requests',
        'aiohttp',
        'stdlib_list',
        'requests',
        'twine'
    ],
    project_urls={
        "Documentation": "http://python-depscanner.readthedocs.io",
        "Source": "https://github.com/nickdecodes/python-depscanner",
    },
)
