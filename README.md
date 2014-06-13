# umobj
Command Line Utilties for UMIACS Object Storage Services

This is a collection of utilities written in Python using the
standard Boto library.  They all support some common environment
variables that can be set to avoid needing to specified each
command line.

 * *OBJ_ACCESS_KEY_ID* - The users access key
 * *OBJ_SECRET_ACCESS_KEY* - The users secret key
 * *OBJ_SERVER*  - The object server to use

## Requirements

These utilties and libraries are work with Python 2.6+ (and are not tested
    under Python 3.x+).  They require the following modules:

- Boto > 2.5.x
- FileChunkIO
- Progressbar

If running python 2.6 you need to have the following backports

- argparse

These are most easily going to be satisfied with a virtualenv.

## Installation

```python setup.py install```
