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
    version='0.0.1',
    author='Tangshimin',
    description='tg_flask_sse_common for call-center',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        'tg_flask_sse_common.api', 'tg_flask_sse_common.cache',
        'tg_flask_sse_common.configs', 'tg_flask_sse_common.logic'
    ],
    requires=['flask', 'redis'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
