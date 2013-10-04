# -*- coding: utf-8 -*-

from rest_framework.authentication import BaseAuthentication


class SessionAuthentication(BaseAuthentication):
    """
    Use Django's session framework for authentication without csrf.
    """
    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.

        :param Request request: an HTTP request object.
        :return: a user object or None
        :rtype: User or None
        """
        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
            return None

        return (user, None)
