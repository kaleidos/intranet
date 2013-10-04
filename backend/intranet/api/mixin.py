# -*- coding: utf-8 -*-

from django.utils.functional import Promise
from django.utils.encoding import force_unicode

import json

import datetime


class LazyEncoder(json.JSONEncoder):
    """ Costum JSON encoder class for encode correctly traduction strings.
    Is for ajax response encode."""

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        return super(LazyEncoder, self).default(obj)
