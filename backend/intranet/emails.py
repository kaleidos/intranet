# -*- coding: utf-8 -*-

from djmail import template_mail


def send_reset_password_email(user, context):
    """
    Send a reset password email to an user.

    :param User user: An user object.
    """
    mails = template_mail.MagicMailBuilder()
    email = mails.reset_password(user, context)
    email.send()
