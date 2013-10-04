from optparse import make_option
import os.path

from django.db.models import get_app, get_models
from django.conf import settings
from django.core import serializers
from django.core.management.base import CommandError, BaseCommand


def get_default_excludes():
    if hasattr(settings, 'FIXTURES_EXCLUDES'):
        return list(settings.FIXTURES_EXCLUDES)
    else:
        return []


class Command(BaseCommand):
    help = u"Save fixtures from database"

    option_list = BaseCommand.option_list + (
        make_option('--format', default='xml', dest='format',
                    help=('Specifies the output serialization '
                          'format for fixtures.')),
        make_option('--indent', default=2, dest='indent', type='int',
                    help=('Specifies the indent level to use when '
                          'pretty-printing output')),
        make_option('-e', '--exclude', dest='exclude', action='append',
                    default=get_default_excludes(),
                    help=('Apps to exclude (use multiple --exclude to '
                          'exclude multiple apps). Use app.model to '
                          'exclude specific models of an app')),
    )

    args = "<fixture_name fixture_name ...>"

    def handle(self, *fixtures, **options):
        if not fixtures:
            raise CommandError("Enter at least one fixture name")

        format = options.get('format')
        indent = options.get('indent')
        exclude = options.get('exclude')

        show_traceback = options.get('traceback', False)

        for fixture in fixtures:
            self.handle_fixture(fixture, format, indent, exclude,
                                show_traceback)

    def handle_fixture(self, fixture, format, indent, exclude, show_traceback):
        # Check that the serialization format exists
        if format not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % format)
        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)

        filename = '%s.%s' % (fixture, format)
        for d in settings.FIXTURE_DIRS:
            app_name = d.split('/')[-1]
            if app_name in exclude:
                continue

            print ('Saving fixtures for %s application into %s'
                   % (app_name, filename))

            objects = []
            for model in get_models(get_app(app_name)):
                full_name = '%s.%s' % (app_name, model._meta.module_name)
                if full_name not in exclude:
                    objects.extend(model._default_manager.all())

            output = None
            try:
                output = serializers.serialize(format, objects, indent=indent)
            except Exception, e:
                if show_traceback:
                    raise
                raise CommandError("Unable to serialize database: %s" % e)

            if output:
                if not os.path.isdir(d):
                    os.makedirs(d)
                fout = open(os.path.join(d, filename), 'w')
                fout.write(output)
                fout.close()
