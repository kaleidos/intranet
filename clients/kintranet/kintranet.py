#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmd

from kclient import KClient
from kmixin import AuthenticationMixin, PartsMixin, HolidaysMixin
import settings


class KIntranet(AuthenticationMixin,
                PartsMixin,
                HolidaysMixin,
                cmd.Cmd):
    """Connecting to the Kaleidos Intranet"""

    def __init__(self):
        super().__init__()
        self.prompt = settings.RED + '[kintranet]>> ' + settings.WHITE
        self.intro  = 'Welcome to kaleidos intranet!'
        self.client = KClient()

    def emptyline(self):
        pass

    def do_EOF(self, args=None):
        self.stdout.write('\n')
        return True


if __name__ == '__main__':
    KIntranet().cmdloop()
