#!/usr/bin/env python

import logging
import os
import sys
import signal


def umobj_logging(level, filename=None):
    ''' Set up logging for the umobj utilties.  '''
    if filename is None:
        home_directory = os.path.expanduser("~")
        log_file = home_directory + os.sep + ".umobj.log"
    else:
        log_file = filename
    console_fmt = '%(levelname)s: %(message)s'
    file_fmt = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=file_fmt,
                        datefmt='%m-%d %H:%M',
                        filename=log_file,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter(console_fmt)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info('Finished setting up logging.')


def umobj_keyboard_interrupt_handler(signal, frame):
    '''Print Exiting... when registered in umobj_init_keyboard_interrupt'''
    print '\nExiting...'
    sys.exit(0)


def umobj_init_keyboard_interrupt():
    '''Override the default SIGINT handler so that a stack trace is not printed
    to the user when a SIGINT is called'''
    signal.signal(signal.SIGINT, umobj_keyboard_interrupt_handler)
