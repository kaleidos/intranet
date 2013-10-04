"""
Widget classes specific to saludinnova project (based on Community project)
"""

from datetime import datetime
import os

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db import models
from django.db.models.manager import Manager
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils import simplejson as json
from django.utils.simplejson import JSONEncoder
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

try:
    from django.contrib.admin.widgets import AdminSplitDateTime
    _SplitDateTimeWidget = AdminSplitDateTime
except ImportError:
    from django.forms.widgets import SplitDateTimeWidget
    _SplitDateTimeWidget = SplitDateTimeWidget

from cmsutils.map_utils import MapPosition


__all__ = (
    'ButtonWidget',
    'ReadOnlyInput',
    'GoogleMapsWidget',
    'TinyMCE',
    'MySplitDateTimeWidget',
    'AJAXAutocompletionWidget',
)


def load_javascript(src, script_id=None):
    """
    Returns the HTML code to load a javascript file inside the render method of a widget.

    src is the path to the javascript file inside the media/cmsutils/js directory.
    If script_id is None it will be created based in src

    Usage:
        def render():
            head = load_javascript('dir/file.js')
            html = (widget-dependent code)
            return mark_safe("".join([head, html]))
    """
    if not script_id:
        script_id = os.path.basename(src).replace('.', '_')
    js = u"""
    <script type="text/javascript">
        if (!document.getElementById('%(script_id)s')) {
            // if is not loaded yet we create
            var script = document.createElement('script');
            script.id = '%(script_id)s';
            script.src = '%(src)s';
            script.type = 'text/javascript';
            document.getElementsByTagName('head')[0].appendChild(script);
    }</script>
    """ % locals()
    return js


def load_javascript_in_order(script_list, callback=None, suffix=''):
    """
    Returns the HTML code to load a list of javascript files and ensure its execution order.

    A callback function to be executed after all the scripts in the list can be passed as the name of a existing javascript function.
    """
    load_functions_js = u''
    for i in range(len(script_list)):
        id, src = script_list[i]

        try:
            next_id = script_list[i + 1][0]
        except:
            next_id = None
        if next_id:
            next_function = u"load_%s%s" % (next_id, suffix)
            next_else_function_js = u"%s();" % next_function
            next_function_js = u"""
                add_onload(script_%(id)s, %(next_function)s);
            """ % {'next_function': next_function, 'id': id }
        elif callback:
            next_else_function_js = u"%s%s();" % (callback, suffix)
            next_function_js = u"""
                add_onload(script_%(id)s, %(callback)s%(suffix)s);
            """ % {'callback': callback, 'id': id, 'suffix': suffix }
        else:
            next_else_function_js = u''
            next_function_js = u''

        load_functions_js += u"""
        function load_%(id)s%(suffix)s() {
            if (!document.getElementById('%(id)s%(suffix)s')) {
                var script_%(id)s = document.createElement('script');
                script_%(id)s.id = '%(id)s%(suffix)s';
                script_%(id)s.src = '%(src)s';
                script_%(id)s.type = 'text/javascript';
                document.getElementsByTagName('head')[0].appendChild(script_%(id)s);
                %(next_function)s
        """ % {'id': id, 'src': src, 'next_function': next_function_js, 'suffix': suffix}


        load_functions_js += u"""
            }
            else {
                %s
            }
        }
        """ % next_else_function_js

    first_function = """
        function add_onload(element, func) {
                var oldonload = element.onload;
                var oldstc = element.onreadystatechange;
                if (oldonload != 'function') {
                    element.onload = func;
                }
                else {
                    element.onload = function() {
                        oldonload();
                        func();
                    }
                }
                if (oldstc != 'function') {
                    element.onreadystatechange = func;
                }
                else {
                    element.onreadystatechange = function() {
                        oldstch();
                        func();
                    }
                }
        }
    """

    try:
        first_function += u'load_%s%s();' % (script_list[0][0], suffix)
    except:
        pass

    js = u"""
    <script type="text/javascript">
        %s
        %s
    </script>
    """ % (load_functions_js, first_function)
    return js

