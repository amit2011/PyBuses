#!/usr/bin/env python

from setuptools import setup
import os


def get_requirements():
    packages = list()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "requirements.txt"), "r") as f:
        for line in f.readlines():
            if not line.isspace():
                packages.append(line.strip())
    return packages


setup(
    name='PyBuses',
    version='0.1',
    description='Python framework to help organizing and working with Buses and Stops',
    author='David Lorenzo',
    author_email='david@python.xxx',
    url='https://www.github.com/enforcerzhukov',
    packages=['pybuses'],
    install_requires=get_requirements()
)
