from optparse import make_option

from django.core.management.base import BaseCommand

from cmsutils.docfilters import extract_objects

class Command(BaseCommand):
    help = "Index documents of a model"
    option_list = BaseCommand.option_list + (
        make_option('--application', action='store', dest='application'),
        make_option('--model', action='store', dest='model'),
        make_option('--field', action='store', dest='field'),
        make_option('--indexed', action='store', dest='indexed'),
        )

    def handle(self, *args, **options):
        from django.db.models import get_model

        application_name = options.get('application')
        model_name = options.get('model')
        field_name = options.get('field')

        model = get_model(application_name, model_name)

        indexed = options.get('indexed', None)
        filters = {'%s__isnull' % field_name: False}
        if indexed is not None:
            filters[indexed] = False
        queryset = model.objects.filter(**filters)
        extract_objects(queryset, field_name, buffered_output=False)
