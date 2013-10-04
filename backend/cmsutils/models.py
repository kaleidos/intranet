from django.db import models
from django.utils.translation import ugettext_lazy as _


class ParameterManager(models.Manager):

    def get_value(self, name, default=None):
        value = None
        try:
            parameter = self.get(name=name)
            value = parameter.value
        except Parameter.DoesNotExist:
            value = default

        return value

    def set_value(self, name, value):
        parameter = None

        try:
            parameter = self.get(name=name)
            parameter.value = value
        except Parameter.DoesNotExist:
            parameter = self.create(name=name, value=value)

        if value is None:
            parameter.delete()
        else:
            parameter.save()
        return parameter


class Parameter(models.Model):
    """ A global parameter.

    # Create some parameters
    >>> param1 = Parameter.objects.create(name="portal_title",
    ...                                   value="Portal Test")
    >>> param2 = Parameter.objects.create(name="admin_email",
    ...                                   value="admin@fundacioniavante.com")

    # Let's see their unicode representation
    >>> unicode(param1)
    u'portal_title: Portal Test'

    >>> unicode(param2)
    u'admin_email: admin@fundacioniavante.com'
    """

    name = models.CharField(_("name"), max_length=50, unique=True, blank=False)
    value = models.CharField(_("value"), max_length=50, blank=False)

    objects = ParameterManager()

    class Meta:
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')

    def __unicode__(self):
        return u'%s: %s' % (self.name, self.value)


class OrderedModel(models.Model):
    """
    Base model for simple ordering

    Example use::

    class FooModel(OrderedModel):
        name = models.CharField(max_length=100)
        objects = OrderedManager()

    """
    position = models.IntegerField(verbose_name=_('position'),
                                   db_index=True, default=0, null=True)

    class Meta:
        verbose_name = _('ordered model')
        verbose_name_plural = _('ordered models')
        abstract = True
