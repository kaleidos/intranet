from django import template
from django.db.models.query import QuerySet

register = template.Library()

class GetCountNode(template.Node):
    def __init__(self, list_var, context_var):
        self.list_var = template.Variable(list_var)
        self.context_var = context_var

    def render(self, context):
        object_list = self.list_var.resolve(context)
        if isinstance(object_list, QuerySet):
            list_count = object_list.count()
        else:
            list_count = len(object_list)
        context[self.context_var] = int(list_count)
        return ''

@register.tag(name="get_count")
def do_get_count(parser, token):
    """
    Retrieves the object count from a list or a queryset
    and stores it in a context variable.

    Syntax::

        {% get_count [queryset_or_list] as [varname] %}

    Example::

        {% get_count my_list as list_count %}

    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return GetCountNode(bits[1], bits[3])

@register.filter
def partition(thelist, n):
    """
    From this snippet:
       http://www.djangosnippets.org/snippets/6/

    Break a list into ``n`` pieces. The last list may be larger than the rest if
    the list doesn't break cleanly. That is::

        >>> l = range(10)

        >>> partition(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> partition(l, 3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]

        >>> partition(l, 4)
        [[0, 1], [2, 3], [4, 5], [6, 7, 8, 9]]

        >>> partition(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

    Usage::

    {% load listutil %}
    {% for sublist in mylist|partition:"3" %}
        {% for item in mylist %}
            do something with {{ item }}
        {% endfor %}
    {% endfor %}
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    p = len(thelist) / n
    return [thelist[p*i:p*(i+1)] for i in range(n - 1)] + [thelist[p*(i+1):]]

@register.filter
def partition_horizontal(thelist, n):
    """
    From this snippet:
       http://www.djangosnippets.org/snippets/6/

    Break a list into ``n`` peices, but "horizontally." That is, 
    ``partition_horizontal(range(10), 3)`` gives::

        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9],
         [10]]

    Clear as mud?
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    newlists = [list() for i in range(n)]
    for i, val in enumerate(thelist):
        newlists[i%n].append(val)
    return newlists