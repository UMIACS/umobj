#!/usr/bin/env python

import logging
import os
import string
import random
import unittest
import six.moves.urllib.request
import six.moves.urllib.error
import six.moves.urllib.parse
import subprocess

from boto.s3.connection import S3Connection
from six.moves import range

log = logging.getLogger(__name__)


class TestWebobj(unittest.TestCase):

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
        try:
            self.vhost_domain = os.environ["VHOST_DOMAIN"]
        except KeyError:
            self.vhost_domain = "umiacs.io"

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
        # Attempt to set website.
        index = bucket.new_key("index.html")
        index1 = bucket.new_key("index1.html")
        error = bucket.new_key("error.html")
        error1 = bucket.new_key("error1.html")
        index.set_contents_from_string("Hello World!")
        index1.set_contents_from_string("Hello World 1!")
        error.set_contents_from_string("Error")
        error1.set_contents_from_string("Error 1")
        index.make_public()
        index1.make_public()
        error.make_public()
        error1.make_public()

        return bucket_name

    def tearDownBucket(self, bucket_name):
        bucket = self.conn.get_bucket(bucket_name)
        bucket.get_key("index.html").delete()
        bucket.get_key("index1.html").delete()
        bucket.get_key("error.html").delete()
        bucket.get_key("error1.html").delete()
        self.conn.delete_bucket(bucket_name)

    def test_create_website(self):
        # Create website configuration
        command = ("webobj -m create -c website --index=index.html " +
                   "--error=error.html %s" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 0)

        url = "https://%s.%s" % (self.bucket_name, self.vhost_domain)

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url)
            content = res.read().decode()
        except Exception as e:
            self.fail("Could not read from bucket site: %s" % str(e))

        assert content == "Hello World!", "Did not find correct index content."

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url + "/no_page")
            content = res.read()
        except six.moves.urllib.error.HTTPError as e:
            res = e.fp.read().decode()
            assert res == "Error", "Error page not set."
        except Exception as e:
            self.fail("Could not read from bucket site: %s" % str(e))

        command = ("webobj -f -m create -c website " +
                   "--index=index1.html --error=error1.html %s"
                   % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 0,
                         "Failed to overwrite configuration when forced")

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url)
            content = res.read().decode()
        except Exception as e:
            self.fail("Could not read from bucket site: %s" % str(e))

        assert content == "Hello World 1!"

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url + "/no_page")
            content = res.read()
        except six.moves.urllib.error.HTTPError as e:
            res = e.fp.read().decode()
            assert res == "Error 1", "Error page not set."
        except Exception as e:
            self.fail("Could not read from bucket site: %s" % str(e))

    def test_invalid_create_website_params(self):
        command = ("webobj -m create -c website --index=index.html " +
                   "--error=error.html %s" % self.gen_bucket_name())
        self.assertEqual(subprocess.call(command.split(" ")), 1,
                         "Failed to return error with no bucket.")

        command = ("webobj -m create -c website --index=index.html " +
                   "--error=error.html %s" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 0,
                         "Failed to create website conf when expected.")

        command = ("webobj -m create -c website --index=index1.html " +
                   "--error=error1.html %s" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 1,
                         "Failed to return error with preexisting website  " +
                         "conf and no force option.")

        command = ("webobj -m create -c website --index=index1.html " +
                   "--error=error1.html %s:somepath" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 1,
                         "Failed detect key path as invalid")

    def test_examine(self):
        command = ("webobj -m create -c website --index=index.html " +
                   "--error=error.html %s" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 0)

        command = "webobj -m examine -c website %s" % self.bucket_name
        expected = "Index: index.html\nError Key: error.html\n"
        actual = subprocess.check_output(command.split(" ")).decode()
        self.assertEqual(expected, actual, "Invalid examine output.")

    def test_delete(self):
        command = ("webobj -m create -c website --index=index.html " +
                   "--error=error.html %s" % self.bucket_name)
        self.assertEqual(subprocess.call(command.split(" ")), 0)

        command = "webobj -m delete -c website %s" % self.bucket_name
        self.assertEqual(subprocess.call(command.split(" ")), 0,
                         "Failed to delete website config.")

        url = "https://%s.%s" % (self.bucket_name, self.vhost_domain)
        try:
            six.moves.urllib.request.urlopen(url)
            self.fail("Website still returned on root of domain after delete.")
        except six.moves.urllib.error.HTTPError as e:
            assert e.code == 404, "Website did not 404 on root after delete"
        except Exception as e:
            self.fail("Invalid error reading from site: %s" % str(e))


if __name__ == "__main__":
    unittest.main()
