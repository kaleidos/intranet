# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail

import datetime

from intranet.models import HolidaysRequest, HolidaysYear, User, STATE_ACCEPTED, STATE_REJECTED

class EmailsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        mail.outbox = []

        User.objects.all().delete()

        cls.c = Client()
        #Create users
        cls.user = User(
            username = 'user1',
            first_name = 'first',
            last_name = 'last',
            email = 'user@test.es'
        )
        cls.user.set_password('dummy')
        cls.user.save()

    #def test_reset_password_email_sent(self):
    #    response = self.c.post(reverse('reset-password'), {'username': self.user.username})
    #    self.assertEqual(len(mail.outbox), 1)

    def test_holidays_approbed_email_sent(self):
        year = HolidaysYear.objects.create(year=2013, active=True)
        request = HolidaysRequest.objects.create(
                employee=self.user,
                year=year,
                beginning=datetime.date.today(),
                ending=datetime.date.today()
        )
        self.assertEqual(len(mail.outbox), 0)

        request.status = STATE_REJECTED
        request.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your holidays has been Rejected")

        mail.outbox = []
        request.status = STATE_ACCEPTED
        request.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your holidays has been Accepted")

        mail.outbox = []
        request.status = STATE_ACCEPTED
        request.save()
        self.assertEqual(len(mail.outbox), 0)
