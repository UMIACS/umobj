#!/usr/bin/env python

import logging
import os

def umobj_logging(level, filename=None):
    ''' Set up logging for the umobj utilties.  '''
    if filename is None:
        home_directory = os.path.expanduser("~")
        log_file = home_directory + os.sep + ".umobj.log"
    else:
        log_file = filename
    logger = logging.getLogger()
    fileHandler = logging.FileHandler(log_file)
    file_fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    if level is logging.INFO or level is logging.DEBUG:
        logging.basicConfig(level=level,
                            format='%(levelname)s: %(message)s')
        fileHandler.setLevel(level=level)
    else:
        logging.basicConfig(level=logging.WARNING,
                            format='%(levelname)s: %(message)s')
        fileHandler.setLevel(level=logging.INFO)
    fileHandler.setFormatter(file_fmt)
    logger.addHandler(fileHandler)
