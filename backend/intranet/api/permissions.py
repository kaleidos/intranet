# -*- coding: utf-8 -*-
from rest_framework import permissions

class HolidaysPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous():
            return False

        if obj.status != 0 and request.method == 'DELETE':
            return False

        return obj.employee == request.user
