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


readme = '\n' + open('README.rst').read()
import VERSION

doclink = """
Documentation
-------------

The full documentation is at http://gerritssh.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='gerritssh',
    version=VERSION.__version__,
    description='Python package wrapping the Gerrit command line API',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author=VERSION.__author__,
    author_email=VERSION.__email__,
    url='https://github.com/kdopen/gerritssh',
    packages=find_packages(exclude=['test']),
    package_dir={'gerritssh': 'gerritssh'},
    include_package_data=True,
    install_requires=['paramiko>=1.13,<2',
                      'semantic-version>=2.3,<3'
                     ],
    license='Apache',
    zip_safe=False,
    keywords='gerritssh',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    tests_require=['pytest>=2.3.5'],
    cmdclass={'test': PyTest},
    scripts=['gsshcli.py'],
)
