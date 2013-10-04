# -*-  coding: utf-8 -*-
import os
import tempfile
import re
from StringIO import StringIO
import time
import popen2

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models import signals
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.serializers.json import DjangoJSONEncoder
from django.template import defaultfilters
from django.utils import simplejson as json
from django.utils.functional import curry
from django.utils.encoding import smart_unicode

from cmsutils import forms as cmsutilsforms
from cmsutils.compat import SubfieldBase
from cmsutils.forms.fields import ESCCCField as ESCCCFormField
from cmsutils.forms.fields import ESPhoneNumberField \
                           as ESPhoneNumberFormField
from cmsutils.forms.fields import MultipleESPhoneNumberField \
                           as MultipleESPhoneNumberFormField
from cmsutils.forms.fields import LatitudeLongitudeField
from cmsutils.forms.widgets import GoogleMapsWidget, ColorPickerWidget
from cmsutils.map_utils import MapPosition
from cmsutils.utils import encrypt, decrypt, is_encrypted
from cmsutils.exceptions import VideoException


def get_ordered_parents(model):
    """
    Returns a list of all the ancestor of this model as a list.
    """
    result = []
    for parent in model._meta.parents:
        result.append(parent)
        result.extend(get_ordered_parents(parent))
    return result


class AutoSlugField(models.SlugField):

    def __init__(self, autofromfield, *args, **kwargs):
        self.force_on_edit = kwargs.pop('force_on_edit', False)
        self.unique_on_parent_model = kwargs.pop('unique_on_parent_model', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)
        self.autofromfield = autofromfield
        self.editable = kwargs.get('editable', False)

    def sluggify(self, name, objects):
        slug = defaultfilters.slugify(name)
        slug_num = slug
        n = 2
        filter_param = '%s__exact' % self.name
        filters = {filter_param: slug_num}
        while objects.filter(**filters):
            slug_num = slug + u'-%s' % n
            filters[filter_param] = slug_num
            n += 1
        return slug_num

    def _get_manager(self, instance):
        instance_model = instance.__class__
        if not self.unique_on_parent_model:
            return instance_model._default_manager
        models_to_iterate = [instance_model] + get_ordered_parents(instance_model)
        for model in models_to_iterate:
            if self in model._meta.local_fields:
                return model._default_manager

    def pre_save(self, instance, add):
        value = getattr(instance, self.autofromfield)

        objects_manager = self._get_manager(instance)

        if not instance.id:
            slug = self.sluggify(value, objects_manager.all())
        elif add or self.force_on_edit:
            slug = self.sluggify(value, objects_manager.exclude(id=instance.id))
        else:
            slug = getattr(instance, self.name)
        setattr(instance, self.name, slug)
        return slug

    def get_internal_type(self):
        return 'SlugField'


class DynamicMixin(object):
    """Allows model instance to specify upload_to dynamically.

    Model class should have a method like:

        def get_upload_to(self, attname):
            return 'path/to/%d' % self.id

    Based on:
    http://scottbarnham.com/blog/2007/07/31/uploading-images-to-a-dynamic-
    path-with-django/
    """

    def save_form_data(self, instance, data):
        self.data = data
        return

    def _post_save(field, instance, created=False, raw=False, **kwargs):
        if not getattr(field, 'real_save', None):
            if hasattr(instance, 'get_upload_to'):
                field.upload_to = instance.get_upload_to(field.attname)
                if getattr(field, 'data', None):
                    if field.data and isinstance(field.data, UploadedFile):
                        field.real_save=1
                        getattr(instance, "%s" % field.name).save(field.data.name, field.data, save=True)
                        del(field.data)
                        field.real_save=0

    def get_internal_type(self):
        return 'FileField'


class DynamicFileField(DynamicMixin, models.FileField):

    def contribute_to_class(self, cls, name):
        """Hook up events so we can access the instance."""
        super(DynamicFileField, self).contribute_to_class(cls, name)
        signals.post_save.connect(self._post_save, sender=cls)


class DynamicImageField(DynamicMixin, models.ImageField):

    def contribute_to_class(self, cls, name):
        """Hook up events so we can access the instance."""
        super(DynamicImageField, self).contribute_to_class(cls, name)
        signals.post_save.connect(self._post_save, sender=cls)


class AutoResizeImageFieldFile(models.fields.files.ImageFieldFile):

    def save(self, name, content, save=True):
        # Resize image if needed
        self.auto_resize(content, max_width=self.field.max_width, max_height=self.field.max_height)
        super(AutoResizeImageFieldFile, self).save(name, content, save)

    def auto_resize(self, content, width=None, height=None, max_width=None, max_height=None):
        """
        Resize an image to fit an area.

        At least one of max_width or max_height must be provided.
        """
        # Return if no file given or no maximum size passed
        try:
            from PIL import Image
        except ImportError:
            import Image
        if not max_width and not max_height:
            raise ValueError('At least one of max_height or max_width must be provided.')
        else:
            img = Image.open(content)
            width, height = img.size
            width = int(max_width or width)
            height = int(max_height or height)
        img.thumbnail((width, height), Image.ANTIALIAS) # resize maintaining aspect ratio
        resized_image = StringIO()
        img.save(resized_image, format=img.format)
        content._file = resized_image


