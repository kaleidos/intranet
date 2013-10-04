import glob
from optparse import make_option
import os.path
import subprocess

from django.conf import settings
from django.core.management import call_command, get_commands
from django.core.management.base import BaseCommand

from cmsutils.signals import pre_rebuild_db, post_rebuild_db_before_syncdb, post_rebuild_db

if 'south' in settings.INSTALLED_APPS:
    HAS_SOUTH = True
else:
    HAS_SOUTH = False

# utility functions


def get_db_command_args():
    comdb_args = []
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        database_host = settings.DATABASES['default']['HOST']
        database_port = settings.DATABASES['default']['PORT']
        database_name = settings.DATABASES['default']['NAME']
    else:
        database_host = settings.DATABASE_HOST
        database_port = settings.DATABASE_PORT
        database_name = settings.DATABASE_NAME
    if database_host:
        comdb_args.append("--host=%s" % database_host)
    if hasattr(settings, 'DATABASE_MANAGEMENT_USER'):
        comdb_args.append("--username=%s" % settings.DATABASE_MANAGEMENT_USER)
    if database_port:
        comdb_args.append("--port=%s" % database_port)
    comdb_args.append(database_name)
    return comdb_args


def execute_drop_database():
    """ execute DROP DATABASE statement """
    dropdb_args = get_db_command_args()
    dropdb_command = ['dropdb'] + dropdb_args

    return subprocess.call(dropdb_command)


def execute_create_database(template=None):
    """ execute CREATE DATABASE command """
    createdb_args = get_db_command_args()
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        database_user = settings.DATABASES['default']['USER']
    else:
        database_user = settings.DATABASE_USER
    createdb_args.extend(['--owner=%s' % database_user,
                          '--encoding=UTF8'])
    if template:
        createdb_args.append('--template=%s' % template)

    createdb_command = ['createdb'] + createdb_args

    return subprocess.call(createdb_command)


class Command(BaseCommand):
    help = u"Rebuild the database"

    option_list = BaseCommand.option_list + (
        make_option('-b', '--backup', action='store_true', dest='backup',
                    help='Makes a backup of the current database. True by default'),
        make_option('-t', '--template', dest='template',
                    help='Use a db template while creating database'),
        make_option('-B', '--no-backup', action='store_false', dest='backup',
                    help='Wipe out the database without doing backups. Only for brave or stupid people'),
        make_option('-N', '--noinput', action='store_false', dest='interactive',
                    help='Do not prompt the user for input of any kind. True by default'),
        )

    args = "fixture [fixture ...]"

    def handle(self, *fixtures, **options):
        # read options
        from django.db import connection
        connection.close()

        backup = options.get('backup', True)
        if backup is None:
            backup = True

        interactive = options.get('interactive', True)
        if interactive is None:
            interactive = True

        template = options.get('template', '')

        # make the backup
        if interactive:
            default_answer = backup and 'yes' or 'no'
            answer = self.ask_yesno_question('Would you like to make a database backup? (Highly recomended!)',
                                             default_answer)
            backup = answer == 'yes' and True or False

        # send pre rebuild db signal
        pre_rebuild_db.send(sender=self)

        if backup:
            call_command('backupdb')

        print 'Dropping the database ...',
        ret = execute_drop_database()

        if ret != 0:
            print '\nERROR: There was an error while dropping the database'
            if interactive:
                answer = self.ask_yesno_question('Do you want to follow with this command?', 'no')
                if answer != 'yes':
                    return
            else:
                return
        print 'Done'

        print 'Creating the database ...'
        ret = execute_create_database(template)

        if ret != 0:
            print
            print 'ERROR: There was an error while creating the database'
            return
        print 'Done'

        # send post rebuild db before syncdb signal
        post_rebuild_db_before_syncdb.send(sender=self)

        # create the tables
        call_command('syncdb', interactive=False)

        # migrate schemas with south
        if HAS_SOUTH:
            call_command('migrate', interactive=False)

        # load the fixtures
        if interactive:
            question = 'What fixtures do you want to install?'
            fixtures = ask_for_fixtures(question)

        if fixtures:
            for fixture in fixtures:
                call_command('loaddata', fixture)

        if "group_admin_perms" in get_commands():
            call_command("group_admin_perms")

        # send post rebuild db signal
        post_rebuild_db.send(sender=self)

    def ask_yesno_question(self, question, default_answer):
        while True:
            prompt = '%s: (yes/no) [%s]: ' % (question, default_answer)
            answer = raw_input(prompt).strip()
            if answer == '':
                return default_answer
            elif answer in ('yes', 'no'):
                return answer
            else:
                print 'Please answer yes or no'


def get_available_fixtures():
    result = []
    for fix_dir in settings.FIXTURE_DIRS:
        files = [os.path.basename(f)
                 for f in glob.glob(os.path.join(fix_dir, '*.xml'))]
        result.extend(files)

    # remove duplicates
    result = set(result)
    if 'initial_data.xml' in result:
        result.remove("initial_data.xml")
    result = list(result)
    result.sort()
    return result


def ask_for_fixtures(question='What fixtures do you want to use?'):
    fixtures = get_available_fixtures()
    if fixtures:
        print 'The following fixtures were found in your project:'
        print '\t0. No fixtures, thanks'
        for i, fixture in enumerate(fixtures):
            print '\t%d. %s' % (i + 1, fixture)
        while True:
            prompt = question + ' [1]: '
            answer = raw_input(prompt).strip()
            if answer == '':
                return [fixtures[0]]
            else:
                try:
                    index = int(answer) - 1
                    if index < 0:
                        return []
                    elif index > len(fixtures):
                        print 'That is not a valid fixture number'
                    else:
                        return [fixtures[index]]
                except ValueError:
                    print 'Please write a number'
