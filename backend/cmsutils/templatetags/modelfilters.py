from django.template import Context, Library, Node, TemplateSyntaxError, loader, Variable
from django.db import models
from django.contrib.admin.filterspecs import FilterSpec

from cmsutils.adminfilters import QueryStringManager, MultipleRelatedFilterSpec, FieldAvailabilityValueFilterSpec

register = Library()

class ModelFilterNode(Node):

    def __init__(self, app_name, model_name, field_name, choices_queryset=None, multiselection=True, delete_fields=['page']):
        self.app_name = Variable(app_name)
        self.model_name = Variable(model_name)
        self.field_name = Variable(field_name)
        self.multiselection = multiselection
        if choices_queryset is not None :
            self.choices_queryset = Variable(choices_queryset)
        else:
            self.choices_queryset = None
        self.delete_fields = delete_fields

    def render(self, context):
        filters = []
        request = context['request']
        app_name = self.app_name.resolve(context)
        model_name = self.model_name.resolve(context)
        field_name = self.field_name.resolve(context)
        if self.choices_queryset is not None:
            choices_queryset = self.choices_queryset.resolve(context)
        else:
            choices_queryset = None
        model = models.get_model(app_name, model_name)
        qsm = QueryStringManager(request)
        params = qsm.get_params()
        if params.get('page', None):
            del params['page']
        field = model._meta.get_field(field_name)
        if field.get_internal_type() == 'FileField':
            spec = FieldAvailabilityValueFilterSpec(field, request, params, model, None)
        elif self.multiselection and (field.rel is not None): # is a related field (ForeignKeyField)
            spec = MultipleRelatedFilterSpec(field, request, params, model, None, choices_queryset)
        else: # normal filter spec
            spec = FilterSpec.create(field, request, params, model, None)
        filter_context = {'title': spec.title(), 'choices' : list(spec.choices(qsm))}
        tpl = loader.get_template('admin/filter.html')
        return tpl.render(Context(dict(filter_context, autoescape=context.autoescape)))


def do_filter_for_model(request, token):
    """
    This will create filters like in django admin

    Usage::

        {% filter_for_model app_name model_name field_name [choices_queryset] %}

    Example view::

      def foo_listing(request, ...):
        qsm = QueryStringManager(request)
        queryset = FooModel.objects.all()
        queryset = queryset.filter(qsm.get_filters())
        category_choices = Category.objects.filter(parent__isnull=True)
        render_to_response('foo_listing.html', {'queryset': queryset,
                                              'qsm': qsm,
                                              'category_choices': category_choices} )

    Example template::

    {% load modelfilters %}
    {% filter_for_model 'fooapp' 'foomodel' 'publish_date' %}
    {% filter_for_model 'fooapp' 'foomodel' 'category' category_choices %}

    """
    tokens = token.contents.split()
    if len(tokens) < 4:
        raise TemplateSyntaxError(u"'%r' tag requires at least 3 arguments." % tokens[0])
    app_name, model_name, field_name = tokens[1:4]
    choices_queryset = (len(tokens) >= 5 and not tokens[4] == 'None' and tokens[4]) or None # default for choices is None
    multiselection = len(tokens) < 6 or tokens[5] == 'True' # default True for multiselection
    delete_fields = (len(tokens) >= 7 and tokens[6]) or [] # default for choices is None
    return ModelFilterNode(app_name, model_name, field_name, choices_queryset, multiselection, delete_fields)
register.tag('filter_for_model', do_filter_for_model)

