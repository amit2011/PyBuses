#!/usr/bin/env python

from setuptools import setup
from shutil import copyfile
import os


# def get_requirements():
#     packages = list()
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     with open(os.path.join(current_dir, "requirements.txt"), "r") as f:
#         for line in f.readlines():
#             if not line.isspace():
#                 packages.append(line.strip())
#     return packages

current_dir = os.path.dirname(os.path.abspath(__file__))
pybuses_dir = os.path.join(current_dir, "pybuses")
pybuses_assets_dir = os.path.join(current_dir, "pybuses_assets")
pybuses_assets_initfile_dir = os.path.join(pybuses_assets_dir, "__init__.py")
os.mkdir(pybuses_assets_dir)

copyfile(
    src=os.path.join(pybuses_dir, "assets.py"),
    dst=os.path.join(pybuses_assets_dir, "assets.py")
)

with open(pybuses_assets_initfile_dir, "w") as f:
    f.write("from .assets import *")


setup(
    name='PyBuses Assets',
    version='0.1',
    description='Python framework to help organizing and working with Buses and Stops.'
                'This package only includes the Bus and Stop assets used by PyBuses',
    author='David Lorenzo',
    author_email='david@python.xxx',
    url='https://www.github.com/enforcerzhukov',
    packages=['pybuses_assets'],
)
