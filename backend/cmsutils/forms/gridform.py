from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.encoding import force_unicode

class GridForm(forms.Form):
    layout = None

    def _single_html_output(self, name, field, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        """
        Original _html_output but used to process just one field, specified as parameter

        name: name of the field to process
        field: Field instance of the field to process
        """
        "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        bf = forms.forms.BoundField(self, field, name)
        bf_errors = self.error_class([escape(error) for error in bf.errors]) # Escape and cache in local variable.
        if bf.is_hidden:
            if bf_errors:
                top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
            hidden_fields.append(unicode(bf))
        else:
            if errors_on_separate_row and bf_errors:
                output.append(error_row % force_unicode(bf_errors))
            if bf.label:
                label = escape(force_unicode(bf.label))
                # Only add the suffix if the label does not end in
                # punctuation.
                if self.label_suffix:
                    if label[-1] not in ':?.!':
                        label += self.label_suffix
                label = bf.label_tag(label) or ''
            else:
                label = ''
            if field.help_text:
                help_text = help_text_html % force_unicode(field.help_text)
            else:
                help_text = u''
            output.append(normal_row % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))

    def as_grid(self):
        """
        Renders form as a table, using layout variable to define columns and
        attributes.
        Generated html adds "required" class to cells containing required fields
        """
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'layout'):
            return super(GridForm, self).as_table()
        else:
            output = []
            for fieldset in self.Meta.layout:
                if fieldset.has_key('name'):
                    output.append('<h2>%s</h2>' % unicode(fieldset['name']))
                table_attrs = ''
                if fieldset.has_key('class'):
                    table_attrs = forms.util.flatatt({'class': fieldset['class']})
                output.append('<table%s>' % table_attrs)
                for row in fieldset['fields']:
                    output.append('<tr>')
                    for field in row:
                        if field:
                            td_attrs = {}
                            if hasattr(field, 'attrs') and isinstance(field.attrs, dict):
                                td_attrs = field.attrs.copy()
                            if self.fields[field].required:
                                if td_attrs.has_key('class'): 
                                    td_attrs['class'] += ' required'
                                else:
                                    td_attrs['class'] = 'required'
                            output.append(self._single_html_output(
                                field, # name
                                self.fields[field], # field
                                u'<td' + forms.util.flatatt(td_attrs) + '>%(label)s%(field)s%(errors)s%(help_text)s</td>', # normal_row
                                u'%s', # error_row
                                u'</td>', # row_ender
                                u' %s', # help_text_html
                                False # errors_on_separate_row
                            ))
                        else:
                            output.append('<td></td>')
                    output.append('</tr>')
                output.append('</table>')
            return '\n'.join(output)

    __unicode__ = as_grid

class GridModelForm(forms.ModelForm, GridForm):
    __metaclass__ = type('GridModelFormMetaclass', (forms.models.ModelFormMetaclass, forms.forms.DeclarativeFieldsMetaclass), {})

def addattr(field, attrs):
    UnicodeAndAttrs = type('UnicodeAndAttrs', (unicode,), dict(attrs=attrs))
    return UnicodeAndAttrs(field)

"""
    Usage example and code for testing this module
"""
if __name__ == '__main__':
    class MyForm(GridForm):
        field1 = forms.CharField(max_length=100, required=True)
        field2 = forms.IntegerField(required=True)
        field3 = forms.CharField(max_length=100, required=False)
        field4 = forms.CharField(max_length=100, required=False)

        class Meta:
            layout = (
                { 'name': 'Fieldset 1',
                    'fields': (
                        (addattr('field1', dict(colspan=2)), 'field3'),
                        (None, None, 'field2'),
                    ),
                    'class': 'firstfieldset highlight',
                },
                { 'name': 'Fieldset 2',
                    'fields': (
                        ('field4',),
                    ),
                    'class': 'secondfieldset',
                },
            )
    form = MyForm()
    print unicode(form)

