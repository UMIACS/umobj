#!/usr/bin/env python

from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

from umobj import __version__

long_description = "Command-line utilities for S3-compatible Object Storage"

install_requires = [
    'boto >= 2.49.0',
    'filechunkio',
    'progressbar',
    'qav',
    'bagit >= 1.7.0',
    'certifi >= 2019.11.28',
]

if sys.version_info <= (2, 6):
    errormsg = "ERROR: umobj requires Python Version 2.7 or above... Exiting.\n"
    sys.stderr.write(errormsg)
    sys.exit(1)

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
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Operating System :: OS Independent",
          "Topic :: Internet",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
      ],
      )