def load_stylesheet(src, css_id=None):
    """
    Returns the HTML code to load a stylesheet file inside the render method of a widget.

    src is the path to the stylesheet file inside the media/cmsutils/ directory.
    If css_id is None it will be created based in src

    Usage:
        def render():
            head = load_stylesheet('dir/file.css')
            html = (widget-dependent code)
            return mark_safe("".join([head, html]))
    """
    if not css_id:
        css_id = os.path.basename(src).replace('.', '_')
    js = u"""
    <script type="text/javascript">
        if (!document.getElementById('%(css_id)s')) {
            // if is not loaded yet we create
            var link = document.createElement('link');
            link.id = '%(css_id)s';
            link.href = '%(src)s';
            link.rel = 'stylesheet';
            link.type = 'text/css';
            document.getElementsByTagName('head')[0].appendChild(link);
    }</script>
    """ % locals()
    return js

def aff(field_name, model=None, **kwargs):
    """Attributes From Field

    This is a useful function when defining form fields from a model field.
    """
    if isinstance(field_name, basestring):
        field = model._meta.get_field(field_name)
    else:
        field = field_name
    attrs = {'required': not field.blank,
             'label': capfirst(unicode(field.verbose_name)),
             'help_text': field.help_text,
             'max_length': field.max_length}
    if field.choices:
        attrs['widget'] = forms.Select(choices=field.get_choices())
    attrs.update(kwargs)
    return attrs


class ButtonWidget(forms.Widget):
    def set_button_label(self, label):
        self.button_label = label

    def render(self, name, value, attrs=None):
        return u'<button id="%s" type="button">%s</button>' % (attrs['id'],
                                                               self.button_label)


