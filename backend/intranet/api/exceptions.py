# -*- coding: utf-8 -*-

from rest_framework.exceptions import APIException


class InvalidUsernameOrPassword(APIException):
    """
    Exception used for invalid username or password.
    """
    detail = "Invalid username or password"
    status_code = "400"

class InvalidUsername(APIException):
    """
    Exception used for invalid username.
    """
    detail = "Invalid username"
    status_code = "400"


class InvalidToken(APIException):
    """
    Exception used for invalid username.
    """
    detail = "Invalid token"
    status_code = "400"


class InactiveUser(APIException):
    """
    Exception used for invalid username.
    """
    detail = "Inactive user"
    status_code = "400"


class YouAreNotATalker(APIException):
    """
    Exception used when you need to be a talker to do something.
    """
    detail = "You are not a talker"
    status_code = "400"


