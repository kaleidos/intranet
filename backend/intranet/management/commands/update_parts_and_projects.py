from django.core.management.base import BaseCommand, CommandError
from intranet.models import *
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Intranet part generation and project update'

    # handle
    def handle(self, *args, **options):
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month

        #Part generation
        for u in User.objects.filter(is_company_team=True):
            print "User %s" % (u)
            part = Part.objects.filter(year=year, month=month, employee=u)
            part = part.count()==1 and part.get() or None
            if not part:
                part = Part.objects.create(year=year, month=month, employee=u, state=STATE_CREATED)

        #Part update
        for project in Project.objects.all():
            project.update_last_month_activity()