class ResizingImageField(models.ImageField):
    """ImageField that automatically resizes uploaded images to a maximum width
    or height. """
    attr_class = AutoResizeImageFieldFile

    def __init__(self, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        super(ResizingImageField, self).__init__(**kwargs)


class JSONField(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""
        if value == "":
            return None

        value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONField, self).get_db_prep_save(value)

    def value_to_string(self, obj):
        """Serialize object into a JSON string """
        value = getattr(obj, self.name)
        return json.dumps(value)


class VideoFile(File):
    """
    A mixin for use alongside django.core.files.base.File, which provides
    additional features for dealing with videos.
    """

    def _get_thumbnail(self):
        thumbnail_name = "%s.jpg" % self.name
        os.chdir(settings.MEDIA_ROOT)
        thumbnail_file = open(thumbnail_name, 'rw')
        return ImageFile(thumbnail_file)
    thumbnail = property(_get_thumbnail)


class AutoEncodeFieldFile(VideoFile, models.fields.files.FieldFile):

    def save(self, name, content, save=True):
        try:
            dot_index = name.rindex('.')
        except ValueError: # filename has no dot
            pass
        else:
            name = name[:dot_index]
        # Encode video
        duration = self.encode_video(content, name, max_width=self.field.max_width, max_height=self.field.max_height, codec=self.field.codec)
        if self.field.duration_field:
            setattr(self.instance, self.field.duration_field, duration)
        super(AutoEncodeFieldFile, self).save("%s.%s" % (name, self.field.codec), content, save)

    def encode_video(self, content, name, max_width=None, max_height=None, codec=None):
        """
        Resize and encode a video. Requires ffmpeg and yamdi.
        """
        if codec is None:
            codec = 'flv'
        tempfd, tempfilename = tempfile.mkstemp()
        os.close(tempfd)
        ffmpeg = "ffmpeg -y -i - -acodec libmp3lame -ar 22050 -ab 96k -f %s -s %dx%d %s -b 900000" % (codec, (max_width or 320), (max_height or 240), tempfilename)
        pop = popen2.Popen3(ffmpeg, capturestderr=False)
        chunks = content.chunks()
        time.sleep(1)
        while pop.poll() == -1:
            try:
                chunk = chunks.next()
                pop.tochild.write(chunk)
            except (StopIteration, IOError):
                pop.tochild.close()
                pop.fromchild.close()
        ffmpeg_exit_status = pop.wait()
        if ffmpeg_exit_status != 0:
            raise VideoException(ffmpeg_exit_status)
        if codec == 'flv':
            # inject FLV metadata
            tempfd2, tempfilename2 = tempfile.mkstemp()
            os.close(tempfd2)
            yamdi = "yamdi -i %s -o %s" % (tempfilename, tempfilename2)
            os.popen(yamdi)
            os.rename(tempfilename2, tempfilename)
        vf = open(tempfilename)
        content._file.seek(0)
        content._file.write(vf.read())
        content._file.truncate()
        vf.close()
        fin, fout, ferr=os.popen3("ffmpeg -i %s" % tempfilename)
        video_info = ferr.read()
        fin.close()
        fout.close()
        ferr.close()
        match = re.search("Duration: [0-9][0-9]:[0-9][0-9]:(?P<seconds>[0-9][0-9])\.[0-9][0-9]?", video_info)
        if match:
            duration_seconds = int(match.groupdict()['seconds'])
        else:
            duration_seconds = 0
        video_filename = self.field.generate_filename(self.instance, "%s.%s" % (name, codec))
        video_path = os.path.join(settings.MEDIA_ROOT, self.field.generate_filename(self.instance, self.storage.get_available_name(video_filename)))
        ffmpeg_thumbnail = "ffmpeg -y -itsoffset -%d -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s %dx%d %s.jpg" % (duration_seconds/2, tempfilename, (max_width or 320), (max_height or 240), video_path)
        os.popen(ffmpeg_thumbnail)
        os.remove(tempfilename)
        return duration_seconds


class VideoField(models.FileField):
    """FileField that automatically resizes and encodes uploaded videos to a maximum height
    and with and a specified codec"""
    attr_class = AutoEncodeFieldFile

    def __init__(self, *args, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        self.codec = kwargs.pop('codec', None)
        self.duration_field = kwargs.pop('duration_field', None)
        super(VideoField, self).__init__(*args, **kwargs)


class ESPhoneNumberField(models.CharField):
    """Custom model field to store Spanish phone numbers (9-digit integers that
    start by 6, 8 or 9).

    If multiple=True then it allows for storing multiple phones, separated by
    hyphen (-), slash (/), comma (,) and/or whitespace. For this purpose
    cmsutils.forms.fields.MultipleESPhoneNumberField is used as form field.
    Otherwise django.contrib.localflavor.es.forms.ESPhoneNumberField is used.

    """

    def __init__(self, *args, **kwargs):
        self.multiple = kwargs.pop('multiple', False)
        super(ESPhoneNumberField, self).__init__(*args, **kwargs)
        if not self.multiple:
            self.max_length=9

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        if self.multiple:
            form_class = MultipleESPhoneNumberFormField
        else:
            form_class = ESPhoneNumberFormField
        defaults = {'form_class': form_class}
        defaults.update(kwargs)
        return super(ESPhoneNumberField, self).formfield(**defaults)


class SpanishDateField(models.DateField):

    def formfield(self, **kwargs):
        kwargs.update({'form_class': cmsutilsforms.fields.SpanishDateField})
        return super(SpanishDateField, self).formfield(**kwargs)

    def get_internal_type(self):
        return 'DateField'


class SpanishDateTimeField(models.DateTimeField):

    def formfield(self, **kwargs):
        kwargs.update({'form_class': cmsutilsforms.fields.SpanishDateTimeField})
        return super(SpanishDateTimeField, self).formfield(**kwargs)

    def get_internal_type(self):
        return 'DateTimeField'


class ESCCCField(models.CharField):
    """Custom model field to store Spanish bank account numbers
    (CCC short of "Código de Cuenta Cliente").

    When creating a forms form it uses the field
    cmsutils.forms.fields.ESCCCField

    """

    def __init__(self, *args, **kwargs):
        super(ESCCCField, self).__init__(*args, **kwargs)
        self.max_length=23

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        defaults = {'form_class': ESCCCFormField}
        defaults.update(kwargs)
        return super(ESCCCField, self).formfield(**defaults)


class GoogleMapsPositionField(models.Field):
    """Custom model field to store a position's latitude and longitude, using
    by default LatitudeLongitudeField forms field and GoogleMapsWidget to
    render a Google Maps map to choose the location easily.

    Sample usage:

    location = GoogleMapsPositionField(_(u'location'), blank=True, null=True,
        initial=MapPosition(37.303006,-6.302719,14), size=(500,309))

    Note to parameters:
        * initial is the default center of the map when there is no value.
        * default is the default position for a new point in the map.
        * size should be a 2-valued tuple with the map desired width and height.

    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 24
        self.initial = kwargs.pop('initial', None)
        self.default = kwargs.pop('default', None)
        self.width, self.height = kwargs.pop('size', (400, 247))

        super(GoogleMapsPositionField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, MapPosition):
            return value
        else:
            coords = value.split(",")
            if len(coords)<2:
                coords = ("0", "0")
            coords = [float(c.strip()) for c in coords]
            if len(coords)==2:
                lat, lng = coords
                zoom = self.initial and self.initial.zoom or None
                return MapPosition(lat, lng, zoom)
            if len(coords)==3:
                lat, lng, zoom = coords
                return MapPosition(lat, lng, zoom)

    def db_type(self):
        return 'char(%s)' % self.max_length

    def get_internal_type(self):
        return 'CharField'

    def get_db_prep_save(self, value):
        if value:
            return u"%.6f,%.6f" % (value.latitude, value.longitude)
        else:
            if self.default and self.default is not models.fields.NOT_PROVIDED:
                return u"%.6f,%.6f" % (self.default.latitude, self.default.longitude)
            else:
                return None

    def formfield(self, **kwargs):
        defaults = {'form_class': LatitudeLongitudeField}
        defaults.update(kwargs)
        defaults['widget'] = GoogleMapsWidget(initial=self.initial,
                                              attrs={'width': self.width, 'height': self.height})

        return super(GoogleMapsPositionField, self).formfield(**defaults)


class EncryptedField(models.CharField):

    def __init__(self, verbose_name=None, cipher_key=None, **kwargs):
        self.input_type = "password"
        self.key = smart_unicode(kwargs.pop('cipher_key', settings.SECRET_KEY))
        models.CharField.__init__(self, verbose_name=verbose_name, max_length=200, **kwargs)

    def _encrypt(self, value):
        if value is not None:
            return encrypt(smart_unicode(value), self.key)
        else:
            return None

    def _decrypt(self, value):
        if value is not None:
            return decrypt(smart_unicode(value), self.key)
        else:
            return None

    def _decrypt_field(self, cls, field):
        return field._decrypt(getattr(cls, field.name))

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        cls._meta.add_field(self)
        setattr(cls, 'get_decrypted_%s' % self.name, curry(self._decrypt_field, field=self))

    def get_internal_type(self):
        return "TextField"

    def get_db_prep_save(self, value):
        if not is_encrypted(value):
            # value is yet encrypted (for example if it came from fixtures)
            value = self._encrypt(value)
        return super(EncryptedField, self).get_db_prep_save(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        defaults['widget'] = forms.PasswordInput()

        return super(EncryptedField, self).formfield(**defaults)


class ColorField(models.CharField):

    def __init__(self, **kwargs):
        super(ColorField, self).__init__(max_length=16, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        defaults['widget'] = ColorPickerWidget()

        return super(ColorField, self).formfield(**defaults)
