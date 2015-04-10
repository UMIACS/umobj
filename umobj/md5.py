import logging
import math
import hashlib
from umobj.obj import Obj

log = logging.getLogger(__name__)


def compute_file_md5(filename, block_size=2 ** 20):
    log.info('Computing MD5 hash on %s' % filename)
    f = open(filename)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    digest = md5.hexdigest()
    log.info('File %s has MD5 %s' % (filename, digest))
    return digest


def compute_key_md5(bucket, key_name):
    key = bucket.get_key(key_name)
    if key is None:
        logging.error("Key %s does not exist in bucket %s" %
                      (key_name, bucket.name))
        return None

    md5 = hashlib.md5()
    size = key.size
    if size != 0:
        # pbar = progressbar.ProgressBar(maxval=size)
        bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(size)),
                              5242880)
        chunk_amount = int(math.ceil(size / float(bytes_per_chunk)))
        log.debug("MD5 Total Bytes: %d " % size +
                  "Bytes/Chunk : %d " % bytes_per_chunk +
                  "Chunks : %d" % chunk_amount)
        # pbar.start()
        for i in range(chunk_amount):
            offset = i * bytes_per_chunk
            remaining_bytes = size - offset
            bytes = min([bytes_per_chunk, remaining_bytes])
            start_byte = offset
            end_byte = offset + bytes - 1
            log.debug("MD5 Processing bytes %d - %d" % (start_byte, end_byte))
            key_range = Obj.conn.make_request('GET',
                                              bucket=bucket.name,
                                              key=key_name,
                                              headers={'Range': "bytes=%d-%d" %
                                                       (start_byte, end_byte)})
            chunk_size = min((end_byte - start_byte), 32 * 1024 * 1024)
            while True:
                data = key_range.read(chunk_size)
                if data == "":
                    break
                md5.update(data)
                # pbar.update(end_byte)
        # pbar.finish()
    return md5.hexdigest()
