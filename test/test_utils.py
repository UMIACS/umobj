#!/usr/bin/env python

import unittest

from umobj.utils import umobj_get_bucket_key_pair_from_string, path_parts


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_blank_bucket_and_key(self):
        bucket, key = umobj_get_bucket_key_pair_from_string("")
        self.assertTrue(bucket is None)
        self.assertTrue(key is None)

    def test_bucket_name_without_colon(self):
        bucket, key = umobj_get_bucket_key_pair_from_string("bucket")
        self.assertTrue(bucket == "bucket")
        self.assertTrue(key is None)

    def test_bucket_name_with_colon(self):
        bucket, key = umobj_get_bucket_key_pair_from_string("bucket:")
        self.assertTrue(bucket == "bucket")
        self.assertTrue(key is None)

    def test_bucket_and_key_name(self):
        bucket, key = umobj_get_bucket_key_pair_from_string("bucket:key")
        self.assertTrue(bucket == "bucket")
        self.assertTrue(key == "key")

    def test_key_name_without_bucket_name(self):
        bucket, key = umobj_get_bucket_key_pair_from_string(":key")
        self.assertTrue(bucket is None)
        self.assertTrue(key == "key")

    def test_colon_without_bucket_or_key_name(self):
        bucket, key = umobj_get_bucket_key_pair_from_string(":")
        self.assertTrue(bucket is None)
        self.assertTrue(key is None)

    def test_colons_in_key_name(self):
        bucket, key = umobj_get_bucket_key_pair_from_string("bucket:key:foo")
        self.assertTrue(bucket == "bucket")
        self.assertTrue(key == "key:foo")

    def test_multiple_colons_and_no_bucket(self):
        bucket, key = umobj_get_bucket_key_pair_from_string("::")
        self.assertTrue(bucket is None)
        self.assertTrue(key == ":")

    def test_path_parts(self):
        assert sorted(list(path_parts('/tmp/foo/bar/'))) == \
            sorted(["/", "/tmp", "/tmp/foo", "/tmp/foo/bar"])

        assert sorted(list(path_parts('./tmp/foo/'))) == \
            sorted(["./tmp/foo", "./tmp", "."])

        assert sorted(list(path_parts('../tmp/foo/'))) == \
            sorted(["../tmp/foo", "../tmp", ".."])

        assert sorted(list(path_parts('tmp/foo/'))) == \
            sorted(["tmp/foo", "tmp"])

        assert list(path_parts('tmp/')) == ['tmp']
        assert list(path_parts('tmp')) == ['tmp']
        assert list(path_parts('tmp/foo')) == ['tmp/foo', 'tmp']
        assert list(path_parts('/')) == ['/']


if __name__ == '__main__':
    unittest.main()
