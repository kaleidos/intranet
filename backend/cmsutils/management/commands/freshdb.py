"""
put in your project's management/commands/freshdb.py
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Drops and re-creates the database"

    def handle(self, *args, **options):
        from django.db import connection
        from django.conf import settings
        c = connection.cursor()
        c.execute("DROP DATABASE " + settings.DATABASE_NAME)
        c.execute("CREATE DATABASE " + settings.DATABASE_NAME)
        print 'Created new database: %s' % settings.DATABASE_NAME
        c.close()
