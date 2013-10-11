# -*- coding: utf-8 -*-
import datetime

from cintranet.session import Session
from cintranet import settings

import json

from datetime import date


class UtilsAuthenticationMixin():

    def authenticate(self, username, password):
        r = self.session.post(
            settings.BASE_URL + 'auth/login/',
            data=json.dumps({"username": username, "password": password})
        ).json()

        #TODO: this print shoud be in kmixin.py
        print('You are in')
        self.save_token(r)

    def save_token(self, user):
        self.session.headers.update({settings.HTTP_TOKEN: user['token']})

    def logout(self):
        self.session.post(settings.BASE_URL + 'auth/logout/')
        if settings.HTTP_TOKEN in self.session.headers:
            del self.session.headers[settings.HTTP_TOKEN]


class UtilsPartsMixin():

    def show_pending_parts(self):
        r = self.get_pending_parts()
        json_parts = r['results']
        pending_parts_ids = []
        for p in json_parts:
            pending_parts_ids.append(str(p['id']))
            print('[id: {0}] {1}-{2}'.format(p['id'], p['month'], p['year']))
        return pending_parts_ids

    def get_pending_parts(self):
        return self.session.get(
            settings.BASE_URL + 'parts/',
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
            settings.BASE_URL + 'projects/',
            params={'active': True}
        ).json()

    def get_part(self, part_id):
        return self.session.get(settings.BASE_URL + 'parts/' + part_id).json()

    def single_imputation(self, part_id, imputations):
        return self.session.patch(
            settings.BASE_URL + 'parts/' + part_id + '/',
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
        return self.session.get(settings.BASE_URL + 'holidays-years/').json()

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
            is_weekend = date.weekday(req_day) in [5, 6]
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
                settings.BASE_URL + 'holidays-requests/',
                data=json.dumps({"data": data})).json()


class Client(UtilsAuthenticationMixin,
              UtilsPartsMixin,
              UtilsHolidaysMixin):
    def __init__(self):
        self.session = Session()
        self.session.headers.update({'content-type': 'application/json'})
