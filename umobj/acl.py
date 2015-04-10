import logging

CANNED_ACLS = frozenset(['READ', 'WRITE', 'READ_ACP', 'WRITE_ACP',
                         'FULL_CONTROL'])
all_users = 'http://acs.amazonaws.com/groups/global/AllUsers'
auth_users = 'http://acs.amazonaws.com/groups/global/AuthenticatedUsers'

log = logging.getLogger(__name__)


def get_formatted_grants(grants):
    '''
    Return a list of formatted grant strings

    This will pair the grantee with the permission given to the grantee.  The
    grantee may be represented by id (e.g. liam) or by group grantees set forth
    by the Amazon S3 API such as AllUsers and AuthenticatedUsers.
    '''
    pairs = []
    for grant in grants:
        if grant.uri == all_users:
            grantee = "PUBLIC"
        elif grant.uri == auth_users:
            grantee = "AUTHENTICATED_USERS"
        else:
            grantee = grant.id
        pairs.append("%s:%s" % (grantee, grant.permission))
    return pairs


def get_formatted_grants_from_acl(acl):
    '''Return a grant list given an ACL'''
    return get_formatted_grants(acl.grants)


def get_formatted_grants_from_key(key):
    '''Return a grant list given a Key'''
    return get_formatted_grants(key.get_acl().acl.grants)


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


def make_private(object):
    '''Given a Bucket or a Key object, make it private by removing the
    AllUsers grant'''
    new_grants = []
    acl = object.get_acl()
    for g in acl.acl.grants:
        if g.uri == all_users:
            pass
        else:
            new_grants.append(g)
    acl.acl.grants = new_grants
    object.set_acl(acl)
