# -*- coding: utf-8 -*-
import os, sys

from .settings import *

try:
    from .local import *
except ImportError:
    print >> sys.stderr, "Trying import local.py settings..."
