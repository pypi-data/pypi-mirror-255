#!/usr/bin/env python

"""The setup script."""
import os

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'jsonpath-ng',
    'croniter'
]

test_requirements = [
    'pytest>=3',
    'responses'
]

setup(
    author="Perry Stallings",
    author_email='astal01@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python Integration Project Framework",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='parrot_integrations',
    name='parrot-integrations-core',
    packages=[f'parrot_integrations.{i}' for i in os.listdir('./parrot_integrations') if os.path.isdir(os.path.join('./parrot_integrations', i))],
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/perrystallings/parrot_integrations_core',
    version='0.0.17',
    zip_safe=False
)
