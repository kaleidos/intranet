# -*-  coding: utf-8 -*-
import re

from django import forms
from django.forms import fields
from django.utils import simplejson as json
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from cmsutils.forms import widgets
from cmsutils.map_utils import MapPosition

__all__ = (
    'SlugField',
    'ButtonField',
    'ESCCCField',
    'LatitudeLongitudeField',
)

slug_re = re.compile(r'^[-\w]+$')


class SlugField(fields.CharField):
    def clean(self, value):
        value = super(SlugField, self).clean(value)
        if value is None:
            return None
        if not slug_re.search(value):
            raise forms.ValidationError, ugettext(u"This value must contain only letters, numbers, underscores or hyphens.")
        else:
            return value


class ButtonField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.widget = widgets.ButtonWidget()
        if kwargs.get('button_label',None):
            self.widget.set_button_label(kwargs['button_label'])
            del(kwargs['button_label'])
        forms.Field.__init__(self, *args, **kwargs)

    def clean(self, value):
        return None # always validates :-)

    def widget_attrs(self, widget):
        return {'label': self.label}


class SpanishDateField(fields.DateField):
    def __init__(self, input_formats=None, *args, **kwargs):
        super(SpanishDateField, self).__init__(*args, **kwargs)
        self.input_formats = ('%d/%m/%Y', ) + (input_formats or fields.DEFAULT_DATE_INPUT_FORMATS)


class SpanishDateTimeField(fields.DateTimeField):
    def __init__(self, input_formats=None, *args, **kwargs):
        super(SpanishDateTimeField, self).__init__(*args, **kwargs)
        self.input_formats = ('%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M' ) + (input_formats or fields.DEFAULT_DATETIME_INPUT_FORMATS)
        self.widget = widgets.SpanishSplitDateTimeWidget()

    def clean(self, value):
        if isinstance(value, list):
            if len(value) == 2:
                if not value[0] and not value[1]:
                    value=''
                elif not value[1]:
                    value=value[0]
        return super(SpanishDateTimeField, self).clean(value)

spanish_phone_re = re.compile(r'^(6|8|9)\d{8}$')

class ESPhoneNumberField(fields.RegexField):
    """
    A form field that validates its input as a Spanish phone number.
    Information numbers are ommited. This is a slightly modified version
    of django.contrib.localflavor.es.forms.ESPhoneNumberField that
    removes the min_length and max_length parameters at __init__.

    Spanish phone numbers are nine digit numbers, where first digit is 6 (for
    cell phones), 8 (for special phones), or 9 (for landlines and special
    phones).

    """
    default_error_messages = {
        'invalid': _(u'Enter a valid phone number in one of the formats 6XXXXXXXX, '
                     u'8XXXXXXXX or 9XXXXXXXX.'),
    }

    def __init__(self, *args, **kwargs):
        super(ESPhoneNumberField, self).__init__(r'^(6|8|9)\d{8}$', *args, **kwargs)

