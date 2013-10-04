# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext_lazy as _

import functools
import json

from rest_framework.response import Response
from rest_framework import status

from .api.mixin import LazyEncoder
from . import exceptions


def invalid_password_intercept(error_msg):
    """
    Catches custom InvalidPassword exceptions raised and transforms them in a Response with a
    custom error message. This decorator should be used in an api views.
    """
    def inner(method):
        @functools.wraps(method)
        def _decorator(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exceptions.InvalidPassword:
                return Response({"detail": _(error_msg)}, status.HTTP_400_BAD_REQUEST)
        return _decorator
    return inner


def inactive_user_intercept(error_msg):
    """
    Catches custom InactiveUser exceptions raised and transforms them in a Response with a custom
    error message. This decorator should be used in an api views.
    """
    def inner(method):
        @functools.wraps(method)
        def _decorator(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exceptions.InactiveUser:
                return Response({"detail": _(error_msg)}, status.HTTP_400_BAD_REQUEST)
        return _decorator
    return inner


def user_not_found_intercept(error_msg):
    """
    Catches custom NotFound exceptions raised and transforms them in a Response with a custom
    error message. This decorator should be used in an api views.
    """
    def inner(method):
        @functools.wraps(method)
        def _decorator(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except exceptions.NotFound:
                return Response({"detail": _(error_msg)}, status.HTTP_400_BAD_REQUEST)
        return _decorator
    return inner


def token_auth_required(view_func):
    @functools.wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(self, request, *args, **kwargs)
        else:
            context = {'valid': False, 'errors': [_(u'authentication required')]}
            return HttpResponse(json.dumps(context, indent=4, cls=LazyEncoder, sort_keys=True),
                                mimetype="text/plain",
                                status=401)

    return _wrapped_view
