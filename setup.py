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
    'Pygments>=2.2.0',
]

setup_requirements = [
    'pytest-runner==3.0',
    # TODO(tommikaikkonen): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest==4.3.0',
    'hypothesis==3.33.0',
    'dataclasses==0.6',
    'django>=1.10.8',
    'requests==2.21.0',
    'attrs==17.4.0',
    'IPython==6.2.1',
    'pytz==2017.3',
    'tox-pyenv==1.1.0',
    'pytest-django==3.4.7',
    'pytest-pythonpath==0.7.3',
]

setup(
    name='prettyprinter',
    version='0.15.0',
    description="Syntax-highlighting, declarative and composable pretty printer for Python 3.5+",
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
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
