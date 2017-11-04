from optparse import OptionParser

from .controller.archive import Archive
from .controller.script import Script
from .controller.test import Test


class Application:
    controller = {
        'archive': Archive,
        'script': Script,
    }

    def __init__(self):
        self.op = OptionParser()
        self.op.add_option('-m', '--module', dest='module', help='''Module for use. (archive,script)''')
        self.op.add_option('-a', '--action', dest='action', help='''Action to do. ''')

    def run(self):
        (options, args) = self.op.parse_args()

        controller = Application.controller.get(options.module)

        if controller is None:
            self.op.print_help()
        else:
            try:
                controller.action(options.action)(args)
            except IndexError:
                controller.action(None)(None)
