#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.

.. currentmodule:: setup.py
.. moduleauthor:: kmushegi <mushegiani@gmail.com>
"""

import importlib.util
import os
from codecs import open  # Use a consistent encoding.
from os import path
from pathlib import Path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get the base version from the library.  (We'll find it in the `version.py`
# file in the src directory, but we'll bypass actually loading up the library.)
vspec = importlib.util.spec_from_file_location(
    "version",
    str(Path(__file__).resolve().parent / "komodo_cli" / "version.py"),
)
vmod = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(vmod)
version = getattr(vmod, "__version__")

# If the environment has a build number set...
if os.getenv("buildnum") is not None:
    # ...append it to the version.
    version = f"{version}.{os.getenv('buildnum')}"

print(
    find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
        include=["*"],
    )
)

setup(
    name="komo",
    description="A CLI client for Komodo AI",
    long_description=long_description,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    version=version,
    install_requires=[
        "boto3",
        "click",
        "docker",
        "GitPython",
        "jinja2",
        "kubernetes",
        "loguru",
        "pip-check-reqs",
        "pip-licenses",
        "pylint",
        "pytest",
        "pytest-cov",
        "pytest-pythonpath",
        "requests",
        "setuptools",
        "Sphinx",
        "sphinx-rtd-theme",
        "tabulate",
        "tox",
        "twine",
        "vyper-config",
    ],
    entry_points="""
    [console_scripts]
    komo=komodo_cli.cli:cli
    """,
    python_requires=">=3",
    license=None,  # noqa
    author="Komodo AI",
    author_email="mushegiani@gmail.com",
    # Use the URL to the github repo.
    url="https://github.com/komodoai/komo_cli",
    download_url=(f"https://github.com/komodoai/" f"komo_cli/archive/{version}.tar.gz"),
    keywords=[
        "komodo",
        "komodoai",
        "mlops",
        "dev tools",
        "machine learning",
        "infrastructure",
    ],
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        # "Development Status :: 3 - Beta",
        # Indicate who your project is intended for.
        # "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        # Pick your license.  (It should match "license" above.)
        """License :: OSI Approved :: Apache Software License""",  # noqa
        # noqa
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
