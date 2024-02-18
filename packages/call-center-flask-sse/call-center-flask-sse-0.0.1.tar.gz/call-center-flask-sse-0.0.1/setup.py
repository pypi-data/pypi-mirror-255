#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    setup.py

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-31

"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='call-center-flask-sse',
    version='0.0.1',
    author='Tangshimin',
    description='flask sse',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    requires=['flask', 'redis'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
