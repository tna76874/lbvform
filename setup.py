#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from setuptools import find_packages, setup

from lbvform.version import *
package_version = GitVersion('./lbvform', minor=0, major=0, minor_commit = 'fa158064e713acb651db3d484777c2e13419444a')

setup(
    name='lbvform',
    version=package_version._get_semantic_version(),
    description='lbvform',
    url='https://github.com/tna76874/lbvform',
    author='lmh',
    author_email='',
    license='BSD 2-clause',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyYAML",
        "numpy",
        "PyPDF2",
        "pycryptodome",
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires = ">=3.6",
    entry_points={
        "console_scripts": [
            "lbvform = lbvform.cli:main",
        ],
    },
    )