class MultipleESPhoneNumberField(fields.CharField):
    """
    A form field that validates its input as multiple Spanish phone numbers,
    separated by hyphen (-), slash (/), comma (,) and/or whitespace.

    Spanish phone numbers are nine digit numbers, where first digit is 6 (for
    cell phones), 8 (for special phones), or 9 (for landlines and special
    phones)

    This field is based on django.contrib.localflavor.es.forms.ESPhoneNumberField.

    """
    default_error_messages = {
        'invalid': _('Spanish phone numbers must come in one of the formats '
                     '6XXXXXXXX, 8XXXXXXXX or 9XXXXXXXX.'),
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', ugettext(u'Separate numbers with hyphens, slashes, commas or spaces.'))
        super(MultipleESPhoneNumberField, self).__init__(*args, **kwargs)

    def clean(self, value):
        import string
        phones = str(value).translate(string.maketrans('-/, ', '    ')).split()
        for phone in phones:
            if not spanish_phone_re.match(phone):
                raise forms.ValidationError(self.error_messages['invalid'])
        return value


class ESCCCField(forms.RegexField):
    """
    A form field that validates its input as a Spanish bank account or CCC
    (Codigo Cuenta Cliente).

    This field exists in django.contrib.localflavor.es.forms, but it had a bug
    regarding the max_length parameter in __init__ that conflicted with the
    definition of cmsutils.db.fields.ESCCCField.
    """
    default_error_messages = {
        'invalid': _('Please enter a valid bank account number in format XXXX-XXXX-XX-XXXXXXXXXX.'),
        'checksum': _('Invalid checksum for bank account number.'),
    }

    def __init__(self, *args, **kwargs):
        super(ESCCCField, self).__init__(r'^\d{4}[ -]?\d{4}[ -]?\d{2}[ -]?\d{10}$',
            min_length=None, *args, **kwargs)

    def clean(self, value):
        super(ESCCCField, self).clean(value)
        if value in forms.fields.EMPTY_VALUES:
            return u''
        control_str = [1, 2, 4, 8, 5, 10, 9, 7, 3, 6]
        m = re.match(r'^(\d{4})[ -]?(\d{4})[ -]?(\d{2})[ -]?(\d{10})$', value)
        entity, office, checksum, account = m.groups()
        get_checksum = lambda d: str(11 - sum([int(digit) * int(control) for digit, control in zip(d, control_str)]) % 11).replace('10', '1').replace('11', '0')
        if get_checksum('00' + entity + office) + get_checksum(account) == checksum:
            return value
        else:
            raise forms.ValidationError, self.error_messages['checksum']


class LatitudeLongitudeField(forms.Field):
    """Latitude and longitude input, in one field. It validates that input are
    decimal numbers in the allowed range (-90.0 to 90.0 for latitude and
    -180.0 to 180.0 for longitude).

    This field can be used along with cmsutils.widgets.GoogleMapsWidget.

    """

    default_error_messages = {
        'fields': _(u'Input must be exactly two comma-separated decimal numbers.'),
        'float': _(u'At least one data is not a decimal number.'),
        'latitude': _(u'Latitude must be a decimal number between -90.0 and 90.0.'),
        'longitude': _(u'Longitude must be a decimal number between -180.0 and 180.0.'),
    }

    def clean(self, value):
        super(LatitudeLongitudeField, self).clean(value)
        if value in forms.fields.EMPTY_VALUES:
            return u''
        if isinstance(value, unicode):
            if ',' not in value:
                raise forms.ValidationError, self.error_messages['fields']
            split_list = value.split(',')
            if len(split_list) != 2:
                raise forms.ValidationError, self.error_messages['fields']
            a, b = value.split(',')
        elif isinstance(value, list) or isinstance(value, tuple):
            if len(value) != 2:
                raise forms.ValidationError, self.error_messages['fields']
            a, b = value
        elif isinstance(value, MapPosition):
            a, b = value.latitude, value.longitude
        else:
            raise forms.ValidationError, self.error_messages['fields']

        try:
            lat, lng = float(a), float(b)
        except ValueError:
            raise forms.ValidationError, self.error_messages['float']

        if lat < -90.0 or lat > 90.0:
            raise forms.ValidationError, self.error_messages['latitude']
        if lng < -180.0 or lng > 180.0:
            raise forms.ValidationError, self.error_messages['longitude']

        return u"%f,%f" % (lat, lng)


class ColorField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 16)
        self.widget = widgets.ColorPickerWidget()
        super(ColorField, self).__init__(*args, **kwargs)


class JSONFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        defaults = {'widget': widgets.JSONWidget}
        defaults.update(**kwargs)
        super(JSONFormField, self).__init__(*args, **defaults)

    def clean(self, value):
        if not value:
            return
        if isinstance(value, basestring):
            try:
                value = json.loads(value)
            except Exception, exc:
                raise forms.ValidationError(u'JSON decode error: %s' % (unicode(exc),))
        return value
