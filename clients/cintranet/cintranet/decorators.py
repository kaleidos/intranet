# -*- coding: utf-8 -*-
from __future__ import print_function
import traceback

from functools import wraps

def intercept_error(function):
    @wraps(function)
    def _decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            if args[0].config['api'].get('debug', False):
                traceback.print_exc()
            else:
                print(e)
            return None
    return _decorator

