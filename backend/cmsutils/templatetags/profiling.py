from django.conf import settings
from django.template import Library

register = Library()

def debugqueries(context):
    """ Shows sql queries using in page rendering.
        You can put this to the end of you base template

        Note: only works with these settings::

         DEBUG = True
         INTERNAL_IPS = ('127.0.0.1',) # or whatever

        Example::

         ...
         {% load profiling %}
         {% debugqueries %}
         </body>

        Note: taken from this snippet::
            http://www.djangosnippets.org/snippets/93/
    """
    if not settings.DEBUG:
        return {}
    return {'debug': context.get('debug', None),
            'sql_queries': context.get('sql_queries', None)}
debugqueries = register.inclusion_tag('cmsutils/debugqueries.html',
                                      takes_context=True)(debugqueries)