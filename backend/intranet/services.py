# -*- coding: utf-8 -*-

from django.contrib import auth

try:
    import uuid
    assert uuid
except ImportError:
    from django_extensions.utils import uuid

from . import exceptions
from . import emails


class UserService(object):
    """
    The user service class.
    """
    def _get_user_by_username(self, username):
        try:
            user = auth.get_user_model().objects.get(username=username)
            if not user.is_active:
                raise exceptions.InactiveUser()
            return user
        except auth.get_user_model().DoesNotExist:
            raise exceptions.NotFound()

    def _get_user_by_reset_password_token(self, reset_password_token):
        try:
            user = auth.get_user_model().objects.get(reset_password_token=reset_password_token)
            if not user.is_active:
                raise exceptions.InactiveUser()
            return user
        except auth.get_user_model().DoesNotExist:
            raise exceptions.NotFound()

    def authenticate(self, username=None, password=None):
        """
        Authenticates an user. Get the email and a clear password and return an authenticate user.

        :param string username: a username
        :param string password: a password
        :return: an authenticated user
        :rtype: User
        """
        user = self._get_user_by_username(username)
        if user.check_password(password):
            return auth.authenticate(username=username, password=password)
        raise exceptions.InvalidPassword()

    def reset_password(self, username=None, domain=None, use_https=True):
        """
        Reset the password (generate the reset token) and send the email.

        :param string username: a username
        :param string domain: The domain name
        :param boolean use_https: enable/disable https link on sended email
        :return: an user
        :rtype: User
        """
        user = self._get_user_by_username(username)

        user.reset_password_token = uuid.uuid4()
        user.save(update_fields=["reset_password_token"])

        context = {
            'domain': domain,
            'user': user,
            'protocol': use_https and 'https' or 'http',
        }
        emails.send_reset_password_email(user, context)

        return user

    def change_password(self, token=None, password=None):
        """
        Change the password of an user with his reset password token and a new passowrd.

        :param string token: a valid reset password token
        :param string password: a new password
        :return: an user
        :rtype: User
        """
        user = self._get_user_by_reset_password_token(token)
        user.set_password(password)
        user.reset_password_token = u""
        user.save(update_fields=["password", "reset_password_token"])
        return user

    def change_password_to_user(self, user=None, password=None):
        """
        Change the password of an user with his reset password token and a new passowrd.

        :param User user: a user object
        :param string password: a new password
        :return: an user
        :rtype: User
        """
        if not user.is_active:
            raise exceptions.InactiveUser()

        user.set_password(password)
        user.save(update_fields=["password"])
        return user
