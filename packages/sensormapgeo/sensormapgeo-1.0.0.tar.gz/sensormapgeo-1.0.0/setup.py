#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sensormapgeo, Transform remote sensing images between sensor and map geometry.
#
# Copyright (C) 2020-2024
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
# - Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences Potsdam,
#   Germany (https://www.gfz-potsdam.de/)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The setup script."""

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("sensormapgeo/version.py") as version_file:
    exec(version_file.read(), version)

req = [
    'numpy',
    'gdal>=3.8',
    'pyresample>=1.17.0',
    'py_tools_ds>=0.18.0',
    'pyproj>=2.2', 'joblib'
]

req_setup = ['setuptools']

req_test = ['pytest', 'pytest-cov', 'pytest-reporter-html1', 'pytest-subtests', 'urlchecker']

req_doc = ['sphinx-argparse', 'sphinx_rtd_theme', 'sphinx-autodoc-typehints']

req_lint = ['flake8', 'pycodestyle', 'pydocstyle']

req_dev = req_setup + req_test + req_doc + req_lint

setup(
    author="Daniel Scheffler",
    author_email='daniel.scheffler@gfz-potsdam.de',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    description="A package for transforming remote sensing images between sensor and map geometry.",
    extras_require={
        "doc": req_doc,
        "test": req_test,
        "lint": req_lint,
        "dev": req_dev
    },
    include_package_data=True,
    install_requires=req,
    keywords=['sensormapgeo', 'geometric pre-processing', 'remote sensing', 'orthorectification'],
    license="Apache-2.0",
    long_description=readme,
    long_description_content_type='text/x-rst',
    name='sensormapgeo',
    packages=find_packages(exclude=['tests*']),
    project_urls={
        "Source code": "https://git.gfz-potsdam.de/EnMAP/sensormapgeo",
        "Issue Tracker": "https://git.gfz-potsdam.de/EnMAP/sensormapgeo/-/issues",
        "Documentation": "https://enmap.git-pages.gfz-potsdam.de/sensormapgeo/doc/",
        "Change log": "https://enmap.git-pages.gfz-potsdam.de/sensormapgeo/doc/history.html",
    },
    python_requires='>=3.8',
    setup_requires=req_setup,
    test_suite='tests',
    tests_require=req + req_test,
    url='https://git.gfz-potsdam.de/EnMAP/sensormapgeo',
    version=version['__version__'],
    zip_safe=False,
)
