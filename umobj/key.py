import logging

from umobj.md5 import compute_key_md5, compute_file_md5

log = logging.getLogger(__name__)


def create_directory(bucket, directory):
    """
        Create a directry (key will always end in a /)
    """
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
    except IOError, e:
        print e
        return False
    return True


def check_directory(bucket, directory):
    """
        Given a S3 bucket object and a directory path check to see
        if the directory exists in the S3 bucket.
    """
    key = bucket.get_key(directory)
    if key is not None and key.size == 0 and key.name.endswith('/'):
        return True
    else:
        return False



def check_key_upload(bucket, key_name, filename):
    '''Given a bucket, key_name and the filename locally check for update
       via MD5 sum'''
    key = bucket.get_key(key_name)
    if key is not None:
        file_md5 = compute_file_md5(filename)
        etag = key.etag.strip('\"')
        log.debug('Etag %s' % etag)
        if '-' in etag:
            ## multipart upload need to read all data and compute
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
