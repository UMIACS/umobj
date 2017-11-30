#!/usr/bin/env python

from __future__ import with_statement

try:
    from setuptools import setup
    extra = dict(test_suite="tests.test.suite", include_package_data=True)
except ImportError:
    from distutils.core import setup
    extra = {}

import sys

from umobj import __version__

long_description = "Command-line utilties for S3-compatible Object Storage"

install_requires = [
    'boto',
    'filechunkio',
    'progressbar',
    'qav',
    'bagit'
]

if sys.version_info <= (2, 5):
    error = "ERROR: umobj requires Python Version 2.6 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

if sys.version_info <= (2, 6):
    install_requires.append('argparse')

setup(name="umobj",
      version=__version__,
      description="UMIACS Object Storage Commands",
      long_description=long_description,
      author="UMIACS Staff",
      author_email="github@umiacs.umd.edu",
      scripts=[
           "bin/bagobj",
           "bin/catobj",
           "bin/chobj",
           "bin/cmpobj",
           "bin/cpobj",
           "bin/lsobj",
           "bin/mkobj",
           "bin/mvobj",
           "bin/rmobj",
           "bin/syncobj",
           "bin/streamobj",
           "bin/webobj",
      ],
      url="https://github.com/UMIACS/umobj",
      packages=["umobj"],
      install_requires=install_requires,
      license="LGPL v2.1",
      platforms="Posix; MacOS X; Windows",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Operating System :: OS Independent",
                   "Topic :: Internet",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7"],
      **extra
      )
