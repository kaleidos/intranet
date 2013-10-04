
from django.forms.widgets import Widget
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class NumbersSelectionWidget(Widget):
    def __init__(self, choices, attrs=None, renderer=lambda x: mark_safe(u'\n'.join(x))):
        super(NumbersSelectionWidget, self).__init__(attrs)
        self.choices = choices

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        output = []

        output.append('<table width=200>')
        output.append('<tr>')
        for i, d in enumerate(self.choices):
            output.append('<td>%s</td>' % unicode(i+1))
        output.append('</tr>')
        output.append('<tr>')

        days = value.split(',')
        #New imputation
        if len(days) == 1:
            days = []
        #Change imputation to new month with more days
        if len(days) < len(self.choices):
            days = days + (len(self.choices) - len(days))*[0]

        has_id = attrs and 'id' in attrs
        for i, v in enumerate(self.choices):
            final_attrs = self.build_attrs(attrs, type='input', name=name)
            final_attrs['value'] = force_unicode(days[i])
            if has_id:
                final_attrs['id'] = '%s_%s' % (attrs['id'], v)
            output.append(u'<td><input %s style="width: 12px;" title="%s"/></td>' % (flatatt(final_attrs), final_attrs['value']))

        output.append('</tr>')
        output.append('</table>')
        return mark_safe(u'\n'.join(output))

    def value_from_datadict(self, data, files, name):
        values = data.getlist(name)
        return ','.join(values) if values else ''
