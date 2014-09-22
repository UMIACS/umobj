import logging
import os
import sys
import progressbar
import signal
from umobj.key import check_directory, create_directory, check_key_upload
from umobj.key import check_key_download
from umobj.utils import umobj_add_handler, walk_path, lremove
from umobj.multipart import MultiPart
from umobj.obj import Obj

log = logging.getLogger(__name__)
pbar = None


def transfer_stats(trans_bytes, total_bytes):
    try:
        pbar.update(trans_bytes)
    except AssertionError, e:
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
        key.set_contents_from_filename(filename)
        if progress:
            pbar.update(100)
            pbar.finish()
        return 0
    if progress:
        pbar = progressbar.ProgressBar(maxval=file_size)
        pbar.start()
    try:
        if progress:
            key.set_contents_from_filename(filename, cb=transfer_stats,
                                           num_cb=100)
        else:
            key.set_contents_from_filename(filename)
    except IOError, e:
        print e
        return 0
    if progress:
        pbar.finish()
    return file_size


def download_file(key, filename, progress=True):
    logging.info("Downloading to %s with %d bytes." % (filename, key.size))
    global pbar
    if key.size is 0:
        pbar = progressbar.ProgressBar(maxval=100)
        pbar.start()
        if filename.endswith('/'):
            if not os.path.isdir(filename):
                if os.path.isfile(filename.rstrip('/')):
                    logging.critical('%s already a file can not make directory')
                    sys.exit(1)
                logging.info("Creating directory %s" % filename)
                os.makedirs(filename)
            else:
                logging.info("Directory %s already exists, skipping." %
                             filename)
        else:
            key.get_contents_to_filename(filename)
        pbar.update(100)
        pbar.finish()
        return
    pbar = progressbar.ProgressBar(maxval=key.size)
    pbar.start()
    if os.path.isdir(filename):
        filename = filename + os.sep + os.path.basename(key.name)
    f = open(filename, 'w')
    key.get_contents_to_file(f, cb=transfer_stats, num_cb=100)
    f.close()
    pbar.finish()


def obj_key(bucket_name, key_name):
    '''Return a Key object given bucket_name and key_name'''
    bucket = Obj.conn.get_bucket(bucket_name)
    if bucket:
        return bucket.get_key(key_name)
    else:
        return None


def obj_download(bucket_name, dest, key_name, force=False, recursive=False,
                 multi=False, checksum=False):
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
                    download_file(key, filename)
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
            key = bucket.get_key(key_name)
            if key is None:
                logging.error("Key does not exist or if this is a prefix" +
                              " you need to specify recusive, %s" % key_name)
                return
            if checksum and not check_key_download(bucket, key.name, dest):
                return
            ## only multipart if we specify and the key is >5MB
            if multi and key.size > 5 * 1024 * 1024:
                logging.info("Downloading key %s (%d) to %s" %
                             (key, key.size, dest))
                m = MultiPart()
                m.start_download(bucket_name, key_name, dest)
            else:
                key = bucket.get_key(key_name)
                download_file(key, dest)


def obj_upload(bucket_name, src, dest_name, recursive=False, multi=False,
               checksum=False):
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
        prefix = src.split(os.sep)[-1]
        if dest_name:
            prefix = dest_name.rstrip(os.sep) + '/' + prefix
        for directory in walk_path(prefix):
            directory = directory + '/'
            if not check_directory(bucket, directory):
                create_directory(bucket, directory)
        operations = sum([len(files) for r, d, files in \
                         os.walk(src.rstrip(os.sep))])
        pbar = progressbar.ProgressBar(maxval=operations)
        pbar.start()
        count = 0
        for root, dirs, files in os.walk(src.rstrip(os.sep)):
            # we will not create the base directory
            if root != src:
                directory = '%s/%s/' % (prefix,
                                        lremove(src, root).lstrip(os.sep))
                if not check_directory(bucket, directory):
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
                    keyname = '%s/%s/%s' % (prefix,
                                            lremove(src, root).lstrip(os.sep),
                                            f)
                else:
                    keyname = '%s/%s' % (prefix, f)
                if checksum and not check_key_upload(bucket, keyname, filename):
                    continue
                logging.info("Upload key %s from file %s" %
                             (keyname, filename))
                if (multi and size > 0) or (size > (1024*1024*1024)):
                    m = MultiPart()
                    m.start_upload(bucket_name, keyname, filename, policy)
                else:
                    key = bucket.new_key(keyname)
                    res = upload_file(key, filename, progress=False)
                    if res >= 0:
                        logging.debug("Applying bucket policy %s" % policy)
                        key.set_acl(policy)
                count += 1
                if count < operations:
                    pbar.update(count)
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
            for dir_part in dest_name.lstrip(os.sep).split(os.sep):
                current_path = current_path + dir_part + '/'
                create_directory(bucket, current_path)
                key_name = current_path + os.path.basename(src)
        else:
            key_name = os.path.basename(src)
        if checksum and not check_key_upload(bucket, key_name, src):
            return
        if multi or (size > (1024*1024*1024)):
            logging.info("Starting a multipart upload.")
            m = MultiPart()
            m.start_upload(bucket_name, key_name, src, policy)
        else:
            key = bucket.new_key(key_name)
            res = upload_file(key, src)
            if res >= 0:
                logging.debug("Applying bucket policy %s" % policy)
                key.set_acl(policy)
