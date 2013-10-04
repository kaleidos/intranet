from htmlentitydefs import name2codepoint
import re

from django import template

register = template.Library()

from cmsutils.tag_utils import parse_args_kwargs_and_as_var, \
                               RenderWithArgsAndKwargsNode


@register.tag
def urlize(parser, token):
    """
    Fix http prefix on url, take the value as default url tag content. You can 
      add "a" tag properties the first arg is take as length to crop the tag 
      content (visible value).
    For truncate long urls, you can specific the max leng visible chars

    Usage:

      {% load html_tags %}
      {% urlize content.url 50 target="_blank",rel="nofollow" %}

    """
    args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
    return Urlize(args, kwargs, 'cmsutils/urlize.html')

class Urlize(RenderWithArgsAndKwargsNode):
    def prepare_context(self, args, kwargs, context):
        # return prepared context for rendering
        url = args[0]
        if len(args) > 1:
            limit = args[1]
        else:
            limit = None
        url_label = url

        if url.startswith('http://') or url.startswith('https://'):
            if kwargs.get('hide_protocol', ''):
                if url.startswith('http://'):
                    url_label = url_label.replace('http://', '')
                else:
                    url_label = url_label.replace('https://', '')
                del kwargs['hide_protocol']
            url_href = url
        else:
            url_href = 'http://' + url

        if limit and len(url_label) > limit:
            url_label = url_label[:limit-3] + '...'

        return {'request': context.get('request', None),
                'url_label': url_label,
                'url_href': url_href,
                'attributes':kwargs}
