from django import template
from django.utils.translation import ugettext as _

from cmsutils.models import Parameter

register = template.Library()

@register.simple_tag
def param(param_name):
    """Return the value of the parameter 'param_name'"""
    try:
        param = Parameter.objects.get(name=param_name)
    except Parameter.DoesNotExist:
        return _(u'There is no parameter with name %s' % param_name)
    return param.value
