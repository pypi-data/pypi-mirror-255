#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import unlock_joblib_tasks

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="unlock_joblib_tasks",
    version=unlock_joblib_tasks.__version__,
    author="PlumeSoft",
    author_email="master@plumesoft.com",
    description="Unlock the limit of 63 tasks in Windows for the Python joblib library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD 3-Clause",
    url="https://github.com/cnzjy/unlock_joblib_tasks",
    py_modules=['unlock_joblib_tasks'],
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: System :: Operating System",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
