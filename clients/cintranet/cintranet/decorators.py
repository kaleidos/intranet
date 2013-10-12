# -*- coding: utf-8 -*-
from __future__ import print_function

from functools import wraps

def intercept_error(function):
    @wraps(function)
    def _decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            print(e)
            return None
    return _decorator

