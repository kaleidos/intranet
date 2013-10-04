# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

import json

from intranet.models import User, Project, Part, Imputation, STATE_CREATED

class Test(TestCase):
    def setUp(self):
        self.c = Client()

        #Create users
        user = User(
            username = 'user1',
            first_name = 'first',
            last_name = 'last',
            email = 'user@test.es'
        )
        user.set_password('dummy')
        user.save()
        self.user = user

        #LOGIN
        response = self.c.post(reverse('api:login'), {'username': self.user.username, 'password':'dummy'})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)
        self.token_auth = json_response['token_auth']

        self.project = Project(
            name = 'project 1',
            description = 'description project 1',
        )
        self.project.save()

        self.part = Part(
            month = 06,
            year = 2011,
            employee = self.user,
            state = 1,
        )
        self.part.save()

        self.imputation = Imputation(
            part = self.part,
            day = 13,
            hours = 5,
            project = self.project,
        )
        self.imputation.save()

    def test_login_logout_ok(self):
        self.c = Client()
        response = self.c.post(reverse('api:login'), {'username': self.user.username, 'password':'dummy'})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)
        token_auth = json_response['token_auth']

        self.c = Client()
        response = self.c.get(reverse('api:logout'), {'token_auth': token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)

    def test_logout_invalid(self):
        self.c = Client()
        response = self.c.get(reverse('api:logout'))
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], False)

    def test_project_list(self):
        self.c = Client()
        response = self.c.get(reverse('api:project-list'), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['projects']), 1)

    def test_part_list(self):
        self.c = Client()
        response = self.c.get(reverse('api:part-list'), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['parts']), 1)

    def test_imputation_list(self):
        self.c = Client()
        response = self.c.get(reverse('api:imputation-list'), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['imputations']), 1)

    def test_imputation_create(self):
        self.c = Client()
        response = self.c.post(reverse('api:imputation-add'), {'project': self.project.id, 'day':3, 'hours':5, 'part':self.part.id, 'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)
        self.assertEqual(json_response.has_key('id'), True)
        id_imp = json_response['id']

        #Invalid part
        response = self.c.post(reverse('api:imputation-add'), {'project': self.project.id, 'day':3, 'hours':5, 'part':222, 'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], False)

        #Invalid day
        response = self.c.post(reverse('api:imputation-add'), {'token_auth': self.token_auth, 'day':33, 'part':self.part.id, 'project': self.project.id})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], False)

        response = self.c.get(reverse('api:imputation-list'), {'token_auth': self.token_auth, 'day':3, 'part':self.part.id, 'project': self.project.id})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['imputations']), 1)

        response = self.c.get(reverse('api:imputation-list'), {'token_auth': self.token_auth, 'day':1, 'part':self.part.id, 'project': self.project.id})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['imputations']), 0)

        #Delete
        response = self.c.get(reverse('api:imputation-delete', args=[id_imp]), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)

        response = self.c.get(reverse('api:imputation-list'), {'token_auth': self.token_auth, 'day':3, 'part':self.part.id, 'project': self.project.id})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['imputations']), 0)

    def test_part_creation(self):
        self.c = Client()
        response = self.c.post(reverse('api:part-add'), {'month': 3, 'year':2008, 'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)

        self.assertEqual(json_response['valid'], True)
        self.assertEqual(json_response.has_key('id'), True)
        id_part = json_response['id']

        response = self.c.get(reverse('api:part-list'), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['parts']), 2)
        parts = json_response['parts']
        for part in parts:
            if part['id'] == id_part:
                self.assertEqual(part['state'], STATE_CREATED)


        response = self.c.get(reverse('api:part-delete', args=[id_part]), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)

        response = self.c.get(reverse('api:part-list'), {'token_auth': self.token_auth})
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['parts']), 1)

