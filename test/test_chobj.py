#!/usr/bin/env python

import logging
import os
import unittest
import string
import random
import subprocess


from boto.s3.connection import S3Connection

from umobj.key import key_exists, delete_key

log = logging.getLogger(__name__)


def call(command):
    return subprocess.call(command, shell=True)


class TestChobj(unittest.TestCase):

    @staticmethod
    def gen_bucket_name():
        chars = string.ascii_lowercase
        return "".join(random.choice(chars) for x in range(20))

    def setUp(self):
        try:
            host = os.environ["OBJ_SERVER"]
        except KeyError:
            host = "obj.umiacs.umd.edu"
        try:
            access_key = os.environ["OBJ_ACCESS_KEY_ID"]
        except KeyError:
            log.error("Please provide access_key")
        try:
            secret_key = os.environ["OBJ_SECRET_ACCESS_KEY"]
        except KeyError:
            log.error("Please provide secret_key")
        self.conn = S3Connection(host=host, port=443,
                                 is_secure=True,
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key)

        self.bucket_name = self.setUpBucket()

    def tearDown(self):
        bucket = self.get_bucket()
        if bucket:
            for key in bucket.list():
                delete_key(bucket, key.name)
            self.conn.delete_bucket(self.bucket_name)

    def setUpBucket(self):
        bucket_name = self.gen_bucket_name()
        try:
            bucket = self.conn.create_bucket(bucket_name)
        except Exception:
            log.exception("Failed to create bucket %s." % bucket_name)
            return False

        self.assertFalse(bucket is None, "Failed to create bucket")
        # Attempt to create directory structure
        foo = bucket.new_key("foo/")
        foobar = bucket.new_key("foobar/")
        bar = bucket.new_key("foo/bar/")

        foo.set_contents_from_string("")
        foobar.set_contents_from_string("")
        bar.set_contents_from_string("")

        file0 = bucket.new_key("foobar/file0")
        file1 = bucket.new_key("foo/bar/file1")
        file2 = bucket.new_key("foo/bar/file2")
        file3 = bucket.new_key("foo/bar/file3")
        file0.set_contents_from_string("this is file0")
        file1.set_contents_from_string("this is file1")
        file2.set_contents_from_string("this is file2")
        file3.set_contents_from_string("this is file3")

        return bucket_name

    def get_bucket(self):
        try:
            return self.conn.get_bucket(self.bucket_name)
        except:
            return None

    def bucket_exists(self):
        return self.get_bucket(self.bucket_name)

    def key_exists(self, key_name):
        bucket = self.get_bucket()
        if bucket is None:
            return False
        return key_exists(bucket, key_name)

    def test_key_exists(self):
        self.assertTrue(self.key_exists("foo/bar/file1"))
        self.get_bucket().get_key("foo/bar/file1").delete()
        self.assertFalse(self.key_exists("foo/bar/file1"))

    def add_policy(self):
        command = ('chobj -m add -p chrissul:READ %s' % self.bucket_name)
        return call(command)

    def test_add_policy(self):
        self.assertEqual(self.add_policy(), 0)
        policy = self.get_bucket().get_acl()
        self.assertTrue(len(policy.acl.grants) > 1)

    def test_clear(self):
        self.add_policy()
        policy = self.get_bucket().get_acl()
        self.assertTrue(len(policy.acl.grants) > 1)
        command = ('chobj -m clear %s' % self.bucket_name)
        self.assertEqual(call(command), 0)
        policy = self.get_bucket().get_acl()
        self.assertEqual(len(policy.acl.grants), 1)


if __name__ == "__main__":
    unittest.main()
