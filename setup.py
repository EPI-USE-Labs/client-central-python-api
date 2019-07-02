#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = []
with open('requirements') as f:
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
        'Programming Language :: Python :: 3.7',
    ],
    description="Client Central Python API.",
    entry_points={
        'console_scripts': [
            'test=test.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='ClientCentral',
    name='clientcentral',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://git.labs.epiuse.com:SWAT/clientcentral-api-python.git',
    version='6.0.2',
    zip_safe=False,
    data_files=[('.', ['clientcentral/prod_template.yaml','clientcentral/qa_template.yaml'])]
)
