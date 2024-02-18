# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

from Cython.Build import cythonize
from setuptools import find_packages, setup

install_requires = [
    "IsoSpecPy==2.2.1",
    "dill",
    "importlib-resources>=1.1.0; python_version < '3.9'",
    "jinja2",
    "matplotlib",
    "numpy>=1.17",
    "openpyxl",
    "pandas>=2.0.1",
    "pyper==1.1.1",
    "requests",
    "scikit-learn",
    "tqdm",
    "xlrd",
    "xlwt",
]

DOWNLOAD_URL = "https://sis.id.ethz.ch/_downloads"

if sys.platform == "win32":
    install_requires += ["pywin32"]


ext_modules = cythonize(os.path.join("src", "emzed", "optimized", "formula_fit.pyx"))

setup(
    name="emzed",
    version="3.0.0a18",
    description="",
    url="",
    author="Uwe Schmitt",
    author_email="uwe.schmitt@id.ethz.ch",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    ext_modules=ext_modules,
)
