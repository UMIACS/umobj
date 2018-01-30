import logging
import os
import sys
import progressbar
import signal
from umobj.key import directory_file_exists, create_directory, check_key_upload
from umobj.key import check_key_download
from umobj.utils import umobj_add_handler, walk_path, lremove
from umobj.multipart import MultiPart, MultiPartStream
from umobj.obj import Obj
from boto.exception import S3ResponseError

log = logging.getLogger(__name__)
pbar = None


def transfer_stats(trans_bytes, total_bytes):
    try:
        pbar.update(trans_bytes)
    except AssertionError as e:
        print e


def upload_file(key, filename, progress=True):
    global pbar
    if os.path.islink(filename):
        logging.warning('Skipping %s, symlink.' % filename)
        return -1
    if not os.path.isfile(filename):
        logging.warning('Skipping %s, unknown file type.' % filename)
        return -1
    file_size = os.stat(filename).st_size
    logging.info("Uploading %s with %d bytes." % (filename, file_size))
    if file_size is 0:
        if progress:
            pbar = progressbar.ProgressBar(maxval=100)
            pbar.start()
        try:
            key.set_contents_from_filename(filename)
        except S3ResponseError as e:
                logging.critical('%d %s: %s' % (e.status, e.reason, e.error_code))
                sys.exit(1) 
        if progress:
            pbar.update(100)
            pbar.finish()
        return 0
    if progress:
        pbar = progressbar.ProgressBar(maxval=file_size)
        pbar.start()
    try:
        if progress:
            try:
                key.set_contents_from_filename(filename, cb=transfer_stats,
                                               num_cb=100)
            except S3ResponseError as e:
                logging.critical('%d %s: %s' % (e.status, e.reason, e.error_code))
                sys.exit(1)
        else:
            try:
                key.set_contents_from_filename(filename)
            except S3ResponseError as e:
                logging.critical('%d %s: %s' % (e.status, e.reason, e.error_code))
                sys.exit(1)
    except IOError as e:
        print e
        return 0
    if progress:
        pbar.finish()
    return file_size


def _create_needed_parent_directories(filename):
    '''
    Given a filename, create all the parent directories needed to write
    the file if the parent directory does not exist already.

    Given /foo/bar/baz.txt, this method will check if /foo/bar/ exists
    and create it if it does not.
    '''
    if not os.path.exists(os.path.dirname(filename)) and os.path.dirname(filename) != '':
        logging.info('Recursively creating needed directory structure for %s' %
                     filename)
        os.makedirs(os.path.dirname(filename))


def download_file(key, filename, progress=True):
    logging.info("Downloading to %s with %d bytes." % (filename, key.size))
    global pbar
    if key.size is 0:
        if progress:
            pbar = progressbar.ProgressBar(maxval=100)
            pbar.start()
        if filename.endswith('/'):
            if not os.path.isdir(filename):
                if os.path.isfile(filename.rstrip('/')):
                    logging.critical(
                        '%s already a file can not make directory')
                    sys.exit(1)
                logging.info("Creating directory %s" % filename)
                os.makedirs(filename)
            else:
                logging.info("Directory %s already exists, skipping." %
                             filename)
        else:
            _create_needed_parent_directories(filename)
            key.get_contents_to_filename(filename)
        if progress:
            pbar.update(100)
            pbar.finish()
        return
    if os.path.isdir(filename):
        filename = filename + os.sep + os.path.basename(key.name)
    _create_needed_parent_directories(filename)
    f = open(filename, 'w')
    if progress:
        pbar = progressbar.ProgressBar(maxval=key.size)
        pbar.start()
        key.get_contents_to_file(f, cb=transfer_stats, num_cb=100)
    else:
        key.get_contents_to_file(f)
    f.close()
    if progress:
        pbar.finish()


def obj_key(bucket_name, key_name):
    '''Return a Key object given bucket_name and key_name'''
    bucket = Obj.conn.get_bucket(bucket_name)
    if bucket:
        return bucket.get_key(key_name)
    else:
        return None


def obj_download(bucket_name, dest, key_name, force=False, recursive=False,
                 multi=False, checksum=False, progress=True):
    bucket = Obj.conn.get_bucket(bucket_name)
    if recursive:
        logging.info("Starting recursive download %s to %s prefix %s" %
                     (bucket.name, dest, key_name))
        if not os.path.isdir(dest):
            logging.error("DEST %s is not a directory." % dest)
            return
        else:
            for key in bucket.list(prefix=key_name):
                filename = dest.rstrip(os.sep) + os.sep + key.name
                if not check_key_download(bucket, key.name, filename):
                    continue
                logging.info("Downloading key %s (%d) to %s" %
                             (key, key.size, filename))
                if multi and key.size > 5 * 1024 * 1024:
                    m = MultiPart()
                    m.start_download(bucket_name, key.name, dest)
                else:
                    download_file(key, filename, progress=progress)
    else:
        if not key_name:
            logging.error("Must specify a key to download or use " +
                          "recusive option")
            return
        if os.path.isfile(dest) and not force:
            logging.error("File %s already exists " % dest +
                          "please force flag to overwrite.")
            return
        else:
            key_name = key_name.rstrip(os.path.sep)
            key = bucket.get_key(key_name)
            if key is None:
                logging.error("Key does not exist or if this is a prefix" +
                              " you need to specify recusive, %s" % key_name)
                return
            if checksum and not check_key_download(bucket, key.name, dest):
                return
            # only multipart if we specify and the key is >5MB
            if multi and key.size > 5 * 1024 * 1024:
                logging.info("Downloading key %s (%d) to %s" %
                             (key, key.size, dest))
                m = MultiPart()
                m.start_download(bucket_name, key_name, dest)
            else:
                key = bucket.get_key(key_name)
                download_file(key, dest)


