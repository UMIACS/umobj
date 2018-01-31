import os
import logging
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat

log = logging.getLogger(__name__)


class Obj(object):

    def __init__(self, access_key, secret_key, host='obj.umiacs.umd.edu',
                 port=443, is_secure=True, calling_format=None):
        if calling_format is None:
            calling_format = OrdinaryCallingFormat()
        Obj.conn = S3Connection(host=host, port=port,
                                is_secure=is_secure,
                                aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key,
                                calling_format=calling_format)

    @staticmethod
    def connect(host=None, port=None, is_secure=True, access_key=None,
                secret_key=None):
        if host is None:
            try:
                host = os.environ['OBJ_SERVER']
            except:
                host = 'obj.umiacs.umd.edu'
        if port is None:
            if is_secure:
                port = 443
            else:
                port = 80
        if access_key is None:
            try:
                access_key = os.environ['OBJ_ACCESS_KEY_ID']
            except:
                logging.error("Please provide access_key")
                return False
        if secret_key is None:
            try:
                secret_key = os.environ['OBJ_SECRET_ACCESS_KEY']
            except:
                logging.error("Please provide secret_key")
                return False
        Obj(host=host, port=port, access_key=access_key, is_secure=is_secure,
            secret_key=secret_key)
        return True
