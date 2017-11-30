import logging

from boto.exception import S3ResponseError

log = logging.getLogger(__name__)


def delete_bucket(connection, bucket):
    '''
    Given a connection and a bucket name, delete the bucket, catching and
    logging any exceptions encountered in the process.
    '''
    log.info('Deleting bucket %s' % bucket)
    try:
        connection.delete_bucket(bucket)
    except S3ResponseError as e:
        if e.status == 409:
            log.error('Bucket %s is not empty and cannot be deleted' % bucket)
        else:
            log.error('Unable to delete bucket %s (%s: %s)' %
                      (bucket, e.status, e.reason))
    except:
        log.error('Unable to delete bucket %s' % bucket)


def set_website(connection, bucket, index='index.html', error=None):
    '''
    Given a connection and a bucket name, provision a bucket as an
    S3Website virtualhost. Optionally set the index and error pages.
    '''
    log.info('Adding S3 Website configuration for bucket %s' % bucket)
    try:
        b = connection.get_bucket(bucket)
    except S3ResponseError as e:
        if e.status == 404:
            log.error('Bucket %s could not be found.' % bucket)
            return False
        else:
            log.error('Unable to fetch bucket %s.' % bucket)
            return False

    try:
        b.configure_website(suffix=index, error_key=error)
    except S3ResponseError as e:
        log.error('Unable to set website %s.' % bucket)
        return False

    return True


def get_website(connection, bucket):
    '''
    Given a connection and a bucket name, get the s3 configuration of a bucket.
    '''
    log.info('Fetching S3 Website configuration for bucket %s' % bucket)
    try:
        b = connection.get_bucket(bucket)
    except S3ResponseError as e:
        if e.status == 404:
            log.error('Bucket %s could not be found.' % bucket)
            return None
        else:
            log.error('Unable to fetch bucket %s.' % bucket)
            return None

    try:
        ws_obj = b.get_website_configuration_obj()
    except S3ResponseError as e:
        if e.status == 404:
            return None
        else:
            log.error('Unable to fetch bucket %s website config.' % bucket)
            return None
    return ws_obj


def delete_website(connection, bucket):
    '''
    Given a connection and a bucket name, delete the s3 configuration of a
    bucket.
    '''
    log.info('Deleting S3 Website configuration for bucket %s' % bucket)
    try:
        b = connection.get_bucket(bucket)
    except S3ResponseError as e:
        if e.status == 404:
            log.error('Bucket %s could not be found.' % bucket)
            return False
        else:
            log.error('Unable to fetch bucket %s.' % bucket)
            return False
    try:
        b.delete_website_configuration()
    except S3ResponseError as e:
        log.error('Unable to delete website %s.' % bucket)
        return False

    return True
