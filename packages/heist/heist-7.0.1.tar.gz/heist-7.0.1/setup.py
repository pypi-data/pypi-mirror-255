#!/usr/bin/env python3
import os
import shutil

from setuptools import Command
from setuptools import setup

NAME = "heist"
DESC = "Pluggable ephemeral software tunneling and delivery system"

# Version info -- read without importing
_locals = {}
with open(f"{NAME}/version.py") as fp:
    exec(fp.read(), None, _locals)
VERSION = _locals["version"]
SETUP_DIRNAME = os.path.dirname(__file__)
if not SETUP_DIRNAME:
    SETUP_DIRNAME = os.getcwd()


with open("requirements/base.txt") as f:
    REQUIREMENTS = f.read().splitlines()

with open("README.rst", encoding="utf-8") as f:
    LONG_DESC = f.read()


class Clean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for subdir in (NAME, "tests"):
            for root, dirs, files in os.walk(
                os.path.join(os.path.dirname(__file__), subdir)
            ):
                for dir_ in dirs:
                    if dir_ == "__pycache__":
                        shutil.rmtree(os.path.join(root, dir_))


def discover_packages():
    modules = []
    for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, NAME)):
        pdir = os.path.relpath(root, SETUP_DIRNAME)
        modname = pdir.replace(os.sep, ".")
        modules.append(modname)
    return modules


setup(
    name="heist",
    author="VMware Inc.",
    author_email="",
    url="https://gitlab.com/saltstack/pop/heist",
    version=VERSION,
    description=DESC,
    long_description=LONG_DESC,
    long_description_content_type="text/x-rst",
    python_requires=">=3.9",
    install_requires=REQUIREMENTS,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
    ],
    entry_points={
        "console_scripts": [
            "heist = heist.scripts:start",
        ],
    },
    packages=discover_packages(),
    cmdclass={"clean": Clean},
)
