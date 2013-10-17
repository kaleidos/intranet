# -*- coding: utf-8 -*-


class NotFound(Exception):
    """
    Exception used for not found objects.
    """
    pass


class InactiveUser(Exception):
    """
    Exception used for inactive users.
    """
    pass


class InvalidParamError(Exception):
    """
    Exception used for invalid parameters.
    """
    pass


class InvalidPassword(Exception):
    """
    Exception used for invalid password.
    """
