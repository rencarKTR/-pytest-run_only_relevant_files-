#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-run_only_relevant_files',
    version='0.0.1',
    author='Dev Doomari Rencar',
    author_email='devdoomari@imsmobility.co.kr',
    maintainer='Dev Doomari Rencar',
    maintainer_email='devdoomari@imsmobility.co.kr',
    license='MIT',
    url='https://github.com/devdoomari3/pytest-run_only_relevant_files',
    description='Pytest plugin to run only relevant files [',
    long_description=read('README.rst'),
    py_modules=['pytest_run_only_relevant_files', 'unaffected_tests_filter'],
    packages=find_packages(
        include=[
            'unaffected_tests_filter',
            'unaffected_tests_filter.*'
        ],
    ),
    python_requires='>=3.7',
    install_requires=['pytest>=6.2.4'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'run_only_relevant_files = pytest_run_only_relevant_files',
        ],
    },
)
