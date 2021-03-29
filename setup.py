#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

import nimmy

dependencies = ['blessed']
if sys.version_info < (3, 4):  # python 3.4 include the enum package
    dependencies.append('enum34')

setup(
    name='nimmy',
    version=nimmy.__version__,
    description="A Terminal UI to play a variation of nim against a bot",
    author="Mason Legere",
    author_email="masonlegere@gmail.com",
    url="https://github.com/MasonLegere/Nimmy",
    license='LGPLv3',
    install_requires=dependencies,
    packages=find_packages(exclude=["tests"]),
    entry_points={'console_scripts': ('nimmy = nimmy:main')},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Terminals'
        ],
    keywords=['Nim', 'terminal', 'game', 'board']
)