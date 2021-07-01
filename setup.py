#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='gitflow_linter',
    version='0.0.1',
    description='Checks if GitFlow is respected in a given repository, considering rules provided',
    long_description=read("README"),
    author='Poul Fighter',
    author_email='fighter.poul@gmail.com',
    packages=find_packages(exclude=["tests"]),
    entry_points={
        'console_scripts': [
            'gitflow-linter = gitflow_linter:main',
            'gitflow-linter-plugins = gitflow_linter:plugins',
        ],
    },
    python_requires='>3.8',
    license=read("LICENSE"),
    install_requires=[
        'pyyaml>=5.4.1,<6',
        'gitpython>=3.1.17,<4',
        'click>=7,<8',
    ]
)
