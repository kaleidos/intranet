"""
 Command for backup database
"""

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from cmsutils.db_utils import do_backupdb


class Command(BaseCommand):
    help = "Backup database. Only Mysql and Postgresql engines are implemented"

    option_list = BaseCommand.option_list + (
            make_option('-L', '--update-last-link', action='store_true', dest='updatelink',
                    help='update lastbackup.sql symlink on backups/'),
    )
    def handle(self, *args, **options):
        try:
            backup_dir = settings.BACKUP_DIR
        except AttributeError:
            backup_dir = 'backups'
        do_backupdb(backup_dir=backup_dir, updatelink=options.get('updatelink', False))