def obj_upload(bucket_name, src, dest_name, recursive=False, multi=False,
               checksum=False, progress=True, respect_trailing_sep=False):

    if src == '.' or (respect_trailing_sep and src.endswith(os.sep)):
        end_sep = True
    else:
        end_sep = False

    # retranslate to the full absolute path
    src = os.path.abspath(src)
    # retieve the bucket
    bucket = Obj.conn.get_bucket(bucket_name)
    try:
        size = os.stat(src).st_size
    except OSError as e:
        logging.error(e)
        return
    policy = bucket.get_acl()

    # use a closure to capture the current bucket
    def cancel_multipart_handler(signal, frame):
        for upload in bucket.get_all_multipart_uploads():
            upload.cancel_upload()
            logging.info("Removed incomplete multipart upload: %s" %
                         str(upload))

    umobj_add_handler(signal.SIGINT, cancel_multipart_handler)

    if recursive and os.path.isdir(src):
        prefix = None
        if not end_sep:
            prefix = src.split(os.sep)[-1]
        if dest_name:
            if prefix:
                prefix = dest_name.rstrip(os.sep) + '/' + prefix
            else:
                prefix = dest_name.rstrip(os.sep) + '/'
        if prefix:
            for directory in walk_path(prefix):
                directory = directory + '/'
                if not directory_file_exists(bucket, directory):
                    create_directory(bucket, directory)
        operations = sum([len(files) for r, d, files in
                          os.walk(src.rstrip(os.sep))])
        if operations < 1:
            # we can not start a progress bar with less than 1 operation
            progress = False
        if progress:
            pbar = progressbar.ProgressBar(maxval=operations)
            pbar.start()
        count = 0
        for root, dirs, files in os.walk(src.rstrip(os.sep)):
            # we will not create the base directory
            if root != src:
                if prefix:
                    directory = '%s/%s/' % (prefix,
                                            lremove(src, root).lstrip(os.sep))
                else:
                    directory = '%s/' % (lremove(src, root).lstrip(os.sep))
                if not directory_file_exists(bucket, directory):
                    create_directory(bucket, directory)
                    count += 1
                    if count < operations:
                        pbar.update(count)
            for f in files:
                filename = root + os.sep + f
                try:
                    file_st = os.stat(filename)
                    size = file_st.st_size
                except OSError as e:
                    logging.error(e)
                    continue
                if root != src:
                    if prefix:
                        keyname = ('%s/%s/%s' %
                                   (prefix,
                                    lremove(src, root).lstrip(os.sep),
                                    f))
                    else:
                        keyname = ('%s/%s' %
                                   (lremove(src, root).lstrip(os.sep), f))
                else:
                    if prefix:
                        keyname = '%s/%s' % (prefix, f)
                    else:
                        keyname = '%s' % f

                if checksum and not check_key_upload(
                        bucket, keyname, filename):
                    continue
                logging.info("Upload key %s from file %s" %
                             (keyname, filename))
                if (multi and size > 0) or (size > (1024 * 1024 * 1024)):
                    m = MultiPart()
                    m.start_upload(bucket_name, keyname, filename, policy)
                else:
                    key = bucket.new_key(keyname)
                    res = upload_file(key, filename, progress=False)
                    if res >= 0:
                        logging.debug("Applying bucket policy %s" % policy)
                        ## set the owner of the policy to the upload user
                        policy.owner = key.get_acl().owner
                        key.set_acl(policy)
                count += 1
                if count < operations and progress:
                    pbar.update(count)
        if progress:
            pbar.finish()
    else:
        if os.path.isdir(src):
            logging.warning("Skipping directory %s, " % src +
                            "use the recursive option.")
            return
        if not os.path.isfile(src):
            logging.error("File %s does not exist." % src)
            return
        if dest_name:
            current_path = ''
            for dir_part in dest_name.lstrip(os.sep).split(os.sep)[:-1]:
                current_path = current_path + dir_part + '/'
                create_directory(bucket, current_path)
            if dest_name.endswith('/'):
                key_name = current_path + os.path.basename(src)
            else:
                key_name = dest_name
        else:
            key_name = os.path.basename(src)
        if checksum and not check_key_upload(bucket, key_name, src):
            return
        if multi or (size > (1024 * 1024 * 1024)):
            logging.info("Starting a multipart upload.")
            m = MultiPart()
            m.start_upload(bucket_name, key_name, src, policy)
        else:
            key = bucket.new_key(key_name)
            res = upload_file(key, src)
            if res >= 0:
                logging.debug("Applying bucket policy %s" % policy)
                ## set the owner of the policy to the upload user
                policy.owner = key.get_acl().owner
                key.set_acl(policy)


def obj_stream(bucket_name, src, dest_name, filename):
    bucket = Obj.conn.get_bucket(bucket_name)
    policy = bucket.get_acl()
    if dest_name:
        current_path = ''
        for dir_part in dest_name.lstrip(os.sep).split(os.sep):
            current_path = current_path + dir_part + '/'
            create_directory(bucket, current_path)
            key_name = current_path + filename
    else:
        key_name = filename
    # always multipart since total size of stream is unknown
    logging.info("Starting a multipart upload using stream.")
    m = MultiPartStream()
    m.start_upload(bucket_name, key_name, src, policy)
