#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'colorful>=0.4.0',
    'Pygments>=2.2.0'
]

setup_requirements = [
    'pytest-runner',
    # TODO(tommikaikkonen): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'hypothesis',
    'dataclasses',
    'requests',
    'attrs',
    'IPython',
    'pytz'
    'tox-pyenv'
]

setup(
    name='prettyprinter',
    version='0.10.0',
    description="Syntax-highlighting, declarative and composable pretty printer for Python 3.6+",
    long_description=readme + '\n\n' + history,
    author="Tommi Kaikkonen",
    author_email='kaikkonentommi@gmail.com',
    url='https://github.com/tommikaikkonen/prettyprinter',
    packages=find_packages(include=['prettyprinter', 'prettyprinter.extras']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='prettyprinter',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
