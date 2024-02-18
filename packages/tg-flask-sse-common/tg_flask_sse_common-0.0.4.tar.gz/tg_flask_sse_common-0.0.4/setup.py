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
    name='tg_flask_sse_common',
    version='0.0.4',
    author='Tangshimin',
    description='tg_flask_sse_common',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        'tg_flask_sse_common'
    ],
    requires=['redis'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
