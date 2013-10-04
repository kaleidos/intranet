from django.template import Library
from django.utils.translation import ugettext as _
import calendar
from intranet import models
import locale
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

register = Library()


@register.filter
def sum(parts, project):
    sum = 0
    sum_raw = 0
    sum_chargeability = 0
    sum_profit = 0
    sum_real = 0

    for part in parts:
        sum += part.total_hours(project.id)
        sum_raw += part.raw_cost(project.id)
        sum_chargeability += part.chargeability_cost(project.id)
        sum_profit += part.profit_cost(project.id)
        sum_real += part.real_cost(project.id)
    return (sum, sum_raw, sum_chargeability, sum_profit, sum_real)


@register.filter
def total_hours(part, project):
    return part.total_hours(project.id)


@register.filter
def raw_cost(part, project):
    return part.raw_cost(project.id)


@register.filter
def chargeability_cost(part, project):
    return part.chargeability_cost(project.id)


@register.filter
def profit_cost(part, project):
    return part.profit_cost(project.id)


@register.filter
def real_cost(part, project):
    return part.real_cost(project.id)


@register.filter
def negative(value):
    return -1 * value


@register.filter
def pretty_name(user):
    if user.first_name:
        return u"%s %s" % (user.first_name, user.last_name)
    else:
        return user.username


@register.filter
def month_name(month_number):
    return _(calendar.month_name[month_number])


@register.filter
def hash(h, key):
    return h[key]


@register.filter()
def currency(value):
    if not value:
        value = 0
    return locale.currency(value, grouping=True)


@register.filter
def project_name(project_id):
    return models.Project.objects.get(id=project_id).name
