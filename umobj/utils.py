#!/usr/bin/env python

import logging
import os
import sys
import signal

from handler_queue import HandlerQueue
from contextlib import contextmanager
from boto.exception import S3CreateError, S3ResponseError, \
    BotoClientError, BotoServerError


@contextmanager
def boto_error_handler():
    '''Errors are caught in order for most to least specific'''
    try:
        yield
        return
    except S3ResponseError as e:
        if e.error_code in ['InvalidAccessKeyId', 'SignatureDoesNotMatch']:
            logging.error('Invalid credentials.')
            sys.exit(1)
        else:
            raise e


def umobj_excepthook(error_type, ex, traceback):
    '''Override sys.excepthook to handle any interesting uncaught exceptions'''
    if error_type == IOError:
        logging.error('Encountered an I/O error: %s' % ex.strerror)
        sys.exit(1)

    # if we didn't have a special reason to handle an exception above, pass
    # through to the default excepthook
    sys.__excepthook__(type, ex, traceback)


def umobj_set_excepthook():
    '''Set a custom excepthook for umobj'''
    sys.excepthook = umobj_excepthook


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
                        filemode='a')
    rotations = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=(1024 * 1024 * 10),
                backupCount=5)
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter(console_fmt)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.getLogger('').addHandler(rotations)
    logging.info('Finished setting up logging.')


def umobj_keyboard_interrupt_handler(signal, frame):
    '''Print Exiting... when registered in umobj_init_keyboard_interrupt'''
    print '\nExiting...'
    sys.exit(0)


def umobj_init_keyboard_interrupt():
    '''Override the default SIGINT handler so that a stack trace is not printed
    to the user when a SIGINT is called'''
    umobj_add_handler(signal.SIGINT, umobj_keyboard_interrupt_handler)


def umobj_add_handler(signal, handler):
    '''A passthrough function to adding a handler to the global HandlerQueue'''
    HandlerQueue.add_handler(signal, handler)


def umobj_init():
    '''
    Set some sensible initialization defaults for all umobj utilities

    This initiates common initialization tasks, like:
      * setting up a custom keyboard intrerrupt handler
      * providing a custom sys.excepthook function to handle specific uncaught
        errors wherever they appear without having to resort to littering the
        code with redundant try/except blocks.
    '''
    umobj_set_excepthook()
    umobj_init_keyboard_interrupt()


# Key/Bucket-specific manipulation

def umobj_get_bucket_key_pair_from_string(bucket_and_key):
    '''Return a tuple consisting of the bucket and then the key that are
    contained in the string bucket_and_key'''

    if bucket_and_key is None:
        return (None, None)

    # something like "foo:" is split into ['foo', '']
    values = bucket_and_key.split(":", 1)

    if len(values) == 2:
        if values[0] is '':
            values[0] = None
        if values[1] is '':
            values[1] = None
        return (values[0], values[1])
    elif len(values) == 1:
        if values[0] is '':
            return (None, None)
        else:
            return (values[0], None)
    else:  # should never reach here
        return (None, None)


def lremove(prefix, string):
    '''Returns string with the prefix removed'''
    if string.startswith(prefix):
        return string[len(prefix):]


def walk_path(path, character='/'):
    '''Generator that returns each part of a file like path'''
    parts = path.strip(character).split(character)
    for x, y in enumerate(parts):
        yield '/'.join(parts[0:x + 1])


def print_word_list(words, preface=None):
    '''Given an array, print it in a condensed form separated by spaces'''
    line_length = 79
    chars_left_in_line = line_length
    returning = ''
    if preface is not None:
        words.insert(0, preface)
    for word in words:
        if chars_left_in_line < len(word):
            returning += '\n'
            chars_left_in_line = line_length
        returning += ' %s' % (str(word))
        chars_left_in_line -= (len(str(word)) + 1)

    return returning


def sizeof_fmt(num):
    for x in ['b ', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, x)


def parse_key_value_pair(pair):
    '''
    Given a key-value string, parse the key and the value and return a
    tuple of the two.

    If it is unparsable, return pair, None
    '''
    parts = pair.split('=', 1)
    if len(parts) != 2:
        return pair, None
    return parts[0], parts[1]

