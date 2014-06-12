import threading
import Queue
import logging
import mimetypes
import os
import time
import math
from filechunkio import FileChunkIO
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat
from umobj.obj import Obj
import progressbar


class UploadThread(threading.Thread):
    def __init__(self, mp, queue):
        threading.Thread.__init__(self)
        self.mp = mp
        self.queue = queue
        self.obj = self.mp.connect()

    def run(self):
        while not self.queue.empty():
            part_num, offset, bytes = self.queue.get()
            logging.info('%s : Starting part %d on offset %d with %d bytes.' %
                         (self.mp.mp_id, part_num, offset, bytes))
            self._upload_part(part_num, offset, bytes)
            self.queue.task_done()

    def _upload_part(self, part_num, offset, bytes, retries=10):
        try:
            bucket = self.obj.get_bucket(self.mp.bucketname)
            for mp in bucket.get_all_multipart_uploads():
                if mp.id == self.mp.mp_id:
                    logging.debug('%s : Uploading chunk (%d retries left) %s' %
                                  (self.mp.mp_id, retries, part_num))
                    with FileChunkIO(self.mp.filename, 'r', offset=offset,
                                     bytes=bytes) as fp:
                        mp.upload_part_from_file(fp=fp, part_num=part_num)
                        break
        except Exception, exc:
            print exc
            if retries:
                logging.info('%s : retrying with %d retries left' % retries-1)
                self._upload_part(part_num, offset,
                                  bytes, retries=retries-1)
            else:
                logging.error('%s : Failed uploading part %d' %
                              (self.mp.mp_id, part_num))
                raise exc
        else:
            logging.info('%s : Uploaded part %d' % (self.mp.mp_id, part_num))


class DownloadThread(threading.Thread):
    def __init__(self, mp, queue):
        threading.Thread.__init__(self)
        self.mp = mp
        self.queue = queue
        self.obj = self.mp.connect()

    def run(self):
        while not self.queue.empty():
            start_byte, end_byte = self.queue.get(True, 2)
            logging.info('Starting downloading bytes %d - %d.' %
                         (self.mp.mp_id, start_byte, end_byte))
            self._download_part(start_byte, end_byte)
            self.queue.task_done()

    def _download_part(self, start_byte, end_byte):
        try:
            key_range = self.obj.make_request(
                'GET',
                bucket=self.mp.bucketname,
                key=self.mp.keyname,
                headers={'Range': "bytes=%d-%d" % (start_byte, end_byte)})
            filename = self.mp.filename
            fd = os.open(filename, os.O_WRONLY)
            logging.debug("Opening file descriptor %d, seeking to %d" %
                         (fd, start_byte))
            os.lseek(fd, start_byte, os.SEEK_SET)
            chunk_size = min((end_byte-start_byte), 32 * 1024 * 1024)
            while True:
                data = key_range.read(chunk_size)
                if data == "":
                    break
                os.write(fd, data)
        except Exception, exc:
            print exc


class MultiPart:

    ### code adapted from https://gist.github.com/fabiant7t/924094
    def __init__(self):
        self.mp_id = None
        self.bucketname = None
        self.filename = None
        self.keyname = None

    def connect(self):
        return Obj.conn

    def start_download(self, bucketname, keyname, filename, threads=4):
        logging.info("Starting a multipart download for bucket %s and key %s" %
                     (bucketname, keyname))
        self.bucketname = bucketname
        if os.path.isdir(filename):
            self.filename = filename + os.sep + os.path.basename(keyname)
        else:
            self.filename = filename
        self.keyname = keyname
        obj = self.connect()
        bucket = obj.get_bucket(self.bucketname)
        key = bucket.get_key(keyname)
        size = key.size
        # create the file
        fd = os.open(self.filename, os.O_CREAT)
        os.close(fd)
        bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(size)),
                              5242880)
        chunk_amount = int(math.ceil(size / float(bytes_per_chunk)))
        logging.info("%s : Size: %16d   " % (self.keyname, size) +
                     "Chunk Size: %16d   " % bytes_per_chunk +
                     "Number Chunks: %8d" % chunk_amount)
        queue = Queue.Queue()
        for i in range(chunk_amount):
            offset = i * bytes_per_chunk
            remaining_bytes = size - offset
            bytes = min([bytes_per_chunk, remaining_bytes])
            queue.put((offset, offset + bytes - 1))
        for i in range(threads):
            t = DownloadThread(self, queue)
            t.setDaemon(True)
            t.start()
        queue.join()

    def start_upload(self, bucketname, keyname, filename, policy, threads=4):
        self.bucketname = bucketname
        self.filename = filename
        headers = {}
        obj = self.connect()
        bucket = obj.get_bucket(self.bucketname)
        mtype = mimetypes.guess_type(keyname)[0] or 'application/octet-stream'
        headers.update({'Content-Type': mtype})
        mp = bucket.initiate_multipart_upload(keyname, headers=headers)
        self.mp_id = mp.id
        logging.info("%s: Starting a multipart upload for %s" %
                     (mp.id, filename))
        source_size = os.stat(filename).st_size
        bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(source_size)),
                              5242880)
        chunk_amount = int(math.ceil(source_size / float(bytes_per_chunk)))
        logging.info("%s : Size: %16d   " % (mp.id, source_size) +
                     "Chunk Size: %16d   " % bytes_per_chunk +
                     "Number Chunks: %8d" % chunk_amount)
        queue = Queue.Queue()
        logging.info("%s : Starting a pool with %d threads." %
                     (mp.id, threads))

        ### putting all the tasks together in a queue
        for i in range(chunk_amount):
            offset = i * bytes_per_chunk
            remaining_bytes = source_size - offset
            bytes = min([bytes_per_chunk, remaining_bytes])
            part_num = i + 1
            queue.put((part_num, offset, bytes))

        for i in range(threads):
            t = UploadThread(self, queue)
            t.setDaemon(True)
            t.start()

        pbar = progressbar.ProgressBar(maxval=chunk_amount)
        pbar.start()
        while not queue.empty():
            pbar.update(chunk_amount - queue.qsize())
            time.sleep(1)
        pbar.finish()
        queue.join()

        if len(mp.get_all_parts()) == chunk_amount:
            mp.complete_upload()
            key = bucket.get_key(keyname)
            logging.debug("%s : Applying bucket policy %s" % (mp.id, policy))
            key.set_acl(policy)
        else:
            logging.warning("%s : Canceling mulitpart upload." % mp.id)
            mp.cancel_upload()
