#!/usr/bin/env python

import logging
import os
import string
import random
import unittest
import urllib2
import subprocess

from boto.s3.connection import S3Connection

log = logging.getLogger(__name__)


def get_env():
    return {
        "PATH": "/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin",
        "OBJ_SERVER": os.environ.get("OBJ_SERVER"),
        "OBJ_ACCESS_KEY_ID": os.environ.get("OBJ_ACCESS_KEY_ID"),
        "OBJ_SECRET_ACCESS_KEY": os.environ.get("OBJ_SECRET_ACCESS_KEY")
    }


class TestDownload(unittest.TestCase):

    @staticmethod
    def gen_bucket_name():
        chars = string.ascii_lowercase
        return "".join(random.choice(chars) for x in range(20))

    def setUp(self):
        try:
            host = os.environ["OBJ_SERVER"]
        except:
            host = "obj.umiacs.umd.edu"
        try:
            access_key = os.environ["OBJ_ACCESS_KEY_ID"]
        except:
            log.error("Please provide access_key")
        try:
            secret_key = os.environ["OBJ_SECRET_ACCESS_KEY"]
        except:
            log.error("Please provide secret_key")
        self.conn = S3Connection(host=host, port=443,
                                 is_secure=True,
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key)

        self.bucket_name = self.setUpBucket()

    def tearDown(self):
        self.tearDownBucket(self.bucket_name)
        self.cleanDirectory()

    def setUpBucket(self):
        bucket_name = self.gen_bucket_name()
        try:
            bucket = self.conn.create_bucket(bucket_name)
        except Exception as e:
            log.exception("Failed to create bucket %s." % bucket_name)
            return False

        self.assertFalse(bucket is None, "Failed to create bucket")
        # Attempt to set website.
        file1 = bucket.new_key("file1.txt")
        file1.set_contents_from_string("Hello World!")
        file1.make_public()

        return bucket_name

    def tearDownBucket(self, bucket_name):
        bucket = self.conn.get_bucket(bucket_name)
        bucket.get_key("file1.txt").delete()
        self.conn.delete_bucket(bucket_name)

    def cleanDirectory(self):
        if 'file2.txt' in os.listdir('./'):
            os.remove('./file2.txt')

    def test_download_rename(self):
        # Create website configuration
        command = ("../bin/cpobj %s:file1.txt file2.txt" % (self.bucket_name))
        self.assertEqual(subprocess.call(command.split(" ")), 0)
        self.assertTrue('file1.txt' not in os.listdir('./'))
        self.assertTrue('file2.txt' in os.listdir('./'))
        with open('file2.txt', 'r') as file2:
            self.assertTrue(file2.read() == 'Hello World!')


if __name__ == "__main__":
    unittest.main()
