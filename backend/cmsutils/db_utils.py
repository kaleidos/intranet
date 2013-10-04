import os
import time
import tempfile

from django.conf import settings
from django.core.management import call_command
from django.db import connection


def do_backupdb(backup_dir=None, updatelink=False):
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        engine = settings.DATABASES['default']['ENGINE']
        db = settings.DATABASES['default']['NAME']
        password = settings.DATABASES['default']['PASSWORD']
    else:
        engine = settings.DATABASE_ENGINE
        db = settings.DATABASE_NAME
        password = settings.DATABASE_PASSWORD

    if not backup_dir:
        backup_dir = tempfile.gettempdir()

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    outfile = os.path.join(backup_dir, 'backup_%s.sql' % time.strftime('%y%m%d%S'))
    args = get_args(engine, db)
    if 'mysql' in engine:
        print 'Doing Mysql backup to database %s into %s' % (db, outfile)
        do_mysql_backup(args, outfile)
    elif is_postgresql(engine):
        print 'Doing Postgresql backup to database %s into %s' % (db, outfile)
        do_postgresql_backup(args, password, outfile)
    else:
        print 'Backup in %s engine not implemented' % engine
    if updatelink:
        lastlink = os.path.join(backup_dir, 'lastbackup.sql')
        print 'Doing a symlink %s to %s' % (lastlink, outfile)
        realpath_outfile = os.path.realpath(outfile)
        if os.path.islink(lastlink):
            os.remove(lastlink)
        os.symlink(realpath_outfile, lastlink)
    return outfile


def get_args(engine, db):
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        db = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        passwd = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
    else:
        db = settings.DATABASE_NAME
        user = settings.DATABASE_USER
        passwd = settings.DATABASE_PASSWORD
        host = settings.DATABASE_HOST
        port = settings.DATABASE_PORT
    if 'mysql' in engine:
        return mysql_args(db, user, passwd, host, port)
    elif is_postgresql(engine):
        return postgresql_args(db, user, passwd, host, port)
    return []


def mysql_args(db, user, passwd, host, port):
    args = []
    if user:
        args += ["--user=%s" % user]
    if passwd:
        args += ["--password=%s" % passwd]
    if host:
        args += ["--host=%s" % host]
    if port:
        args += ["--port=%s" % port]
    args += [db]
    return args


def do_mysql_backup(args, outfile):
    if getattr(settings, 'SCRIPT_BACKUPDB', None):
        os.system('%s %s %s' % (settings.SCRIPT_BACKUPDB, ' '.join(args), outfile))
    else:
        os.system('mysqldump %s > %s' % (' '.join(args), outfile))


def postgresql_args(db, user, passwd, host, port):
    args = []
    if user:
        args += ["--username=%s" % user]
    if passwd:
        args += ["--password"]
    if host:
        args += ["--host=%s" % host]
    if port:
        args += ["--port=%s" % port]
    if db:
        args += [db]
    return args


def do_postgresql_backup(args, passwd, outfile):
    import pexpect
    args = ' '.join(args)
    if getattr(settings, 'SCRIPT_BACKUPDB', None):
        os.system('%s %s %s' % (settings.SCRIPT_BACKUPDB, ' '.join(args), outfile))
    else:
        cmd = 'pg_dump %s' % args
        if passwd:
            child = pexpect.spawn(cmd, timeout=1000)
            child.expect("\s*:")  # pg_dump ask for the password here
            child.sendline(passwd)

            child.expect(pexpect.EOF)
            file(outfile, "w").write(child.before)
            child.close()
        else:
            os.system('%s > %s' % (cmd, outfile))


def set_backup(db):
    # Depend of django-extension
    call_command('reset_db', interactive=False)
    cursor = connection.cursor()
    cursor.execute(db)


def _set_autocommit(connection):
    """
    Make sure a connection is in autocommit mode.
    """
    if hasattr(connection.connection, "autocommit"):
        connection.connection.autocommit(True)
    elif hasattr(connection.connection, "set_isolation_level"):
        connection.connection.set_isolation_level(0)


def is_postgresql(engine):
    return 'postgresql_psycopg2' in engine or 'postgresql' in engine or 'postgis' in engine
