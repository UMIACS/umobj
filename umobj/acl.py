import logging

CANNED_ACLS = frozenset(['READ', 'WRITE', 'READ_ACP', 'WRITE_ACP',
                         'FULL_CONTROL'])
all_users = 'http://acs.amazonaws.com/groups/global/AllUsers'

log = logging.getLogger(__name__)

def acl_pairs(acl):
    pairs = []
    for grant in acl.grants:
        pairs.append('%s:%s' % (grant.id, grant.permission))
    return pairs

def split_acl(s):
    '''Return a user and CANNED_ACL split from a string'''
    parts = s.split(':', 1)
    if len(parts) != 2:
        log.warning('ACL malformed %s' % s)
        return None, None
    if parts[1] not in CANNED_ACLS:
        log.warning('Canned ACL %s not valid' % parts[1])
        return None, None
    else:
        return parts[0], parts[1]
