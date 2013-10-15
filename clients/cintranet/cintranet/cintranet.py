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
        self.config = self.read_config()
        self.prompt = colored('[kintranet]>> ', 'red')
        self.intro  = 'Welcome to kaleidos intranet!'
        self.client = Client(self.config['api'])

    def cmdloop(self):
        if 'username' in self.config['api'] and 'password' in self.config['api']:
            username = self.config['api']['username']
            password = self.config['api']['password']
            try:
                self.client.authenticate(username, password)
                self.prompt = colored('[' + username + ']>> ', 'green')
            except Exception as e:
                print(e)
        super().cmdloop()

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

    def do_help(self, args):
        "Show this help"
        print("General commands:")
        print("  {:16}  {}".format("quit", "Quit the cintranet client"))
        print("  {:16}  {}".format("help", "Show this help"))
        print()

        print("Auth commands:")
        print("  {:16}  {}".format("login [<username>]", "Login"))
        print("  {:16}  {}".format("logout", "Logout"))
        print()

        print("Parts commands:")
        print("  {:16}  {}".format("projects", "List my projects"))
        print("  {:16}  {}".format("pending_parts", "List the 3 latest pending parts"))
        print("  {:16}  {}".format("impute", "Impute hours to a project"))
        print()

        print("Holidays commands:")
        print("  {:16}  {}".format("view_my_holidays", "View my holidays status"))
        print("  {:16}  {}".format("request_holidays", "Add a new request of holidays"))
        print()

        print("Talks commands:")
        print("  {:16}  {}".format("talks", "List the talks"))
        print("  {:16}  {}".format("talk <id> [iWant|iTalk]", "View a talk, or mark as i want or i talk"))
        print("  {:16}  {}".format("new_talk <id>#<description>", "Add a new talk"))
        print()

    def do_quit(self, args=None):
        "Exit"
        self.stdout.write('\n')
        return True

    do_EOF = do_quit

def main_loop():
    CIntranet().cmdloop()

if __name__ == '__main__':
    main_loop()
