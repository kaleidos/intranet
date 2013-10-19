# -*- coding: utf-8 -*-

from __future__ import print_function

from cintranet.session import Session

import json
import datetime
from termcolor import colored


class UtilsAuthenticationMixin():

    def authenticate(self, username, password):
        r = self.session.post(
            self.BASE_URL + 'auth/login/',
            data=json.dumps({"username": username, "password": password})
        ).json()

        #TODO: this print shoud be in kmixin.py
        print('You are in')
        self.save_token(r)

    def save_token(self, user):
        self.session.headers.update({self.HTTP_TOKEN: user['token']})

    def logout(self):
        self.session.post(self.BASE_URL + 'auth/logout/')
        if self.HTTP_TOKEN in self.session.headers:
            del self.session.headers[self.HTTP_TOKEN]


class UtilsPartsMixin():

    def show_pending_parts(self):
        r = self.get_pending_parts()
        json_parts = r['results']
        pending_parts_ids = []
        for p in json_parts:
            pending_parts_ids.append(str(p['id']))
            print('[id: {0}] {1}-{2}'.format(p['id'], p['month'], p['year']))
        return pending_parts_ids

    def _print_day_hours(self, hours, year, month, day):
        d = datetime.date(year=year, month=month, day=day)
        weekday = d.weekday()
        if weekday in [5, 6]:
            if day % 2:
                colored_value = colored("{0:02}".format(hours), "red", "on_white")
            else:
                colored_value = colored("{0:02}".format(hours), "white", "on_red")
        else:
            if day % 2:
                colored_value = colored("{0:02}".format(hours), "blue", "on_white")
            else:
                colored_value = colored("{0:02}".format(hours), "white", "on_cyan")
        print(colored_value, end='')

    def show_part(self, id):
        part = self.get_part(id)
        projects_json = self.get_projects()
        projects = {}
        year = part['year']
        month = part['month']
        for project in projects_json:
            projects[int(project['id'])] = project['name']

        total_per_day = {}
        total_days = -1
        # Need refactor
        for key, values in part['data'].items():
            if total_days == -1:
                total_days = len(values)
                break
        total_hours = 0

        print(colored("{:20}".format(""), "white"), end='')
        first_weekday = datetime.date(year=year, month=month, day=1).weekday()
        weekdays_letters = ['M','T','W','T','F','S','S']
        for x in range(total_days):
            print("{:2}".format(weekdays_letters[(x + first_weekday) % 7]), end='')
        print(colored("{:4}".format(''), "white"))

        for key, values in part['data'].items():
            print(colored("{:20}".format(projects.get(int(key), "")[:20]), "white", "on_magenta"), end='')
            total_project_hours = 0
            for x in sorted(map(lambda x: (int(x[0]), x[1]), values.items())):
                total_project_hours += int(x[1])
                total_hours += int(x[1])
                if x[0] in total_per_day:
                    total_per_day[x[0]] += int(x[1])
                else:
                    total_per_day[x[0]] = int(x[1])
                self._print_day_hours(int(x[1]), year, month, x[0])
            print(colored("{:4}".format(total_project_hours), "white", "on_blue"))

        holidays = self.get_holidays(year, month)
        print(colored("{:20}".format("Holidays"), "white", "on_magenta"), end='')
        total_holidays_hours = 0
        for x in range(1, total_days + 1):
            holiday = list(filter(lambda x: x['day'] == x, holidays))
            hours = 0
            if holiday:
                total_per_day[x] += 8
                total_hours += 8
                total_holidays_hours += 8
                hours = 8

            self._print_day_hours(hours, year, month, x)
        print(colored("{:4}".format(total_holidays_hours), "white", "on_blue"))

        print(colored("{:20}".format("Total"), "white", "on_magenta"), end='')
        for x in range(1, total_days + 1):
            self._print_day_hours(total_per_day[x], year, month, x)
        print(colored("{:4}".format(total_hours), "white", "on_blue"))

    def get_part(self, id):
        return self.session.get(
            self.BASE_URL + 'parts/' + str(id) + "/",
        ).json()

    def get_holidays(self, year, month):
        return self.session.get(
            self.BASE_URL + 'holidays/',
            params={"page_size": 0, "year": year, "month": month}
        ).json()

    def get_pending_parts(self):
        return self.session.get(
            self.BASE_URL + 'parts/',
            params={'type': 'pending', 'page_size': 3}
        ).json()

    def show_projects(self):
        json_projects = self.get_projects()
        project_ids = []
        for p in json_projects:
            project_ids.append(str(p['id']))
            print('[id: {0}] {1}'.format(p['id'], p['name']))
        return project_ids

    def get_projects(self):
        return self.session.get(
            self.BASE_URL + 'projects/',
            params={'active': True}
        ).json()

    def get_part(self, part_id):
        return self.session.get(self.BASE_URL + 'parts/' + str(part_id)).json()

    def single_imputation(self, part_id, imputations):
        return self.session.patch(
            self.BASE_URL + 'parts/' + part_id + '/',
            data=json.dumps({"data": imputations})
        )

    def today(self):
        return str(datetime.datetime.today().day)


