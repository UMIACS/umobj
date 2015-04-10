import logging
import bagit
from umobj.transfer import obj_key

log = logging.getLogger(__name__)


def get_bag_checksumming_algorithm(bucket_name, key_path):
    for algo in bagit.checksum_algos:
        manifest = obj_key(
            bucket_name, '%s/manifest-%s.txt' % (key_path, algo))
        if manifest is not None:
            return algo
    return None


def obj_checksums(bucket_name, key_path):
    for algo in bagit.checksum_algos:
        manifest = obj_key(
            bucket_name, '%s/manifest-%s.txt' %
            (key_path, algo))
        if manifest is not None:
            checksums = manifest.get_contents_as_string().strip()
            tagmanifest = obj_key(bucket_name, '%s/tagmanifest-%s.txt' %
                                  (key_path, algo))
            if tagmanifest is None:
                log.critical('Bag tag manifest is not found in object store.')
            else:
                checksums += '\n' + \
                    tagmanifest.get_contents_as_string().strip()
            log.debug('Retrieved %d checksums from object store.' %
                      len(checksums))
            return algo, checksums
    return None, None


def load_bag_checksums(bucket_name, key_path):
    obj_entries = {}
    algo, checksums = obj_checksums(bucket_name, key_path)
    for line in checksums.split('\n'):
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        entry = line.split(None, 1)
        obj_entries[entry[1]] = {}
        obj_entries[entry[1]][algo] = entry[0]
    return obj_entries
