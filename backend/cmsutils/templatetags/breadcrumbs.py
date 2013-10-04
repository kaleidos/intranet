from django import template
from django.utils.translation import ugettext as _

register = template.Library()

@register.tag
def breadcrumbs(parser, token):
    """Tag for rendering breadcrumbs.

    Syntax:
    {% breadcrumbs item1[:url1][:max_words] item2[:url2][:max_words] ... itemN[:urlN][:max_words] %}

    Each item will be resolved in the context before rendering. If an object
    is found its unicode representation will be used as the title and its
    get_absolute_url method will be called for the url in case no url was
    provided.

    The optional max_words clause will truncate each breadcrumbs part.
    """
    contents = token.split_contents()
    items = []
    for item in contents[1:]:
        if (item[0] == item[-1] and item[0] in ('"', "'")):
            item = item[1:-1]
        title = item
        url = None
        max_words = None
        if ':' in item:
            parts = item.split(':')
            if len(parts) == 2:
                title, url = parts
            elif len(parts) == 3:
                title, url, max_words = parts
                max_words = int(max_words)
            else:
                raise template.TemplateSyntaxError("You can not put more than "
                                                   "two colons in a breadcrumb item")
        items.append(dict(title=title, url=url, max_words=max_words))

    return BreadcrumbsNode(items)

class BreadcrumbsNode(template.Node):
    """Template node for the breadcrumbs tag"""
    def __init__(self, items):
        self.items = items

    def render(self, context):
        context.push()
        items = [dict(title=_('Home'), url='/')]
        for item in self.items:
            title = item['title']
            url = item['url']
            max_words = item['max_words']
            variable = template.Variable(title)
            try:
                obj = variable.resolve(context)
                title = unicode(obj)
                if hasattr(obj, 'get_absolute_url') and not url:
                    url = obj.get_absolute_url()
                elif not url:
                    continue
            except template.VariableDoesNotExist:
                title = _(title)
            try:
                url = template.Variable(url).resolve(context)
            except:
                pass
            items.append(dict(title=title, url=url, max_words=max_words))

        context['items'] = items
        tpl = template.loader.get_template('cmsutils/breadcrumbs.html')
        output = tpl.render(context)
        context.pop()
        return output
