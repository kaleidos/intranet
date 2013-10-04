# -*- coding: utf-8 -*-

from django.contrib import auth
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from intranet import decorators
from intranet import services
from intranet import serializers


class Login(APIView):
    """
    The login api view class.
    """
    @decorators.invalid_password_intercept(u"Username or password incorrect")
    @decorators.user_not_found_intercept(u"Username or password incorrect")
    @decorators.inactive_user_intercept(u"The user is inactive")
    def post(self, request, format=None):
        username = request.DATA.get("username", None)
        password = request.DATA.get("password", None)
        user_service = services.UserService()

        user = user_service.authenticate(username=username, password=password)
        auth.login(request, user)

        serializer = serializers.LoginSerializer(serializers.UserLogged(**{
            "token": request.session.session_key,
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "is_staff":  request.user.is_staff,
            "is_superuser":  request.user.is_superuser,
            "date_joined": request.user.date_joined,
            "last_login": request.user.last_login,
        }))
        return Response(serializer.data)


class Logout(APIView):
    """
    The logout api view class.
    """
    def post(self, request, format=None):
        auth.logout(request)
        return Response({"detail": u"Logout successfully."})


class ResetPassword(APIView):
    """
    The reset password api view class.
    """
    @decorators.invalid_password_intercept(u"Email or password incorrect")
    @decorators.user_not_found_intercept(u"Email or password incorrect")
    @decorators.inactive_user_intercept(u"The user is inactive")
    def post(self, request, format=None):
        username = request.DATA.get("username", None)
        domain = request.DATA.get("client_domain", settings.CLIENT_DOMAIN)
        use_https = request.DATA.get("use_https", settings.CLIENT_USE_HTTPS)

        user_service = services.UserService()
        user_service.reset_password(username=username, domain=domain, use_https=use_https)

        return Response({"detail": u"The reset password email has been sent successfully."})


class ChangePassword(APIView):
    """
    The reset password api view class.
    """
    @decorators.user_not_found_intercept(u"Incorrect token")
    @decorators.inactive_user_intercept(u"The user is inactive")
    def post(self, request, format=None):
        user = request.user
        token = request.DATA.get("token", None)
        password1 = request.DATA.get("password1", None)
        password2 = request.DATA.get("password2", None)

        if not password1 or password1 != password2:
            return Response({"detail": u"Password empty or not matchs"},
                            status.HTTP_400_BAD_REQUEST)

        user_service = services.UserService()
        if token:
            user_service.change_password(token, password1)
        elif user and not user.is_anonymous():
            user_service.change_password_to_user(user, password1)
        else:
            return Response({"detail": u"You don\'t have permission to do that."},
                            status.HTTP_401_UNAUTHORIZED)
        return Response({"detail": "The password has beeen changed successfully."})
