# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from intranet.models import *
from optparse import make_option

import os, datetime, tempfile, codecs, csv, cStringIO, math

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class Command(BaseCommand):
    help = 'Intranet imputation analysis'

    option_list = BaseCommand.option_list + (
        make_option('--year', action='store', default=datetime.datetime.today().year, dest='year',
            help="Set the year"),
        make_option('--month', action='store', default=datetime.datetime.today().month, dest='month',
            help="Set the month"),
        make_option('--client-id', action='store', default=1, dest='client_id',
            help="Set the client"),
    )

    # handle
    def handle(self, *args, **options):

        self.year = options["year"]
        self.month = options["month"]
        self.client_id = int(options["client_id"])

        imputations_dict = {}
        imputations = list(Imputation.objects.filter(
            part__month__exact = self.month,
            part__year__exact = self.year,
            part__employee__is_company_team = True,
        ))

        for imputation in imputations:
            default_dict = {'employee': imputation.part.employee, 'imputations': [], 'total': 0, 'total_company': 0}
            user_imputations = imputations_dict.get(imputation.part.employee.pk, default_dict)
            user_imputations['imputations'].append(imputation)
            imputations_dict[imputation.part.employee.pk] = user_imputations

        with tempfile.NamedTemporaryFile(delete=False) as f:
            writer = UnicodeWriter(f)
            writer.writerow([u"Nombre de usuario", "Total", "Total no facturable", "Porcentaje no facturable"])

            for employee_pk, employee_imputations in imputations_dict.items():
                total = sum([x.total() for x in employee_imputations['imputations']])
                total_company = sum([x.total() for x in employee_imputations['imputations'] if x.project.client.id == self.client_id])
                percentage = total and total_company * 100. / total or 0
                writer.writerow([employee_imputations['employee'].username, unicode(total), unicode(total_company), unicode(percentage)])

            f.close()
            print f.name
