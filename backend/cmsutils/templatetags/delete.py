from django.template import Library
from django.contrib.contenttypes.models import ContentType

register = Library()

@register.inclusion_tag('cmsutils/delete_link.html', takes_context=True)
def delete_link(context, obj):
    result = {'object_id': None}
    app = obj._meta.app_label
    module = obj._meta.module_name
    if context['request'].user.has_perm("%s.delete_%s" % (app, module)):
        content_type = ContentType.objects.get(app_label=app, model=module)
        result['object_id'] = obj.id
        result['content_type_id'] = content_type.id
    return result
