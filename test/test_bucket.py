#!/usr/bin/env python

import logging
import os
import string
import unittest
import six.moves.urllib.request
import six.moves.urllib.error
import six.moves.urllib.parse
import random

from boto.s3.connection import S3Connection

from umobj.bucket import set_website, get_website, delete_website
from six.moves import range

log = logging.getLogger(__name__)


class TestBucket(unittest.TestCase):

    @staticmethod
    def gen_bucket_name():
        chars = string.ascii_lowercase
        return ''.join(random.choice(chars) for x in range(20))

    def setUp(self, host=None, port=443, is_secure=True,
              access_key=None, secret_key=None, vhost_domain=None):
        if host is None:
            try:
                host = os.environ['OBJ_SERVER']
            except KeyError:
                host = 'obj.umiacs.umd.edu'
        if port is None:
            if is_secure:
                port = 443
            else:
                port = 80
        if access_key is None:
            try:
                access_key = os.environ['OBJ_ACCESS_KEY_ID']
            except KeyError:
                log.error("Please provide access_key")
                return False
        if secret_key is None:
            try:
                secret_key = os.environ['OBJ_SECRET_ACCESS_KEY']
            except KeyError:
                log.error("Please provide secret_key")
                return False
        self.conn = S3Connection(host=host, port=port,
                                 is_secure=is_secure,
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key)
        if vhost_domain is None:
            try:
                self.vhost_domain = os.environ['VHOST_DOMAIN']
            except KeyError:
                self.vhost_domain = 'umiacs.io'
        self.port = port
        self.is_secure = is_secure

    def test_website(self):
        bucket_name = self.gen_bucket_name()
        bucket = self.conn.create_bucket(bucket_name)
        assert bucket is not None, 'Failed to create bucket'

        # Attempt to set website.
        index = bucket.new_key('index.html')
        error = bucket.new_key('error.html')
        index.set_contents_from_string('Hello World!')
        error.set_contents_from_string('Error')
        index.make_public()
        error.make_public()
        assert set_website(
            self.conn,
            bucket_name,
            index='index.html',
            error='error.html'
            )

        url = ''
        if self.is_secure:
            url += 'https://'
        else:
            url += 'http://'
        url += '%s.%s' % (bucket_name, self.vhost_domain)
        if self.port not in [80, 443]:
            url += ':%d' % self.port

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url)
            content = res.read().decode()
        except Exception as e:
            self.fail('Could not read from bucket site: %s' % str(e))

        assert content == 'Hello World!', 'Did not find correct index content.'

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url + '/no_page')
            content = res.read()
        except six.moves.urllib.error.HTTPError as e:
            res = e.fp.read().decode()
            assert res == 'Error', 'Error page not set.'
        except Exception as e:
            self.fail('Could not read from bucket site: %s' % str(e))

        # Try to get the config
        config = get_website(self.conn, bucket_name)
        assert config is not None, 'Failed to retrieve config'

        # Try to destroy
        assert delete_website(self.conn, bucket_name), 'Failed to destroy website.'

        res = None
        try:
            res = six.moves.urllib.request.urlopen(url)
            self.fail('Website still returned on root of domain after delete.')
        except six.moves.urllib.error.HTTPError as e:
            assert e.code == 404, 'Website did not 404 on root of domain after delete'
        except Exception as e:
            self.fail('Invalid error reading from site: %s' % str(e))

        index.delete()
        error.delete()
        self.conn.delete_bucket(bucket_name)


if __name__ == '__main__':
    unittest.main()