class ReadOnlyInput(widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        attrs['readonly'] = 'readonly'
        return super(ReadOnlyInput, self).render(name, value, attrs)


class ReadOnlyWidget(forms.Widget):

    def __init__(self, original_value, display_value):
        if display_value is None:
            if isinstance(original_value, Manager) and hasattr(original_value, 'all'):
                display_value = u', '.join(
                    [element.__unicode__() for element in original_value.all()])
            else:
                display_value = original_value or u''
        if isinstance(original_value, models.Model):
            original_value = original_value.pk
        self.original_value = original_value
        self.display_value = display_value

        super(ReadOnlyWidget, self).__init__()

    def render(self, name, value, attrs=None):
        return unicode(self.display_value)

    def value_from_datadict(self, data, files, name):
        return self.original_value


class AJAXAutocompletionWidget(forms.widgets.Widget):
    """Widget to aid the selection of one or multiple item from a long list of possible items. Looks similar than a SelectBoxWidget, but the list of possibilities gets filtered as long as you type. The possibilities could be passed through an array or by an url which will be queried using AJAX.

    Info about options can be viewed at: http://docs.jquery.com/Plugins/Autocomplete/autocomplete#url_or_dataoptions

    """

    DEFAULT_ATTRS = {
            'inputClass':   "ac_input",
            'resultsClass': "ac_results",
            'loadingClass': "ac_loading",
            'minChars': 1,
            'delay': 400,
            'matchCase': False,
            'matchSubset': True,
            'matchContains': False,
            'cacheLength': 10,
            'max': 100,
            'mustMatch': False,
            'extraParams': {},
            'selectFirst': True,
            'autoFill': False,
            'width': 0,
            'multiple': False,
            'multipleSeparator': ", ",
            'scroll': True,
            'scrollHeight': 180
        }

    def __init__(self, choices=None, url=None, attrs=None):
        if isinstance(url, str) or isinstance(url, unicode):
            self.is_url = True
            self.url = url
        else:
            self.is_url = False
            self.choices = choices or []
        attrs = attrs or {}
        self.attrs = self.DEFAULT_ATTRS.copy()
        self.attrs.update(attrs)

        self.inner_widget = forms.widgets.TextInput()
        super(AJAXAutocompletionWidget, self).__init__(attrs)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name

        safe_id = final_attrs['id'].replace('-','_').replace('.','_')
        choices = self.is_url and '"%s"' % self.url or JSONEncoder().encode(self.choices)
        autocomplete_js = u"""<script type="text/javascript">
        function autocomplete_%s() {
            $("#%s").autocomplete(%s, %s);
        }
        </script>\n""" % (safe_id,
                          final_attrs['id'],
                          choices,
                          JSONEncoder().encode(final_attrs))

        js_prefix = "%scmsutils/js/widgets/ajaxautocompletion/" % settings.MEDIA_URL
        head = u''.join([load_stylesheet(src='%sjquery.autocomplete.css' % js_prefix, css_id='jquery_autocomplete'),
                         autocomplete_js,
                         load_javascript_in_order([('jquery_js', '%slib/jquery.js' % js_prefix),
                                                   ('jquery_bgiframe_min_js', '%slib/jquery.bgiframe.min.js' % js_prefix),
                                                   ('jquery_dimensions_js', '%slib/jquery.dimensions.js' % js_prefix),
                                                   ('jquery_ajaxqueue_js', '%slib/jquery.ajaxQueue.js' % js_prefix),
                                                   ('jquery_autocomplete_js', '%sjquery.autocomplete.js' % js_prefix),
                                                  ], callback='autocomplete', suffix='_%s' % safe_id)
                        ])

        for k in self.DEFAULT_ATTRS.keys():
            final_attrs.pop(k,None)

        html = self.inner_widget.render("%s" % name, value, final_attrs)
        return mark_safe(u''.join([head, html]))

class GoogleMapsWidget(forms.widgets.Widget):
    """Widget to choose a location's latitude and longitude by clicking and
    moving a mark in a Google Maps map.

    To use the widget the files media/cmsutils/js/event.js and
    media/cmsutils/js/widgets/GoogleMapsWidget.js must be in the media
    directory of the project.

    """

    DEFAULT_ZOOM = 12

    def __init__(self, initial=None, attrs=None):
        attrs = attrs or {}
        self.attrs = {'width': 400, 'height': 247}
        if initial is None:
            # By default centered at Yaco's office
            initial = MapPosition(37.39076, -5.994997, GoogleMapsWidget.DEFAULT_ZOOM)
        self.initial = initial
        self.attrs.update(attrs)

        self.inner_widget = forms.widgets.TextInput()
        self.print_head=True
        super(GoogleMapsWidget, self).__init__(attrs)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name    

        self.zoom = GoogleMapsWidget.DEFAULT_ZOOM

        if value == u"" or value is None:
            a, b = self.initial.latitude, self.initial.longitude
            self.zoom = self.initial.zoom or GoogleMapsWidget.DEFAULT_ZOOM
        elif isinstance(value, unicode):
            a, b = value.split(',')
        elif isinstance(value, list) or isinstance(value, tuple):
            a, b = value
        elif isinstance(value, MapPosition):
            a, b = value.latitude, value.longitude
            self.zoom = value.zoom or GoogleMapsWidget.DEFAULT_ZOOM
        lat, lng = float(a), float(b)

        if self.print_head:
            google_maps_src = "http://maps.google.com/maps?file=api&v=2&key=%s" % settings.MY_GOOGLE_MAPS_API_KEY
            #load_javascript(src=google_maps_src, script_id='gmap_js'),
            head = u''.join([load_javascript(src='%scmsutils/js/event.js' % settings.MEDIA_URL),
                             load_javascript(src='%scmsutils/js/widgets/GoogleMapWidget.js' % settings.MEDIA_URL)])
        else:
            head = u''
        render_value = value and u"%f,%f" % (lat,lng) or u""
        html = self.inner_widget.render("%s" % name, render_value, dict(id='id_%s' % name))
        js = u"""<script type="text/javascript">
            var map_%(name)s = null;
            function loadMap_%(name)s() {
                map_%(name)s = new GoogleMapPositionSelector('id_%(id)s','%(id)s',%(width)d,%(height)d,%(zoom)d,%(latitude)f,%(longitude)f);
            }
            if (typeof multiLoader == "undefined") {
                function multiLoader() {
                    if (GBrowserIsCompatible()) {
                        for (f in multiLoaderArray) {
                            multiLoaderArray[f]();
                        }
                    }
                }
            }
            if (typeof multiLoaderArray == "undefined") {
                var multiLoaderArray = new Array();
            }
            multiLoaderArray.push(loadMap_%(name)s);

            if (typeof caller == "undefined") {
                var caller = 1;
                addEvent(window, "load", function(){
                    var script = document.createElement('script');
                    script.src = '%(src)s&async=2&callback=multiLoader';
                    script.type = 'text/javascript';
                    document.documentElement.firstChild.appendChild(script);
                });
            }
            </script>
            """ % {'name': name.replace('-','_'), 
                   'id': name,
                   'width': final_attrs['width'],
                   'height': final_attrs['height'],
                   'zoom': self.zoom,
                   'latitude': self.initial.latitude,
                   'longitude': self.initial.longitude,
                   'src': google_maps_src,
                  }
        return mark_safe(u''.join([head, html, js]))


class FilteredSelectMultipleWidget(forms.SelectMultiple):
    """
    An enhanced SelectMultiple widget with a JavaScript filter interface, for
    forms MultipleChoice* fields.

    To use the widget the files media/cmsutils/js/widgets/SelectBox.js and
    media/cmsutils/js/widgets/SelectFilter2.js and media/cmsutils/js/widgets/core.js and media/cmsutils/js/event.js must be in the media
    directory of the project.

    Based on django.contrib.admin.widgets.FilteredSelectMultiple

    """

    def __init__(self, verbose_name, is_stacked=False, print_head=True, attrs=None, choices=()):
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
        self.print_head = print_head
        super(FilteredSelectMultipleWidget, self).__init__(attrs, choices)


    def render(self, name, value, attrs=None, choices=()):
        if self.print_head:
            head = u''.join([
                         load_javascript(src='%scmsutils/js/widgets/core.js' % settings.MEDIA_URL),
                         load_javascript(src='%scmsutils/js/event.js' % settings.MEDIA_URL),
                         load_javascript(src='%scmsutils/js/widgets/SelectBox.js' % settings.MEDIA_URL),
                         load_javascript(src='%scmsutils/js/widgets/SelectFilter2.js' % settings.MEDIA_URL)])
        else:
            head = ''
        html = super(FilteredSelectMultipleWidget, self).render(name, value, attrs, choices)
        js = u"""<script type="text/javascript">addEvent(window, "load", function(e) {
            SelectFilter.init("id_%s", "%s", %s, "%s") });</script>
            """ %(name, self.verbose_name.replace('"', '\\"'), int(self.is_stacked), settings.ADMIN_MEDIA_PREFIX)

        return mark_safe(u''.join([head, html, js]))


TINYMCE_JS = settings.MEDIA_URL + "cmsutils/js/widgets/tiny_mce/tiny_mce.js"

class TinyMCE(widgets.Textarea):
    """
    TinyMCE widget.

    You can customize the mce_settings by overwriting instance mce_settings,
    or add extra options using update_settings
    """
    mce_settings = dict(
        mode = "exact",
        theme = "advanced",
        width = "100%",
        height = 400,
        button_tile_map = True,
        plugins = "preview,paste,inplaceedit",
        theme_advanced_disable = "",
        theme_advanced_buttons1 = "undo,redo,separator,cut,copy,paste,pastetext,pasteword,separator,preview,separator,bold,italic,underline,justifyleft,justifycenter,justifyright,bullist,numlist,outdent,indent",
        theme_advanced_buttons2 = "fontselect,fontsizeselect,link,image,code",
        theme_advanced_buttons3 = "",
        theme_advanced_buttons4 = "",
        theme_advanced_toolbar_location = "top",
        theme_advanced_toolbar_align = "left",
        extended_valid_elements = "hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
        file_browser_callback = "mcFileManager.filebrowserCallBack",
        theme_advanced_resize_horizontal = False,
        theme_advanced_resizing = False,
        apply_source_formatting = False,
        editor_deselector  = "mceNoEditor"
    )

    class Media: # this is for django admin interface
        js = (TINYMCE_JS,)

    def __init__(self, extra_mce_settings={}, print_head=False, *args, **kwargs):
        super(TinyMCE, self).__init__(*args, **kwargs)
        self.print_head = print_head
        # copy the settings so each instance of the widget can modify them
        # without changing the other widgets (e.g. instance vs class variables)
        self.mce_settings = TinyMCE.mce_settings.copy()
        self.mce_settings['spellchecker_languages'] = getattr(settings, 'TINYMCE_LANG_SPELLCHECKER', '+English=en')
        self.mce_settings['language'] = getattr(settings, 'TINYMCE_LANG', 'en')
        self.mce_settings.update(extra_mce_settings)

    def update_settings(self, custom):
        return_dict = self.mce_settings.copy()
        return_dict.update(custom)
        return return_dict

    def with_head(self, on=True):
        self.print_head = on

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)

        self.mce_settings['elements'] = "id_%s" % name
        mce_json = JSONEncoder().encode(self.mce_settings)

        # Print script head once per instance
        if self.print_head:
            head = load_javascript(TINYMCE_JS)
        else:
            head = u''

        return mark_safe(u'''<textarea%s>%s</textarea>
                %s
                <script type="text/javascript">tinyMCE.init(%s)</script>''' % (flatatt(final_attrs), escape(value), head, mce_json))


