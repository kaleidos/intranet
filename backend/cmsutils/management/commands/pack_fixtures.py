import copy
from optparse import make_option
import os.path
import tarfile
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand

from cmsutils.management.commands.rebuild_db import ask_for_fixtures


def get_default_excludes():
    if hasattr(settings, 'FIXTURES_EXCLUDES'):
        return list(settings.FIXTURES_EXCLUDES)
    else:
        return []


class Command(BaseCommand):
    help = u'Pack fixtures and their media files'

    option_list = BaseCommand.option_list + (
        make_option('-e', '--exclude', dest='exclude', action='append',
                    default=get_default_excludes(),
                    help=('Apps to exclude (use multiple --exclude to '
                          'exclude multiple apps). Use app.model to '
                          'exclude specific models of an app')),
        make_option('-N', '--noinput', action='store_false',
                    dest='interactive', default=True,
                    help='Do not prompt the user for input of any kind'),
        )

    args = 'output_file [fixture_name fixture_name ..]'

    def handle(self, *args, **options):
        if not args or len(args) < 1:
            raise CommandError("Enter exactly one output file")

        output_file = args[0]
        fixtures = args[1:]

        exclude = options.get('exclude')
        interactive = options.get('interactive')
        verbosity = options.get('verbosity')

        if interactive:
            fixtures = ask_for_fixtures()

        data = []

        for fixture_dir in settings.FIXTURE_DIRS:
            app_name = fixture_dir.split('/')[-1]
            if app_name in exclude:
                continue

            item = {'app': app_name, 'fixtures': [], 'files': []}

            for fixture_name in fixtures:
                if not fixture_name.endswith('.xml'):
                    fixture_name += '.xml'
                filename = os.path.join(fixture_dir, fixture_name)
                item['fixtures'].append(filename)

                if verbosity > 0:
                    print 'Parsing %s ...' % filename,
                files = get_media_files(filename)
                if verbosity > 0:
                    print '%d files were found' % len(files)
                item['files'].extend(files)

            data.append(item)

        if verbosity > 0:
            print 'Packing data into the file', output_file
        pack_data(output_file, data, verbosity)


def get_media_files(fixture_file):
    parser = make_parser()
    handler = FileFieldSniffer()
    parser.setContentHandler(handler)
    parser.parse(open(fixture_file))
    return handler.files


class FileFieldSniffer(ContentHandler):

    def __init__(self):
        self.files = []
        self.inside_file_field = False
        self.current_file_value = ''

    def startElement(self, name, attrs):
        if name == 'field' and attrs.get('type', '') == 'FileField':
            self.inside_file_field = True

    def endElement(self, name):
        if name == 'field' and self.inside_file_field:
            if self.current_file_value:
                self.files.append(copy.copy(self.current_file_value))
            self.current_file_value = ''
            self.inside_file_field = False

    def characters(self, ch):
        if self.inside_file_field:
            self.current_file_value += ch


def pack_data(output_file, data, verbosity):
    media_name = os.path.basename(os.path.dirname(settings.MEDIA_ROOT))
    output = tarfile.open(output_file, 'w:bz2')
    for item in data:
        app_name = item['app']
        fixtures = item['fixtures']
        files = item['files']
        for fixture in fixtures:
            if verbosity > 0:
                print 'Adding fixture', fixture
            basename = os.path.basename(fixture)
            fixture_path = os.path.join('fixtures', app_name, basename)
            output.add(fixture, fixture_path)

        for file in files:
            if verbosity > 1:
                print 'Adding file', file

            real_path = os.path.join(settings.MEDIA_ROOT, file)
            if os.path.exists(real_path):
                file_path = os.path.join(media_name, file)
                output.add(real_path, file_path)
            else:
                print 'ERROR: The file %s does not exist' % real_path

    output.close()
