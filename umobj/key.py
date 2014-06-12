import logging
from pytz import utc
from datetime import datetime

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


def check_key_upload(bucket, key_name, file_st):
    '''Given a key_name and a os.stat() output decide
       to update the key in the object store'''
    key = bucket.get_key(key_name)
    if key is not None:
        if key.size == file_st.st_size:
            try:
                key_mod_dt = utc.localize(datetime.strptime(key.last_modified,
                                          '%a, %d %b %Y %H:%M:%S %Z'))
            except ValueError:
                return True
            log.debug('Key modified date : %s' % key_mod_dt)
            print file_st.st_mtime
            file_mod_dt = utc.localize(datetime.fromtimestamp(file_st.st_mtime))
            log.debug('File modified date : %s' % file_mod_dt)
            if key_mod_dt > file_mod_dt:
                log.info('No update required %s:%s' % (bucket.name,
                                                           key_name))
                return False
    return True