class MySplitDateTimeWidget(widgets.SplitDateTimeWidget):
    def value_from_datadict(self, data, files, name):
        return u' '.join([widget.value_from_datadict(data, files, name + '_%s' % i) for i, widget in enumerate(self.widgets)]).strip()

    def decompress(self, value):
        if value:
            if isinstance(value, basestring):
                return value.split(' ')
            elif isinstance(value, datetime):
                return [value.strftime("%d/%m/%Y"),
                        value.strftime("%H:%M:%S")]
        return [None,None]


class SpanishSplitDateTimeWidget(_SplitDateTimeWidget):
    def decompress(self, value):
        if value:
            return value.strftime('%d/%m/%Y %H:%M:%S').split()
        return [None, None]



class RelatedFieldWidgetWrapperWithViewLink(RelatedFieldWidgetWrapper):
    """Same as the widget for ForeignKey in the admin interface but this adds
    a link button for viewing the related object"""
    
    def render(self, name, value, *args, **kwargs):
        output = super(RelatedFieldWidgetWrapperWithViewLink, self).render(name, value,
                                                                           *args, **kwargs)
        output = [output]
        rel_to = self.rel.to
        if rel_to in self.admin_site._registry and value is not None:
            related_url = '../../../%s/%s/' % (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            output.append(u'<a href="%s%s/" onclick="return showRelatedObjectLookupPopup(this)">' % (related_url, value))
            output.append(u'<img src="%scmsutils/img/icon_view.gif" width="10" height="10" alt="%s"/></a>'
                          % (settings.MEDIA_URL, _("View related object")))
        return mark_safe(u''.join(output))



class WYMEditor(forms.Textarea):
    """
    WYMeditor widget.
    It require explicit jquery.js definition
    """
    
    class Media:
        js = (
            'cmsutils/js/widgets/wymeditor/jquery.wymeditor.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.attrs = {'class': 'wymeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            jQuery('#id_%s').wymeditor({
                updateSelector: '.submit-row input[type=submit]',
                updateEvent: 'click',
                lang: '%s',
            });
            </script>''' % (name, self.language))


class ColorPickerWidget(forms.widgets.Input):
    """
    jquery Color Picker widget
    It require explicit jquery.js definition
    """
    input_type = 'text'

    def __init__(self, print_head=False, language=None, attrs=None):
        self.attrs = {'class': 'colorfield'}
        if attrs:
            self.attrs.update(attrs)
        super(ColorPickerWidget, self).__init__(attrs)


    def render(self, name, value, attrs=None):
        head = u''.join([load_javascript(src='%scmsutils/js/widgets/colorpicker.js' % settings.MEDIA_URL),
                         load_stylesheet(src='%scmsutils/css/widgets/colorpicker.css' % settings.MEDIA_URL),
                        ])
        html = super(ColorPickerWidget, self).render(name, value, attrs)
        return mark_safe(u''.join([head, html])) + mark_safe(u'''
           <div class="colorSelector" style="background-color:%(value)s;"></div>
           <script type="text/javascript">
            jQuery(function($) {
                $(document).ready(function () {
                    $.getScript("%(media)scmsutils/js/widgets/colorpicker.js", function() {
                    $('.%(fieldname)s div.colorSelector').ColorPicker({
                        color: '%(value)s',
                        onShow: function (colpkr) {
                            $(colpkr).fadeIn(500);
                            return false;
                        },
                        onHide: function (colpkr) {
                            $(colpkr).fadeOut(500);
                            return false;
                        },
                        onSubmit: function(hsb, hex, rgb, el) {
                            $('#id_%(fieldname)s').val('#' + hex);
                            $('.%(fieldname)s .colorSelector').css('backgroundColor', '#' + hex);
                            $(el).ColorPickerHide();
                        },
                        onChange: function (hsb, hex, rgb) {
                            $('#id_%(fieldname)s').val('#' + hex);
                            $('.%(fieldname)s .colorSelector').css('backgroundColor', '#' + hex);
                        }
                    });
                    $('#id_%(fieldname)s').css({float:'left',marginRight:'0.5em'});
                    $('.%(fieldname)s div.colorSelector').show();
                    $('#id_%(fieldname)s').change(function(){
                        var new_color = $(this).val();
                        $('.%(fieldname)s .colorSelector').css('backgroundColor', new_color);
                    });
                });
                });
            });
        </script>
        ''' % ({'media': settings.MEDIA_URL, 'fieldname':name, 'value':value}))


class JSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if not isinstance(value, basestring):
            value = json.dumps(value, indent=2)
        return super(JSONWidget, self).render(name, value, attrs)
 
