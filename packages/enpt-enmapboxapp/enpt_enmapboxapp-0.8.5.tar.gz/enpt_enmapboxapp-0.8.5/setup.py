#!/usr/bin/env python
# -*- coding: utf-8 -*-

# enpt_enmapboxapp, A QGIS EnMAPBox plugin providing a GUI for the EnMAP processing tools (EnPT)
#
# Copyright (C) 2018-2024 Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""The setup script."""

from setuptools import setup, find_packages
from importlib.util import find_spec
from importlib.metadata import version as _get_version
from warnings import warn

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("enpt_enmapboxapp/version.py", encoding='utf-8') as version_file:
    exec(version_file.read(), version)

req = [
    'packaging',
    'psutil',
    # 'qgis',  # conda install -c conda-forge qgis
    # 'enmapbox'  # installation: https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html
    ]

req_setup = ['packaging']

req_test = ['pytest', 'pytest-cov', 'pytest-reporter-html1', 'urlchecker']

req_doc = ['sphinx-argparse', 'sphinx_rtd_theme']

req_lint = ['flake8', 'pycodestyle', 'pydocstyle']

req_deploy = ['twine', 'build']

req_dev = req_setup + req_test + req_doc + req_lint + req_deploy

setup(
    author="Daniel Scheffler",
    author_email='danschef@gfz-potsdam.de',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    description="A QGIS EnMAPBox plugin providing a GUI for the EnMAP processing tools (EnPT).",
    extras_require={
        "doc": req_doc,
        "test": req_test,
        "lint": req_lint,
        "deploy": req_deploy,
        "dev": req_dev
    },
    install_requires=req,
    license="GPL-3.0-or-later",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords=['enpt_enmapboxapp', 'EnMAP', 'EnMAP-Box', 'hyperspectral', 'remote sensing', 'satellite',
              'processing chain'],
    name='enpt_enmapboxapp',
    packages=find_packages(include=['enpt_enmapboxapp']),
    python_requires='>=3.8',
    scripts=[
        'bin/enpt_run_cmd.bat',
        'bin/enpt_run_cmd.sh'
    ],  # include both OS scripts because the feedstock build running on Linux would only include the .sh otherwise
    setup_requires=req_setup,
    test_suite='tests',
    tests_require=req_test,
    url='https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp',
    version=version['__version__'],
    zip_safe=False,
)


# check for missing dependencies #
##################################

installationlink = 'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html'

# check for qgis
if not find_spec('qgis'):
    warn('You need to install QGIS to run the EnPT-EnMAPBox-App. See here for installation instructions: %s'
         % installationlink)

# check for enmapbox
if not find_spec('enmapbox'):
    warn('You need to install the EnMAP-Box to run the EnPT-EnMAPBox-App. See here for installation instructions: %s'
         % installationlink)

# check for enpt
if find_spec('enpt'):
    from packaging.version import parse as _parse_version  # packaging is only available AFTER running setup()
    enpt_version = _get_version('enpt')
    if _parse_version(enpt_version) < _parse_version(version['_minimal_enpt_version']):
        warn(f"The EnPT backend package is already installed, however, its version (v{enpt_version}) is too old "
             f"and not compatible anymore with enpt_enmapboxapp v{version['__version__']}. Please update the EnPT "
             f"backend code to at least version {version['_minimal_enpt_version']}! Refer to "
             f"https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html for more details.")
else:
    print(f"NOTE: To run EnPT within the EnMAP-Box via the EnPT GUI, the EnPT backend code is required "
          f"(minimal version: v{version['_minimal_enpt_version']}). Right now, it could not be found. Refer to "
          f"https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html for more details.")
