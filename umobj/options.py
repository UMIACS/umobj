import umobj
from argparse import ArgumentParser, RawDescriptionHelpFormatter

epilog = '''  ACCESS_KEY  - Your Access Key ID.  If not supplied, will use
                the value of the environment variable OBJ_ACCESS_KEY_ID.
  SECRET_KEY  - Your Secret Access Key.  If not supplied, will use the value
                of the environment variable OBJ_SECRET_ACCESS_KEY.
  HOST        - The object storage server you want to connect to.  This can
                be overridden by the OBJ_SERVER environment variable.
'''


class umobj_parser(object):
    def __init__(self, usage=None, description=None, description_epilog=None):
        description = '\n\n' + epilog
        if description_epilog is not None:
            description += description_epilog
        self.parser = ArgumentParser(usage=usage,
                                     description=description,
                                     add_help=False,
                                     formatter_class=\
                                     RawDescriptionHelpFormatter)
        self.parser._positionals.title = 'Positional Arguments'
        self.parser._optionals.title = 'Optional Arguments'
        self.parser.add_argument('-h', '--help', action='help',
                                 help='Show this help and exit')
        self.parser.add_argument('--version', action='version',
                                 version=umobj.__version__,
                                 help='Show version number and exit')
        self.parser.add_argument("-D", "--debug", dest="debug",
                               action="store_true", default=False,
                               help="Enable debug-level logging")
        self.parser.add_argument("-V", "--verbose", action="store_true",
                               dest="verbose", default=False,
                               help="Enable vebose logging")
        self.parser.add_argument("-A", "--access-key", dest="access_key",
                               help="Object Store Access Key")
        self.parser.add_argument("-S", "--secret-key", dest="secret_key",
                               help="Object Store Secret Key")
        self.parser.add_argument("-H", "--host", dest="host",
                               help="Object Store Host")
        self.parser.add_argument("-P", "--port", dest="port",
                               help="Object Store Port")

    def print_help(self):
        self.parser.print_help()

    def print_usage(self):
        self.parser.print_usage()

    def parse_args(self):
        return self.parser.parse_args()

    def add_verify_bag(self, short='-v', long='--verify-bag',
                       dest='verify_bag', help='Verify bagit archive'):
        self.parser.add_argument(short, long, dest=dest, help=help,
                                 action='store_true', default=False)

    def add_s3path(self, name='S3PATH', number='+', help='BUCKET[:KEY]'):
        self.parser.add_argument(name, type=str, nargs=number, help=help)

    def add_long(self, short='-l', long='--long', dest='long_list',
                 help='Show long information', action="store_true",
                 default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_policy(self, short='-p', long='--policy', dest='policies',
                   help='ACL Policy(s)', metavar="POLICY"):
        self.parser.add_argument(short, long, dest=dest, help=help,
                                 metavar=metavar, action='append')

    def add_recursive(self, short='-r', long='--recursive', dest='recursive',
                      help='Recurse', action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_delete(self, short='-d', long='--delete', dest='delete',
                   help='Delete', action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_mode(self, short='-m', long='--mode', dest='mode',
                 help='Mode', choices=None):
        if choices is None:
            choices = ['add', 'modify', 'remove', 'delete']
        self.parser.add_argument(short, long, dest=dest, help=help,
                                 choices=choices)

    def add_no_bucket_changes(self, long='--no-bucket-changes',
                              dest='no_bucket_changes',
                              help="Don't make any changes to the bucket, only to the keys underneath.  You must also specify the recursive option",
                              action='store_true', default=False):
        self.parser.add_argument(long, dest=dest, help=help, action=action,
                                 default=default)

    def add_public(self, short='-b', long='--public', dest='public',
                   help='Public URL', action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                                 action=action, default=default)

    def add_private(self, long='--private', dest='private',
                    help='Make Private', action='store_true', default=False):
        self.parser.add_argument(long, dest=dest, help=help,
                                 action=action, default=default)

    def add_push_bucket_acls(self, short='-o', long='--push-bucket-acls',
                             dest='push_bucket_acls',
                             help='Push bucket ACLs to key(s)',
                             action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                                 action=action, default=default)

    def add_md5(self, short='-m', long='--md5', dest='md5', help='MD5 Sum',
                action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_force(self, short='-f', long='--force', dest='force', help='Force',
                action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_multipart(self, short='-m', long='--multipart', dest='multipart',
                      help='Multipart upload and downloads',
                      action='store_true', default=False):
        self.parser.add_argument(short, long, dest=dest, help=help,
                               action=action, default=default)
