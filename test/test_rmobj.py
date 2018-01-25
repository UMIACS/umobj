#!/usr/bin/env python

import logging
import os
import string
import random
import unittest
import subprocess

from boto.s3.connection import S3Connection

from umobj.key import key_exists

log = logging.getLogger(__name__)


def call(command):
    return subprocess.call(command, shell=True)


class TestRmobj(unittest.TestCase):

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
        self.tearDownBucket(self.bucket_name)

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

    def tearDownBucket(self, bucket_name):
        try:
            bucket = self.conn.get_bucket(bucket_name)
            bucket.get_key("foo/bar/file3").delete()
            bucket.get_key("foo/bar/file2").delete()
            bucket.get_key("foo/bar/file1").delete()
            bucket.get_key("foobar/file0").delete()
            bucket.get_key("foobar/").delete()
            bucket.get_key("foo/bar/").delete()
            bucket.get_key("foo/").delete()
            self.conn.delete_bucket(bucket_name)
        except:
            pass

    def get_bucket(self):
        try:
            return self.conn.get_bucket(self.bucket_name)
        except:
            return None

    def bucket_exists(self):
        return self.get_bucket() is not None

    def key_exists(self, key_name):
        bucket = self.get_bucket()
        if bucket is None:
            return False
        return key_exists(bucket, key_name)

    def test_key_exists(self):
        self.assertTrue(self.key_exists("foo/bar/file1"))
        self.get_bucket().get_key("foo/bar/file1").delete()
        self.assertFalse(self.key_exists("foo/bar/file1"))

    def test_delete_bucket(self):
        self.assertTrue(self.bucket_exists())
        command = ("../bin/rmobj -rf %s" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 0)
        self.assertFalse(self.bucket_exists())

    def test_prompt_once(self):
        # this command is going to ask for confirmation if we want to
        # recursively delete one keypath
        self.assertTrue(self.key_exists("foo/bar/file1"))
        command = ('echo "no" | ../bin/rmobj -r %s:foo/bar/file1' %
                   self.bucket_name)
        self.assertEqual(call(command), 0)
        self.assertTrue(self.key_exists("foo/bar/file1"))

        command = ('echo "yes" | ../bin/rmobj %s:foo/bar/file1' %
                   self.bucket_name)
        self.assertEqual(call(command), 0)
        self.assertFalse(self.key_exists("foo/bar/file1"))

    def test_cannot_delete_bucket_without_recursive_option(self):
        command = ('../bin/rmobj %s' % self.bucket_name)
        self.assertNotEqual(call(command), 0)
        self.assertTrue(self.bucket_exists())

    def test_cannot_delete_directory_without_recursive_option(self):
        self.assertTrue(self.key_exists("foo/bar/"))
        # with trailing slash
        command = ('../bin/rmobj %s:foo/bar' % self.bucket_name)
        self.assertNotEqual(call(command), 0)
        self.assertTrue(self.key_exists("foo/bar/"))

        # with trailing slash...should work in either case...
        command = ('../bin/rmobj %s:foo/bar/' % self.bucket_name)
        self.assertNotEqual(call(command), 0)
        self.assertTrue(self.key_exists("foo/bar/"))

    def test_delete_directory(self):
        command = ('../bin/rmobj -rf %s:foo/bar/' % self.bucket_name)
        self.assertEqual(call(command), 0)
        self.assertTrue(self.key_exists("foo/"))
        self.assertFalse(self.key_exists("foo/bar/file1"))
        self.assertFalse(self.key_exists("foo/bar/file2"))
        self.assertFalse(self.key_exists("foo/bar/file3"))
        self.assertFalse(self.key_exists("foo/bar/"))

    def test_appending_slash_to_directory_delete(self):
        # this is to ensure that if the user says they want to recursively
        # delete bucket:foo/ we do not also delete bucket:foobar/ if the user
        # doesn't include the slash on the end of foo
        command = ('../bin/rmobj -rf %s:foo' % self.bucket_name)
        self.assertEqual(call(command), 0)
        self.assertTrue(self.key_exists("foobar/"))
        self.assertTrue(self.key_exists("foobar/file0"))
        self.assertFalse(self.key_exists("foo/bar/file1"))
        self.assertFalse(self.key_exists("foo/bar/"))
        self.assertFalse(self.key_exists("foo/"))

    def test_delete_several_files(self):
        command = ('../bin/rmobj %s:foo/bar/file1 %s:foo/bar/file2' %
                   (self.bucket_name, self.bucket_name))
        self.assertEqual(call(command), 0)
        self.assertFalse(self.key_exists("foo/bar/file1"))
        self.assertFalse(self.key_exists("foo/bar/file2"))
        self.assertTrue(self.key_exists("foo/bar/file3"))

    def test_single_file_delete(self):
        command = ('../bin/rmobj %s:foo/bar/file1' % self.bucket_name)
        self.assertEqual(call(command), 0)
        self.assertFalse(self.key_exists("foo/bar/file1"))
        self.assertTrue(self.key_exists("foo/bar/file2"))

    def test_force(self):
        # non-existence checks should always be exit status 0 with force flag

        # nonexistant bucket
        command = ('../bin/rmobj -f %saaa:' % self.bucket_name)
        self.assertEqual(call(command), 0)

        # missing keys
        command = ('../bin/rmobj -f %s:file1' % self.bucket_name)
        self.assertEqual(call(command), 0)
        command = ('../bin/rmobj -f %s:dir1/' % self.bucket_name)
        self.assertEqual(call(command), 0)

        # API usage problems should still have non-zero exit status even
        # though the force flag was given

        # recursive option not given for bucket delete
        command = ('../bin/rmobj -f %s' % self.bucket_name)
        self.assertEqual(call(command), 1)

        # recursive option not given for directory delete
        command = ('../bin/rmobj -f %s:foo/' % self.bucket_name)
        self.assertEqual(call(command), 1)
        self.assertTrue(self.key_exists("foo/"))

    def test_delete_multiple_some_exists_some_do_not(self):
        # God, what a terrible function name.  Sorry.

        # test that if some files do exist and some don't that we keep
        # looping over everything, but record the right exit status
        command = ('echo yes | ../bin/rmobj -r %s:foo/bar/fi %s:foo/bar/file1' %
                   (self.bucket_name, self.bucket_name))
        self.assertEqual(call(command), 1)
        self.assertFalse(self.key_exists("foo/bar/file1"))
        self.assertTrue(self.key_exists("foo/bar/file2"))

        # force flag given, 0 exit status
        command = ('echo yes | ../bin/rmobj -rf %s:foo/bar/fi %s:foo/bar/' %
                   (self.bucket_name, self.bucket_name))
        self.assertEqual(call(command), 0)
        self.assertFalse(self.key_exists("foo/bar/"))
        self.assertTrue(self.key_exists("foo/"))


if __name__ == "__main__":
    unittest.main()
