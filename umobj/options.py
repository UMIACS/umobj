from optparse import Option, OptionGroup, OptionParser, OptionValueError
from copy import copy

def check_date(option, opt, value):
    try:
        return datetime.strptime(value, "%Y%m%d")
    except ValueError:
        raise OptionValueError("option %s: invalid date value: %r. " + \
                               "Should have a format like \"YYYYMMDD\"" %
                               (opt, value))


class OptionTypes(Option):
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    ## date checker
    TYPES = Option.TYPES + ("date",)
    TYPE_CHECKER["date"] = check_date


class umobj_parser(object):
    def __init__(self, usage, description=None):
        self.parser = OptionParser(usage=usage, description=description,
                                   option_class=OptionTypes)
        self.parser.add_option("-D", "--debug", dest="debug",
                               action="store_true", default=False,
                               help="Enable debug-level logging mode")
        self.parser.add_option("-V", "--verbose", action="store_true",
                               dest="verbose", default=False,
                               help="Enable vebose mode")
        self.parser.add_option("-A", "--access-key", dest="access_key",
                               help="Access Key")
        self.parser.add_option("-S", "--secret-key", dest="secret_key",
                               help="Secret Key")
        self.parser.add_option("-H", "--host", dest="host",
                               help="Object Store Host")
        self.parser.add_option("-P", "--port", dest="port",
                               help="Object Store Port")
    def print_help(self):
        self.parser.print_help()

    def print_usage(self):
        self.parser.print_usage()

    def parse_args(self):
        return self.parser.parse_args()

    def add_long(self, short='-l', long='--long', dest='long_list',
                 help='Show long information', action="store_true",
                 default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_policy(self, short='-p', long='--policy', dest='policies',
                   action="append", help='ACL Policy(s)', metavar="POLICY"):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, metavar=metavar)

    def add_recursive(self, short='-r', long='--recursive', dest='recursive',
                      help='Recurse', action='store_true', default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_delete(self, short='-d', long='--delete', dest='delete',
                   help='Delete', action='store_true', default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_mode(self, short='-m', long='--mode', dest="mode",
                 help="Mode",
                 type='choice', choices=None):
        if choices is None:
            choices = ['add', 'modify', 'remove', 'delete']
        help = "%s (%s)" % (help, ','.join(choices))
        self.parser.add_option(short, long, dest=dest, help=help, type=type,
                               choices=choices)

    def add_public(self, short='-b', long='--public', dest='public',
                   help='Public URL', action='store_true', default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_md5(self, short='-m', long='--md5', dest='md5', help='MD5 Sum',
                action='store_true', default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_force(self, short='-f', long='--force', dest='force', help='Force',
                action='store_true', default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)

    def add_multipart(self, short='-m', long='--multipart', dest='multipart',
                      help='Multipart upload and downloads',
                      action='store_true', default=False):
        self.parser.add_option(short, long, dest=dest, help=help,
                               action=action, default=default)
