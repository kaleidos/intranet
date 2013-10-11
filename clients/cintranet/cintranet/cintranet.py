#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmd

from cintranet.client import Client
from cintranet.mixin import AuthenticationMixin, PartsMixin, HolidaysMixin
from cintranet import settings


class CIntranet(AuthenticationMixin,
                PartsMixin,
                HolidaysMixin,
                cmd.Cmd):
    """Connecting to the Kaleidos Intranet"""

    def __init__(self):
        super().__init__()
        self.prompt = settings.RED + '[kintranet]>> ' + settings.WHITE
        self.intro  = 'Welcome to kaleidos intranet!'
        self.client = Client()

    def emptyline(self):
        pass

    def do_EOF(self, args=None):
        self.stdout.write('\n')
        return True
