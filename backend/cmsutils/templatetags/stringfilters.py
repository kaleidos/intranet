from htmlentitydefs import name2codepoint
import re

from django import template

register = template.Library()

@register.filter
def truncatechars(value, arg):
    """
    Truncate chars in a string

    Usage:

      {% load stringfilters %}
      {{ foo_value|truncatechars:"50" }}

    """
    limit = int(arg)
    value = unicode(value)
    if len(value) >= limit:
        return u'%s...' % value[0:max(0, limit-3)]
    return value

entity_re = re.compile(r'&(?:amp;)?#?(?P<name>\w+);')

def _replace_entity(match):
    name = match.group('name')
    if name in name2codepoint:
        return unichr(name2codepoint[name])
    elif name.isdigit():
        return unichr(int(name))
    else:
        return u'?'

@register.filter
def entity2unicode(value):
    """Convert HTML entities to their equivalent unicode character.

    Usage:

        {% load stringfilters %}
        {{ html_text_var|striptags|entity2unicode }}

    """
    return entity_re.sub(_replace_entity, value)
