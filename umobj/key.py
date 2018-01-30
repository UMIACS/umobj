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
        policy = bucket.get_acl()
        policy.owner = dir_key.get_acl().owner
        dir_key.set_acl(policy)
        log.debug("Applied bucket policy %s" % policy)
    except IOError as e:
        print e
        return False
    return True


def is_directory(bucket, path):
    '''
    Return True if the path given is a directory.

    The existence check goes something like this:
        0) for key under consideration foo/bar/
        1) if a zero-length key exists for "foo/bar/", then True.
        2) if a bucket listing with prefix "foo/bar/" returns one or more
           objects, then True.
        3) else False.
    '''
    if not path.endswith('/'):
        path = path + '/'
    for key in bucket.list(prefix=path):
        return True
    return False


def directory_file_exists(bucket, directory):
    '''
    Given a S3 bucket object and a directory path check to see if the directory
    exists in the S3 bucket.

    In order for the directory to exist, there must be a zero-length key with
    that name present.  Some S3 clients do not put this file in place to
    represent the directory, but we do.
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
        log.info('Key does not exist, need to upload.')
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


def key_exists(bucket, key):
    '''Given a bucket and a key name, return True if the key exists.'''
    return bucket.get_key(key) is not None


def delete_key(bucket, key, check_exists=False):
    '''
    Given a boto bucket and a string naming the key to delete, attempt to
    delete, catching any exceptions that may occur.

    Return True if delete was successful; False otherwise.
    '''
    log.info('Deleting key %s' % key)
    try:
        if check_exists:
            if not key_exists(bucket, key):
                return False
        bucket.delete_key(key)
        return True
    except S3ResponseError as e:
        log.error('Unable to delete %s:%s (Reason: %s)' %
                  (bucket.name, key, e.reason))
        return False
    except:
        log.error('Unable to delete %s:%s' % (bucket.name, key))
        return False