class UtilsHolidaysMixin():

    def view_my_holidays(self):
        holidays = self.get_holidays()
        head = ['Year', 'Total', 'Consumed', 'Requested', 'Pending']
        print("{:10}{:10}{:10}{:10}{:10}".format(*head))
        total_pending_days = 0
        for h in holidays:
            year = h['year']
            total_days = h['total_days']
            consumed_days = h['consumed_days']
            requested_days = h['requested_days']
            pending_days = total_days - consumed_days - requested_days
            total_pending_days += pending_days
            print("{:10}{:10}{:10}{:10}{:10}".format(str(year),
                                                     str(total_days),
                                                     str(consumed_days),
                                                     str(requested_days),
                                                     str(pending_days)))
        print('You have {0} days left'.format(total_pending_days))

    def get_holidays(self):
        return self.session.get(self.BASE_URL + 'holidays-years/').json()

    def is_special(self, day, year):
        for special_day in year['special_days']:
            if day == special_day['date']:
                return True
        return False

    def requested_working_days(self, data, years):
        requested_working_days = []
        beg = datetime.datetime.strptime(data['beginning'], "%Y-%m-%d")
        end = datetime.datetime.strptime(data['endining'], "%Y-%m-%d")
        for day in range(int((end - beg).days) + 1):
            req_day = beg + datetime.timedelta(day)
            is_special = self.is_special(req_day, years[req_day.year])
            is_weekend = datetime.date.weekday(req_day) in [5, 6]
            if not is_special and not is_weekend:
                requested_working_days.append(req_day)
        return requested_working_days

    def pending_days(self, years):
        """
        Returns pending days with that format:
        [(year, pending_days), (year, pending_days)]
        """
        pending_days = []
        for y in years:
            total = int(y['total_days'])
            requested = int(y['requested_days'])
            consumed = int(y['consumed_days'])
            pending_days.append((y['year'], total - requested - consumed))
        return pending_days

    def request_holidays(self, data):
        holiday_years = self.get_holidays()
        requested_working_days = self.requested_working_days(data, holiday_years)
        pending_days = self.pending_days(holiday_years)
        # check availability
        if len(requested_working_days) > sum(pending_days):
            raise (ValueError('Not enough days left'))

        # if availabe, generate requests
        reqs = []
        req = []
        for year in pending_days:
            reqs.update({pending_days['year']: []})
        beg = datetime.datetime.strptime(data['beginning'], "%Y-%m-%d")
        end = datetime.datetime.strptime(data['endining'], "%Y-%m-%d")
        for day in range(int((end - beg).days) + 1):
            if pending_days[0][1] > 0:
                req.append(day)
            else:
                reqs[pending_days][0] = req
                req = day
                pending_days.pop(0)
            pending_days[0][1] -= 1

        # make a post for each request
        for req in reqs.keys():
            data['year'] = req
            data['beginning'] = reqs[req].pop(0)
            data['ending'] = reqs[req].pop()
            self.session.post(
                self.BASE_URL + 'holidays-requests/',
                data=json.dumps({"data": data})).json()


class UtilsTalksMixin():
    def view_talks(self):
        head = ['Id', 'Talkers', 'Wanters', 'Talk']
        talks = self.session.get(self.BASE_URL + 'talks/', params={'page_size':1000}).json()
        if talks:
            print("{:10} {:10} {:10} {:10}".format(*head))

        for talk in talks['results']:
            print("{:10} {:10} {:10} {:10}".format(
                talk['id'],
                talk['talkers_count'],
                talk['wanters_count'],
                talk['name']
            ))

    def view_talk(self, talk_id):
        talk = self.session.get(self.BASE_URL + 'talks/' + str(talk_id) + "/").json()
        print("Name: ", talk['name'])
        print("Description: ", talk['description'])
        print("Talkers: ", ", ".join([talker['name'] for talker in talk['talkers']]))
        print("Wanters: ", ", ".join([wanter['name'] for wanter in talk['wanters']]))
        if talk['datetime']:
            print("Date:", talk['datetime'])
        if talk['duration']:
            print("Duration:", talk['duration'], 'min.')
        if talk['place']:
            print("Place:", talk['place'])

    def add_talk(self, title, description):
        data = {
            "name": title,
            "description": description,
            "obsolete": False,
        }
        self.session.post(self.BASE_URL + 'talks/', json.dumps(data))

    def mark_talk_as_i_want(self, talk_id):
        self.session.post(self.BASE_URL + 'talks/' + str(talk_id) + "/i_want/").json()

    def mark_talk_as_i_want(self, talk_id):
        self.session.post(self.BASE_URL + 'talks/' + str(talk_id) + "/i_want/").json()

    def mark_talk_as_i_dont_talk(self, talk_id):
        self.session.delete(self.BASE_URL + 'talks/' + str(talk_id) + "/i_talk/").json()

    def mark_talk_as_i_dont_want(self, talk_id):
        self.session.delete(self.BASE_URL + 'talks/' + str(talk_id) + "/i_want/").json()


class Client(UtilsAuthenticationMixin,
             UtilsPartsMixin,
             UtilsHolidaysMixin,
             UtilsTalksMixin):
    def __init__(self, config):
        self.BASE_URL = config.get('base_url', '')
        self.HTTP_TOKEN = config.get('http_token', 'HTTP_X_SESSION_TOKEN')
        self.session = Session()
        self.session.headers.update({'content-type': 'application/json'})
