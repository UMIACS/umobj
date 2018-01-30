#!/usr/bin/env python

import os
import string
import random
import unittest
import hashlib
import subprocess


def md5sum(filename, blocksize=65536):
    hasher = hashlib.md5()
    with open(filename, "r+b") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hasher.update(block)
    return hasher.hexdigest().replace('md5sum ', '')


class TestSkeleton(unittest.TestCase):

    def setUp(self):
        pass

    def test_multipart_upload_integrity(self):
        # create random file
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(56 * 1024 * 1024))
        md5_on_disk = md5sum('output_file')

        chars = string.ascii_lowercase
        bucket_name = ''.join(random.choice(chars) for x in range(20))

        # make a test bucket
        command = "../bin/mkobj %s" % bucket_name
        self.assertEqual(subprocess.call(command.split(' ')), 0)

        # upload file to object store
        command = "../bin/cpobj -m output_file %s:" % bucket_name
        self.assertEqual(subprocess.call(command.split(' ')), 0)

        # remove local file on disk once uploaded
        os.remove('output_file')

        # verify
        command = "../bin/cmpobj %s:output_file" % bucket_name
        self.assertEqual(subprocess.check_output(command.split(' ')).strip(),
                         md5_on_disk)

        # delete
        command = "../bin/rmobj -rf %s:" % bucket_name
        self.assertEqual(subprocess.call(command.split(' ')), 0)


if __name__ == '__main__':
    unittest.main()
