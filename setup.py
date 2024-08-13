#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from setuptools import find_packages, setup

from versionmygit.version import *
package_version = GitVersion('./lbvform', minor=1, major=0, minor_commit = '09be8d42e74df9083ce01d36573b98a50c7781f7')

setup(
    name='lbvform',
    version=package_version._get_semantic_version(),
    description='lbvform',
    url='https://github.com/tna76874/lbvform',
    author='lmh',
    author_email='',
    license='BSD 2-clause',
    packages=find_packages(exclude=['versionmygit']),
    include_package_data=True,
    install_requires=[
        "PyYAML",
        "numpy",
        "PyPDF2",
        "pycryptodome",
        "python-slugify",
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
