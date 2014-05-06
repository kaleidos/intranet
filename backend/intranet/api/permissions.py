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


class UsersPermission(permissions.BasePermission):
    """
    Permissisons for UserViewSet
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous():
            return False

        if not request.user.is_superuser and not request.user.is_staff:
            if request.method == 'DELETE':
                return False

            if request.method in ["POST", "PUT", "PATCH"] and request.user != obj:
                return False

        return True
