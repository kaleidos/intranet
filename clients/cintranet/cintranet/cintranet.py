#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import cmd
import sys
import os
from termcolor import colored

from cintranet.client import Client
from cintranet.mixin import AuthenticationMixin, PartsMixin, HolidaysMixin, TalksMixin


class CIntranet(AuthenticationMixin,
                PartsMixin,
                HolidaysMixin,
                TalksMixin,
                cmd.Cmd):
    """Connecting to the Kaleidos Intranet"""

    def __init__(self):
        super().__init__()
        config = self.read_config()

        self.prompt = colored('[kintranet]>> ', 'red')
        self.intro  = 'Welcome to kaleidos intranet!'
        self.client = Client(config['api'])

    def read_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.expanduser("~/.cintranet")
        if not os.path.exists(config_path):
            sys.stderr.write(colored("ERROR: The ~/.cintranet config file must exists."))
            sys.exit(1)

        config.read(config_path)

        if "api" not in config:
            sys.stderr.write(colored("ERROR: The ~/.cintranet config file contain api section."))
            sys.exit(1)

        if "base_url" not in config['api']:
            sys.stderr.write(colored("ERROR: The ~/.cintranet config file contain base_url in api section."))
            sys.exit(1)

        return config

    def emptyline(self):
        pass

    def do_EOF(self, args=None):
        self.stdout.write('\n')
        return True

    do_quit = do_EOF

def main_loop():
    CIntranet().cmdloop()

if __name__ == '__main__':
    main_loop()
