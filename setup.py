#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = []
with open('stable-requirements.txt') as f:
    requirements = f.read().splitlines()

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Thomas Scholtz",
    author_email='thomas@labs.epiuse.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
    ],
    description="Client Central Python API.",
    entry_points={
        'console_scripts': [
            'test=test.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords=['ClientCentral', 'Client', 'EPI-USE Labs', 'EPI-USE', 'Client-Central'],
    name='clientcentral',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/EPI-USE-Labs/client-central-python-api',
    version='12.2.2',
    zip_safe=False,
    data_files=[('.', [])],
    python_requires='>=3.9'
)
