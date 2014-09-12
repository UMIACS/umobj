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

if sys.version_info <= (2, 5):
    error = "ERROR: umobj requires Python Version 2.6 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

def readme():
    with open("README.md") as f:
        return f.read()

setup(name = "umobj",
      version = __version__,
      description = "UMIACS Object Storage Commands",
      long_description = readme(),
      author = "Derek Yarnell",
      author_email = "derek@umiacs.umd.edu",
      scripts = ["bin/chobj", "bin/cpobj", "bin/lsobj",
                 "bin/cmpobj", "bin/mkobj", "bin/mvobj",
                 "bin/rmobj"],
      url = "https://staff.umiacs.umd.edu/gitlab/staff/UMobj",
      packages = ["umobj"],
      platforms = "Posix; MacOS X; Windows",
      classifiers = ["Development Status :: 5 - Production/Stable",
                     "Operating System :: OS Independent",
                     "Topic :: Internet",
                     "Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7"],
      **extra
      )
