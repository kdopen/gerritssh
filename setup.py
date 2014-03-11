#!/usr/bin/env python

import os
import sys
from setuptools.command.test import test as TestCommand
from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


readme = open('README.rst').read()
from gerritssh import __version__ as gerritssh_version

doclink = """
Documentation
-------------

The full documentation is at http://gerritssh.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='gerritssh',
    version=gerritssh_version,
    description='Python package wrapping the Gerrit command line API',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Keith Derrick',
    author_email='kderrick_public@att.net',
    url='https://github.com/kdopen/gerritssh',
    packages= find_packages(exclude=['test']),
    package_dir={'gerritssh': 'gerritssh'},
    include_package_data=True,
    install_requires=[
    ],
    license='Apache',
    zip_safe=False,
    keywords='gerritssh',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License 2.0',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=['pytest>=2.3.5'],
    cmdclass={'test': PyTest},
    scripts=['gsshcli.py'],
)
