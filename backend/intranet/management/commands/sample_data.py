# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils.dates import MONTHS

from calendar import monthrange
from datetime import date, timedelta

from sampledatahelper.helper import SampleDataHelper

from intranet.models import *


class Command(BaseCommand):
    args = ''
    help = 'Intranet Sample Data'
    sd = None

    # Creation functions:
    def create_users(self):
        max_users = 5
        for u in range(0, max_users):
            user = User()
            user.email = self.sd.email()
            user.username = self.sd.word()
            user.set_password(user.username)
            user.save()

    def create_holidays_years(self):
        max_holidays_years = 3
        for x in range(max_holidays_years, -1, -1):
            holidays_year = HolidaysYear()
            holidays_year.year = date.today().year - x
            holidays_year.active = x in [0, 1]
            holidays_year.save()

    def create_holidays_requests(self):
        max_holidays_requests_per_user = 10
        for u in User.objects.all():
            for x in range(0, max_holidays_requests_per_user):
                holidays_request = HolidaysRequest()
                holidays_request.employee = u
                holidays_request.year = self.sd.db_object(HolidaysYear)
                holidays_request.beginning = self.sd.date_between(
                    date(year=holidays_request.year.year, month=1, day=1),
                    date(year=holidays_request.year.year, month=12, day=31),
                )
                holidays_request.ending = self.sd.date_between(
                    holidays_request.beginning,
                    holidays_request.beginning + timedelta(10)
                )
                holidays_request.status = self.sd.choice(HOLIDAYS_REQUEST_CHOICES)[0]
                holidays_request.flexible_dates = self.sd.boolean()
                holidays_request.comments = self.sd.paragraph()
                holidays_request.save()

    def create_sectors(self):
        max_sectors = 2
        for u in range(0, max_sectors):
            sector = Sector()
            sector.name = self.sd.word()
            sector.save()

    def create_clients(self):
        max_clients = 5
        for u in range(0, max_clients):
            client = Client()
            client.internal_id = str(u)
            client.name = self.sd.word()
            client.sector = Sector.objects.order_by("?")[0]
            client.employees_number = self.sd.int(1000)
            client.contact_person = self.sd.paragraph()
            client.ubication = self.sd.paragraph()
            client.save()

    def create_projects_parts_and_imputations(self):
        max_projects = 3
        for p in range(0, max_projects):
            project = Project()
            project.internal_id = self.sd.word() + str(p)
            project.name = self.sd.word()
            project.description = self.sd.paragraph()
            project.active = self.sd.boolean()
            project.client = Client.objects.order_by("?")[0]
            project.save()
            project_users = User.objects.order_by("?")[0:3]
            for u in project_users:
                assignation = Assignation(employee=u, project=project)
                assignation.save()

        for u in User.objects.all():
            for year in [2011, 2012, 2013]:
                for month in MONTHS.keys():
                    part = Part()
                    part.month = month
                    part.year = year
                    part.employee = u
                    part.state = self.sd.choice(PART_STATE_CHOICES)[0]
                    part.save()

            for part in u.parts.all():
                part.data = {}
                for project in u.projects.all():
                    project_data = {day+1: self.sd.int(8) for day in range(monthrange(part.year, part.month)[1])}
                    part.data[project.id] = project_data

                part.save()

    # handle
    def handle(self, *args, **options):
        self.sd = SampleDataHelper(seed=1234567890)

        print "Creating users"
        self.create_users()

        print "Creating sectors"
        self.create_sectors()

        print "Creating clients"
        self.create_clients()

        print "creating holidays"
        self.create_holidays_years()
        self.create_holidays_requests()

        print "Creating projects parts and imputations"
        self.create_projects_parts_and_imputations()
