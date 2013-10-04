from django import template
from django.conf import settings
from django.utils.translation import get_language

register = template.Library()


## ("short format", "long format") as strptime format
DATEFORMAT_TRANSLATIONS_DEFAULT = {
    'es': ("%d/%m/%Y", ),
    'fr': ("%d/%m/%Y", ),
    'en': ("%Y-%m-%d", ),
    'de': ("%d.%m.%Y", ),
}

DATEFORMAT_MAP = {
    'short': 0,
#    'long': 1,
}


def get_date_format(format, showtime=False):
    formatindex = DATEFORMAT_MAP[format]
    lang = get_language()
    dateformats = getattr(settings, 'DATEFORMAT_TRANSLATIONS', DATEFORMAT_TRANSLATIONS_DEFAULT)
    if lang in dateformats:
        datetimeformat = dateformats[lang][formatindex]
    else:
        datetimeformat = dateformats[settings.LANGUAGE_CODE][formatindex]

    if showtime:
        datetimeformat += " %H:%M"

    return datetimeformat


@register.filter
def transdate(value, format='short'):
    """
    User transdate to translate a date to language session selected
    (year/month/day) format.

    Usage:

      {% load datefilters %}
      {{ datefield|transdate }}

    """
    if value:
        format = get_date_format(format)
        return value.strftime(format)


@register.filter
def transdatetime(value, format='short'):
    """
    User transdate to translate a date to language session selected
    (year/month/day) format.

    Usage:

      {% load datefilters %}
      {{ datefield|transdate }}

    """
    if value:
        dateformat = get_date_format(format, showtime=True)
        return value.strftime(dateformat)
