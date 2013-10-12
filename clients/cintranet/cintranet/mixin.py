# -*- coding: utf-8 -*-
from __future__ import print_function

import getpass
from termcolor import colored

from cintranet.decorators import intercept_error

class AuthenticationMixin(object):
    @intercept_error
    def do_login(self, args=None):
        """
        Login method. Expecting username and password
        """
        if args:
            username = args.split()[0]
        elif 'username' in self.config['api']:
            username = self.config['api']['username']
        else:
            username = input('Username: ')
        password = getpass.getpass('Password: ')
        self.client.authenticate(username, password)
        self.prompt = colored('[' + username + ']>> ', 'green')

    def do_logout(self, args=None):
        """
        Logout method. Deletes the HTTP_TOKEN key from session
        """
        self.client.logout()
        self.prompt = colored('[kintranet]>> ', 'red')
        print('Ok, now you can exit or login again')


class PartsMixin():

    @intercept_error
    def do_pending_parts(self, args=None):
        """
        Show the 3 latest pending parts.
        """
        self.client.show_pending_parts()

    @intercept_error
    def do_projects(self, args=None):
        """
        Show projects for the user
        """
        self.client.show_projects()

    @intercept_error
    def do_impute(self, args=None):
        """
        Impute hours method.
        """
        #TODO: show how many hours are imputed in each part
        #TODO: indicate that are pending parts
        pending_parts_ids = self.client.show_pending_parts()
        part_id = ''
        while part_id == '' or part_id not in pending_parts_ids:
            part_id = input('Select a part from the list: ')
        part = self.client.get_part(part_id)

        imputations = part['data']

        opt = 'y'
        while opt == 'y':
            project_ids = self.client.show_projects()
            project_id = ''
            while project_id == '' or project_id not in project_ids:
                project_id = input('Select a project from the list: ')

            day = input('Enter the day [today]: ')
            day = day or self.client.today()
            current = imputations[project_id][day]
            hours = input('Enter the hours [current {0}]: '.format(current))
            hours = hours or 0
            imputations[project_id][day] = int(current) + int(hours)

            self.client.single_imputation(part_id, imputations)

            opt = input("Do you want to continue? [Y/n]: ")
            opt = opt or 'y'


class HolidaysMixin():

    @intercept_error
    def do_view_my_holidays(self, args=None):
        """
        View holidays status
        """
        self.client.view_my_holidays()

    @intercept_error
    def do_request_holidays(self, args=None):
        """
        Request holidays
        """
        beginning = input('Init day [yyyy-mm-dd]: ')
        ending = input('End day [yyyy-mm-dd]: ')
        flexible_dates = input('Flexible? [S/n] ')
        flexible_dates = flexible_dates or 's'
        comments = input('Comments: ')
        data = {"beginning": beginning,
                "ending": ending,
                "flexible_dates": flexible_dates,
                "comments": comments}
        self.client.request_holidays(data)

class TalksMixin():

    @intercept_error
    def do_talks(self, args=None):
        """
        View list of talks
        """
        self.client.view_talks()

    @intercept_error
    def do_talk(self, args):
        """
        View a talk or mark as i want or i talk
        """
        args = args.split()

        try:
            talk_id = int(args[0])
        except ValueError:
            raise Exception('Not valid talk_id')

        if len(args) > 1 and args[1] == 'iWant':
            self.client.mark_talk_as_i_want(talk_id)
        elif len(args) > 1 and args[1] == 'iTalk':
            self.client.mark_talk_as_i_talk(talk_id)
        else:
            self.client.view_talk(talk_id)
