import threading
import Queue
import logging
import mimetypes
import os
import time
import math
from StringIO import StringIO
from filechunkio import FileChunkIO
from umobj.obj import Obj
import progressbar


class MultiPartStream():


    def __init__(self):
        self.mp_id = None
        self.bucketname = None
        self.stream = None
        self.keyname = None

    def start_upload(self, bucketname, keyname, stream, policy, threads=4):
        self.bucketname = bucketname
        # TODO this should be the stream
        self.stream = stream
        headers = {}
        obj = self.connect()
        bucket = obj.get_bucket(self.bucketname)
        mtype = mimetypes.guess_type(keyname)[0] or 'application/octet-stream'
        headers.update({'Content-Type': mtype})
        mp = bucket.initiate_multipart_upload(keyname, headers=headers)
        self.mp_id = mp.id
#        logging.info("%s: Starting a multipart upload for %s" %
#                     (mp.id, filename))
        #source_size = os.stat(filename).st_size
        #bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(source_size)),
        #                      5242880)
        bytes_per_chunk = (1024*1024*10)
        #chunk_amount = int(math.ceil(source_size / float(bytes_per_chunk)))
        logging.info("Chunk Size: %16d   " % bytes_per_chunk)
        queue = Queue.Queue()

        # TODO need to figure out how to break up chunks among threads without 
        # knowing the size ahead of time
        logging.info("%s : Starting a pool with %d threads." %
                     (mp.id, threads))

        # read bytes from data stream and upload in parts 
        bytes_in = stream.read(bytes_per_chunk)
        part_num = 1
        while(bytes_in):
            mp.upload_part_from_file(StringIO(bytes_in), part_num=part_num)
            part_num += 1
            bytes_in = stream.read(bytes_per_chunk)
        
        if not stream.read(1):
            mp.complete_upload()
            key = bucket.get_key(keyname)
            logging.debug("%s : Applying bucket policy %s" % (mp.id, policy))
            key.set_acl(policy)
        else:
            logging.warning("%s : Canceling mulitpart upload." % mp.id)
            mp.cancel_upload()
        # putting all the tasks together in a queue
#        for i in range(chunk_amount):
#            offset = i * bytes_per_chunk
#            remaining_bytes = source_size - offset
#            bytes = min([bytes_per_chunk, remaining_bytes])
#            part_num = i + 1
#            queue.put((part_num, offset, bytes))
#
#        for i in range(threads):
#            t = UploadThread(self, queue)
#            t.setDaemon(True)
#            t.start()
#
#        #pbar = progressbar.ProgressBar(maxval=chunk_amount)
#        pbar = progressbar.ProgressBar()
#        pbar.start()
#        while not queue.empty():
#            pbar.update(chunk_amount - queue.qsize())
#            time.sleep(1)
#        pbar.finish()
#        queue.join()

