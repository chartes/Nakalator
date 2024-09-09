#!/usr/bin/env python3
# -- coding: utf-8 --

"""setup.py

This script is used to build the package nakalator and install it.
"""


from setuptools import setup

__version__ = '0.0.1-beta'

# Lire les dépendances depuis requirements.txt
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="nakalator",
    version=__version__,
    packages=['lib', 'lib.bridge', 'lib.utils'],
    package_data={'': ['nakala_request.so',
                       'nakala_request.dylib']},
    include_package_data=True,
    py_modules=["nakalator"],
    install_requires=required,
    entry_points={
        "console_scripts": [
            "nakalator=nakalator:app",
        ],
    },
)

