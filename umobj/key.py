import os
import logging

from boto.exception import S3ResponseError

from umobj.md5 import compute_key_md5, compute_file_md5
from umobj.utils import parse_key_value_pair

log = logging.getLogger(__name__)


def create_directory(bucket, directory):
    '''Create a directry (key will always end in a /)'''
    if not directory.endswith('/'):
        directory += '/'
    log.info("Create directory %s" % directory)
    dir_key = bucket.new_key(directory)
    try:
        dir_key.set_contents_from_string('')
        log.info("Created directory %s" % directory)
        acl = bucket.get_acl()
        dir_key.set_acl(bucket.get_acl())
        log.debug("Applied bucket policy %s" % acl)
    except IOError as e:
        print e
        return False
    return True


def check_directory(bucket, directory):
    '''
    Given a S3 bucket object and a directory path check to see if the directory
    exists in the S3 bucket.
    '''
    key = bucket.get_key(directory)
    if key is not None and key.size == 0 and key.name.endswith('/'):
        return True
    else:
        return False


def check_key_upload(bucket, key_name, filename):
    '''
    Given a bucket, key_name and a local filename, check for MD5 sum match
    '''
    key = bucket.get_key(key_name)
    if key is not None:
        file_md5 = compute_file_md5(filename)
        etag = key.etag.strip('\"')
        log.debug('Etag %s' % etag)
        if '-' in etag:
            # multipart upload need to read all data and compute
            log.info('Computing MD5 of %s:%s' % (bucket.name, key_name))
            key_md5 = compute_key_md5(bucket, key_name)
        else:
            key_md5 = etag
        log.info('Key %s:%s has MD5 %s' % (bucket.name, key_name,
                                           key_md5))
        if file_md5 != key_md5:
            log.info('File MD5 %s != Key MD5 %s' % (file_md5, key_md5))
            return True
        else:
            return False
    else:
        log.info('Key doet not exist, need to upload.')
        return True


def check_key_download(bucket, key_name, filename):
    '''
    Given a bucket, key_name and the filename check to see if we need to
    update via the MD5 sum
    '''
    if os.path.exists(filename):
        if key_name.endswith('/') and os.path.isdir(filename):
            log.info('Directory already exists %s' % filename)
            return False
        key = bucket.get_key(key_name)
        file_md5 = compute_file_md5(filename)
        if key is not None:
            etag = key.etag.strip('\"')
            log.debug('Etag %s' % etag)
            if '-' in etag:
                # multipart upload need to read all data and compute
                log.info('Computing MD5 of %s:%s' % (bucket.name, key_name))
                key_md5 = compute_key_md5(bucket, key_name)
            else:
                key_md5 = etag
            log.info('Key %s:%s has MD5 %s' % (bucket.name, key_name,
                                               key_md5))
            if file_md5 != key_md5:
                log.info('File MD5 %s != Key MD5 %s' % (file_md5, key_md5))
                return True
            else:
                return False
        else:
            log.error('Key does not exist %s:%s' % (bucket.name, key_name))
            return True
    else:
        log.info('File does not exist, download required.')
        return True


def get_metadata(bucket, key_name):
    '''
    Return a dictionary of all metadata on the given key

    bucket      The bucket (boto) object
    key_name    The name of the key
    '''
    return bucket.get_key(key_name).metadata


def set_metadata(bucket, key_name, metadata):
    '''
    Set the metadata on the given key.

    This will not merge the metadata passed in with the existing metadata.
    This will completely overwrite the metadata.

    S3 makes it currently not possible to update metadata for an existing key,
    so the only way to update metadata is through a copy operation.
    '''
    object = bucket.get_key(key_name)
    object.copy(bucket.name, key_name, metadata, preserve_acl=True)


def add_metadata(bucket, key_name, key, val):
    '''Add {key: val} to the metadata for the given key'''
    log.info(
        'Adding metadata %s=%s to %s:%s' %
        (key, val, bucket.name, key_name))
    metadata = get_metadata(bucket, key_name)
    metadata[key] = val
    set_metadata(bucket, key_name, metadata)


def remove_metadata_by_key(bucket, key_name, key):
    '''Remove the metadata key-value pair by key.'''
    log.info(
        'Removing metadata key %s from %s:%s' %
        (key, bucket.name, key_name))
    metadata = get_metadata(bucket, key_name)
    try:
        del metadata[key]
        set_metadata(bucket, key_name, metadata)
    except KeyError:
        pass


def remove_metadata_by_key_value_pair(bucket, key_name, key_value_string):
    '''
    Remove a selected piece of metadata from the key's metadata dict

    key_value_string can be of the form "mykey=myval" or just "mykey"
    '''
    k, v = parse_key_value_pair(key_value_string)
    remove_metadata_by_key(bucket, key_name, k)


def delete_key(bucket, key):
    '''
    Given a boto bucket and a string naming the key to delete, attempt to
    delete, catching any exceptions that may occur.
    '''
    log.info('Deleting key %s' % key)
    try:
        return bucket.delete_key(key)
    except S3ResponseError as e:
        log.error('Unable to delete %s:%s (Reason: %s)' %
                  (bucket.name, key, e.reason))
    except:
        log.error('Unable to delete %s:%s' % (bucket.name, key))
