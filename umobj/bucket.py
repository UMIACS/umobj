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
