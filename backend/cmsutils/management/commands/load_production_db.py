# -*- coding: utf-8 -*-

"""
Command for loading production database, and upgrading to development one (by default using south)
"""

import os
import tempfile
import urllib

from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from cmsutils.management.commands.rebuild_db import execute_drop_database, \
                                                    execute_create_database


def execute_sql_from_file(sql_file):
    import pexpect

    args = ['psql']
    args.append('-f %s' % sql_file)
    outlog = os.path.join(tempfile.gettempdir(), 'out.log')
    args.append('-o %s' % outlog)
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        database_host = settings.DATABASES['default']['HOST']
        database_port = settings.DATABASES['default']['PORT']
        database_name = settings.DATABASES['default']['NAME']
        database_password = settings.DATABASES['default']['PASSWORD']
    else:
        database_host = settings.DATABASE_HOST
        database_port = settings.DATABASE_PORT
        database_name = settings.DATABASE_NAME
        database_password = settings.DATABASE_PASSWORD
    if database_host:
            args.append("-h %s" % database_host)
    if hasattr(settings, 'DATABASE_MANAGEMENT_USER'):
            args.append("-U %s" % settings.DATABASE_MANAGEMENT_USER)
    if database_port:
            args.append("-p %s" % database_port)
    args.append(database_name)

    cmd = ' '.join(args)
    if database_password:
        child = pexpect.spawn(' '.join(args))
        child.expect("\s*:")  # psql ask for the password here
        child.sendline(database_password)

        child.expect(pexpect.EOF)
        print child.before
        child.close()
    else:
        os.system(cmd)


class Command(BaseCommand):
    help = "Load production database from an URL defined in settings"
    args = ""
    option_list = BaseCommand.option_list + (
            make_option('-N', '--no-migrate', action='store_false', dest='migrate',
                    help=''),
            make_option('-I', '--no-interactive', action='store_false', dest='interactive',
                    help=''),
            make_option('-u', '--database-url', dest='database_url',
                    help='Database URL'),
            make_option('-M', '--migration-command', dest='migrate_command', default='syncdb --migrate',
                    help='Migration command. Use space between " to put parameters. Example: -M "dmigrate all"'),
            make_option('-p', '--update-passwords', dest='update_passwords',
                    help='Django user passwords to update. In format user1:password1,user2:password,...'),
    )
    requires_model_validation = False

    def handle(self, *args, **options):
        self.migrate = options.get('migrate')
        if self.migrate is None:
            self.migrate = True
        self.migrate_command = options.get('migrate_command').split(" ")
        self.interactive = options.get('interactive')
        if self.interactive is None:
            self.interactive = True

        connection.close()

        db_url = options.get('database_url', None)
        if db_url is None:
            db_url = getattr(settings, 'PRODUCTION_DB_URL', None)
            if db_url is None:
                raise CommandError('''For executing this command, you have pass a --database-url parameter,
 or to define a PRODUCTION_DB_URL settings, with URL to a compressed database SQL (bzip2 compression)''')

        update_passwords = options.get('update_passwords', None)
        if update_passwords is None:
            update_passwords = getattr(settings, 'PRODUCTION_DB_UPDATE_PASSWORDS', None)
        else:
            update_passwords = [(p.split(':')[0], p.split(':')[1]) for p in update_passwords.split(',')]

        if getattr(settings, 'NEVER_DESTROY_DATABASE', False):
            print 'Execution aborted because you have NEVER_DESTROY_DATABASE settings'
            return

        if self.interactive:
            print 'WARNING: THIS WILL DESTROY YOUR DATABASE'
            print 'Are you sure you want to continue?'
            answer = raw_input('yes/no [no] ')
            if answer != "yes":
                print 'Execution aborted'
                return

        print 'Fetching database from %s...' % db_url,
        db_bzip_filename, headers = urllib.urlretrieve(db_url)
        db_sql_filename = os.path.join(tempfile.gettempdir(), 'out.sql')
        print 'Done'

        print 'Begin database decompression...',
        os.system('bunzip2 --stdout %s > %s' % (db_bzip_filename, db_sql_filename))
        print 'Done'
        print 'Dropping database...',
        ret = execute_drop_database()
        if ret != 0:
            raise CommandError('ERROR: There was an error while dropping the database')
        print 'Done'

        print 'Creating new database...',
        ret = execute_create_database()
        if ret != 0:
            raise CommandError('ERROR: There was an error while creating the database')
        print 'Done'

        print 'Dumping database SQL to new database...',
        execute_sql_from_file(db_sql_filename)
        print 'Done'

        if update_passwords:
            for update in update_passwords:
                try:
                    user = User.objects.get(username=update[0])
                    user.set_password(update[1])
                    user.save()
                    print '%s password changed to %s' % update
                except User.DoesNotExist:
                    pass

        if not self.migrate:
            print 'Exit process without launching dmigrations'
            return
        print 'Migrating database...'
        migrate_kwargs = dict([(a, None) for a in self.migrate_command if a.startswith('-')])
        migrate_args = [a for a in self.migrate_command if a not in migrate_kwargs]
        call_command(*migrate_args, **migrate_kwargs)
        print 'Done'
