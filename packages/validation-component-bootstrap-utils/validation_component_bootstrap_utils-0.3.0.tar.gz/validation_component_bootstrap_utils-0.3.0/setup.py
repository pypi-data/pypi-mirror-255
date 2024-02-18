#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', "PyYAML", "jinja2", "Rich"]

test_requirements = [ ]

setup(
    author="Jaideep Sundaram",
    author_email='jai.python3@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Utilities for Bootstrapping Validation Components",
    entry_points={
        'console_scripts': [
            'bootstrap-validation-component=validation_component_bootstrap_utils.generate_validation_module:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='validation_component_bootstrap_utils',
    name='validation_component_bootstrap_utils',
    packages=find_packages(include=['validation_component_bootstrap_utils', 'validation_component_bootstrap_utils.*']),
    package_data={
        "validation_component_bootstrap_utils": [
            "conf/config.yaml",
            "templates/validation/record.py",
            "templates/validation/validate_file.py",
            "templates/validation/validator.py",
            "templates/validation/parser.py",
        ]
    },
    scripts=["scripts/make_executables_and_aliases.py"],
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jai-python3/validation-component-bootstrap-utils',
    version='0.3.0',
    zip_safe=False,
)
