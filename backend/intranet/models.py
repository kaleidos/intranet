#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext as _
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.core import urlresolvers
from django.core import validators
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver

from picklefield.fields import PickledObjectField
from datetime import datetime, timedelta
from datetime import date

from djmail import template_mail

from .emails import send_holidays_approved_email


STATE_CREATED = 0
STATE_SENT = 10
STATE_ACCEPTED = 20
STATE_REJECTED = 30

PART_STATE_CHOICES = (
    (STATE_CREATED, _(u'Pending')),
    (STATE_SENT, _(u'Sent')),
    (STATE_ACCEPTED, _(u'Accepted')),
    (STATE_REJECTED, _(u'Rejected')),
)

RAW_COST = 0
CHARGEABILITY_COST = 10
PROFIT_COST = 20

COST_CHOICES = (
    (RAW_COST, _(u'Raw')),
    (CHARGEABILITY_COST, _(u'Chargeability')),
    (PROFIT_COST, _(u'Profit')),
)

PERCEPTION_STATE_INVOICE_PENDING = -10
PERCEPTION_STATE_PAYMENT_PENDING = 0
PERCEPTION_STATE_PAYMENT_RECEIVED = 10
PERCEPTION_STATE_CANCELLED = 20

PERCEPTION_STATE_CHOICES = (
    (PERCEPTION_STATE_INVOICE_PENDING, _(u'Invoice pending')),
    (PERCEPTION_STATE_PAYMENT_PENDING, _(u'Payment pending')),
    (PERCEPTION_STATE_PAYMENT_RECEIVED, _(u'Payment received')),
    (PERCEPTION_STATE_CANCELLED, _(u'Payment cancelled')),
)


#######################################################################
# Slug stuff
#######################################################################


def slugify_uniquely(value, model, slugfield="slug"):
    """Returns a slug on a name which is unique within a model's table
       self.slug = SlugifyUniquely(self.name, self.__class__)
    """
    suffix = 0
    potential = base = slugify(value)
    if len(potential) == 0:
        potential = 'null'
    while True:
        if suffix:
                potential = "-".join([base, str(suffix)])
        if not model.objects.filter(**{slugfield: potential}).count():
                return potential
        # we hit a conflicting slug, so bump the suffix & try again
        suffix += 1


#######################################################################
# Models
#######################################################################

class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """
    is_company_team = models.BooleanField(default=True, verbose_name=_(u"is a company member"))
    raw_cost = models.FloatField(default=10)
    chargeability_cost = models.FloatField(default=11)
    profit_cost = models.FloatField(default=12)

    reset_password_token = models.CharField(max_length=40, null=False, blank=True,
                                            verbose_name=_(u"reset password token"),
                                            default=u"")

    @property
    def full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between if both exist,
        or one of them or the username instead.
        """
        if self.first_name and self.last_name:
            return u"{} {}".format(self.first_name, self.last_name)
        elif self.first_name:
            return first_name
        elif self.last_name:
            return self.last_name
        return self.username


class Assignation(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('Project')
    cost = models.IntegerField(choices=COST_CHOICES, default=RAW_COST)

    class Meta:
        unique_together = ("employee", "project")

    def __unicode__(self):
        return unicode(self.employee)


class Project(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    internal_id = models.CharField(max_length=255, unique=True)
    internal_id.compact_filter = True
    name = models.CharField(max_length=600)
    description = models.TextField()
    active = models.BooleanField(default=True)
    client = models.ForeignKey('Client', related_name='project')
    employees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects',
                                       null=True, default=None,
                                       through="Assignation")
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subscribed_projects',
                                         null=True, blank=True, default=None)
    total_income = models.FloatField(default=0)
    is_holidays = models.BooleanField(default=False)
    last_month_activity = models.BooleanField(default=True)

    #Calculate if a part had activity last month
    def update_last_month_activity(self):
        month = datetime.now().month
        year = datetime.now().year
        if month == 1:
            month = 12
            year = year - 1
        else:
            month = month - 1

        hours = sum([part.total_hours(self.id) for part in self.parts.filter(month__exact=month, year__exact=year)])
        self.last_month_activity = hours > 0
        self.save()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Project')
        verbose_name_plural = _(u'Projects')
        ordering = ['name']

    def save(self):
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        super(Project, self).save()


class Part(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    month = models.IntegerField(choices=MONTHS.items())
    year = models.IntegerField(choices=[(i, i) for i in range(datetime.today().year-5, datetime.today().year+5)])
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='parts')
    state = models.IntegerField(choices=PART_STATE_CHOICES)
    info = models.TextField(verbose_name=_(u'Information extra'), null=True, blank=True)
    data = PickledObjectField(default={})
    projects = models.ManyToManyField(Project, related_name='parts', null=True, blank=True)

    def __unicode__(self):
        return u'%s-%s-%s' % (unicode(self.year), unicode(self.month), unicode(self.employee))

    class Meta:
        verbose_name = _(u'Part')
        verbose_name_plural = _(u'Parts')
        ordering = ['-year', '-month']
        unique_together = ("month", "year", "employee")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_uniquely(
                u'%s-%s-%s' % (unicode(self.year), unicode(self.month), unicode(self.employee)),
                self.__class__
            )

        super(Part, self).save(*args, **kwargs)
        #Updating project attributes
        self.projects.clear()
        for project_id in self.data.keys():
            project = Project.objects.get(id=project_id)
            self.projects.add(project)

    def total_hours(self, project_id):
        project_hours = self.data.get(str(project_id), self.data.get(project_id, None))
        if not project_hours:
            return 0

        return sum(map(float, project_hours.values()))

    def total_days(self, project_id):
        return self.total_hours(project_id) / settings.WORKING_HOURS_PER_DAY

    def raw_cost(self, project_id):
        return self.total_hours(project_id) * self.employee.raw_cost

    def chargeability_cost(self, project_id):
        return self.total_hours(project_id) * self.employee.chargeability_cost

    def profit_cost(self, project_id):
        return self.total_hours(project_id) * self.employee.profit_cost

    def real_cost(self, project_id):
        assignation = Assignation.objects.get(project_id=project_id, employee=self.employee)
        if assignation.cost == RAW_COST:
            return self.raw_cost(project_id)
        elif assignation.cost == CHARGEABILITY_COST:
            return self.chargeability_cost(project_id)
        else:
            return self.profit_cost(project_id)


#holiday...days when people shouldn't work
class SpecialDay(models.Model):
    date = models.DateField()
    description = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (unicode(self.date))

    class Meta:
        ordering = ['date']

    def year(self):
        return self.date.year

    year.allow_tags = True
    year.admin_order_field = 'date__year'
    year.short_description = _(u'Year')

    def month(self):
        return self.date.month

    month.allow_tags = True
    month.admin_order_field = 'date__month'
    month.short_description = _(u'Month')

    def day(self):
        return self.date.day

    day.allow_tags = True
    day.admin_order_field = 'date__day'
    day.short_description = _(u'Day')


########################################################################
#Clients
########################################################################

class Sector(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % (unicode(self.name))

    class Meta:
        ordering = ['name']


class Client(models.Model):
    internal_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    sector = models.ForeignKey('Sector', related_name='clients')
    employees_number = models.IntegerField(default=0)
    contact_person = models.TextField(default=u'', blank=True)
    ubication = models.TextField(default=u'', blank=True)

    def __unicode__(self):
        return u'%s' % (unicode(self.name))

    class Meta:
        ordering = ['name']


########################################################################
#Invoices
########################################################################

class Invoice(models.Model):
    number = models.CharField(max_length=255, verbose_name=u'invoice number', unique=True)
    perception_state = models.IntegerField(choices=PERCEPTION_STATE_CHOICES, default=PERCEPTION_STATE_INVOICE_PENDING)

    quantity = models.FloatField(default=0)
    quantity_iva = models.FloatField(default=0, verbose_name=_(u'Quantity (IVA included)'), blank=True, null=True)
    iva = models.FloatField(default=settings.IVA)

    concept = models.TextField(default=u'', blank=True)
    payment_conditions = models.CharField(max_length=255, default=u'', blank=True, verbose_name=u'conditions')
    payment = models.BooleanField(default=False, verbose_name=u'credit note')

    client = models.ForeignKey('Client', related_name='invoices')
    project = models.ForeignKey('Project', related_name='invoices')

    estimated_through_date = models.DateField(blank=True, null=True,
                                              verbose_name=mark_safe(_(u'Estimated through date')))
    through_date = models.DateField(blank=True, null=True)

    estimated_perception_date = models.DateField(blank=True, null=True,
                                                 verbose_name=mark_safe(_(u'Estimated perception date')))
    perception_date = models.DateField(blank=True, null=True)

    invoice_file = models.FileField(upload_to='uploaded/invoices', blank=True, null=True)

    comments = models.TextField(default=u'', blank=True)

    def save(self):
        status_changed = False
        try:
            invoice_state_before_save = Invoice.objects.get(pk=self.pk).perception_state
            if invoice_state_before_save != self.perception_state:
                status_changed = True
        except Invoice.DoesNotExist:
            invoice_state_before_save = "none"
            status_changed = True

        super(Invoice, self).save()
        self.quantity_iva = self.quantity * (1 + self.iva)
        super(Invoice, self).save()

        if status_changed:
            mail_builder = template_mail.MagicMailBuilder()
            if self.project.subscribers.all().count() > 0:
                mail = mail_builder.invoice_state_change(
                    ",".join([u.email for u in self.project.subscribers.all()]),
                    {'invoice': self, 'old_state': invoice_state_before_save, 'base_url': settings.BASE_URL}
                )
                mail.send()

    def __unicode__(self):
        return u'%s' % (self.number)

    class Meta:
        ordering = ['estimated_through_date']

    def get_unicode_perception_state(self):
        return dict(PERCEPTION_STATE_CHOICES)[self.perception_state]

    #0: none
    #1: near date
    #2: over date
    def highlighted_status(self):
        if self.perception_state == PERCEPTION_STATE_PAYMENT_RECEIVED:
            return 0

        elif (not self.through_date
              and self.estimated_through_date
              and self.estimated_through_date < datetime.today().date()):
            return 2

        elif (not self.perception_date
              and self.estimated_perception_date
              and self.estimated_perception_date < datetime.today().date()):
            return 2

        elif (not self.through_date
              and self.estimated_through_date
              and self.estimated_through_date < (datetime.today().date() + timedelta(days=settings.NEXT_INVOICE_DAYS))):
            return 1

        elif (not self.perception_date
              and self.estimated_perception_date
              and self.estimated_perception_date < (datetime.today().date() + timedelta(days=settings.NEXT_INVOICE_DAYS))):
            return 1

        return 0

    highlighted_status.allow_tags = True
    highlighted_status.short_description = _(u' ')


########################################################################
#Holidays
########################################################################

HOLIDAYS_REQUEST_CHOICES = (
    (STATE_CREATED, _(u'Pending')),
    (STATE_ACCEPTED, _(u'Accepted')),
    (STATE_REJECTED, _(u'Rejected')),
)


class HolidaysYear(models.Model):
    year = models.IntegerField(choices=[(i, i) for i in range(datetime.today().year-5, datetime.today().year+5)])
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % (self.year)


class HolidaysRequest(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='holidays_requests')
    year = models.ForeignKey('HolidaysYear', related_name='holidays_requests')
    status = models.IntegerField(choices=HOLIDAYS_REQUEST_CHOICES, default=STATE_CREATED)
    beginning = models.DateField()
    ending = models.DateField()
    flexible_dates = models.BooleanField(default=False)
    comments = models.TextField(default=u'', blank=True)

    def get_working_days(self):
        days = []
        for day_counter in range(int((self.ending - self.beginning).days)+1):
            requested_day = self.beginning + timedelta(day_counter)
            is_special_day = SpecialDay.objects.filter(date=requested_day).count() > 0
            is_weekend = date.weekday(requested_day) in [5, 6]
            if not is_special_day and not is_weekend:
                days.append(requested_day)

        return days

    def count_working_days(self):
        return len(self.get_working_days())

    def __unicode__(self):
        return u'%s: from %s to %s' % (self.employee.get_full_name(), self.beginning, self.ending)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,)
        )

@receiver(pre_save, sender=HolidaysRequest)
def on_holidays_store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        instance.previous_status = HolidaysRequest.objects.get(pk=instance.pk).status

@receiver(post_save, sender=HolidaysRequest)
def on_holidays_request_notification(sender, instance, **kwargs):
    if not hasattr(instance, 'previous_status'):
        return
    if instance.status == instance.previous_status:
        return
    if instance.status in [STATE_ACCEPTED, STATE_REJECTED]:
        send_holidays_approved_email(instance, STATE_ACCEPTED, STATE_REJECTED)

########################################################################
# Talks
########################################################################

class Talk(models.Model):
    name = models.CharField(max_length=250)
    created_date = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    description = models.CharField(max_length=500)
    obsolete = models.BooleanField(default=False)
    wanters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='talks_wanted',
                                       null=True, blank=True, default=None)
    talkers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='talks_offers',
                                       null=True, blank=True, default=None)
    talkers_are_ready = models.BooleanField(default=False)
    duration = models.IntegerField(null=True, blank=True, default=None)
    datetime = models.DateTimeField(null=True, blank=True, default=None)
    place = models.CharField(max_length=150, null=True, blank=True, default=None)

    def __unicode__(self):
        return u"%s" % (self.name,)


########################################################################
# Quotes
########################################################################

class QuoteScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="quote_scores")
    quote = models.ForeignKey("Quote", related_name="scores")
    score = models.IntegerField(default=0, validators=[validators.MinValueValidator(0),
                                                       validators.MaxValueValidator(5)])

    class Meta:
        verbose_name = _(u"Quote score")
        verbose_name_plural = _(u"Quote scores")
        unique_together = ("user", "quote")


class Quote(models.Model):
    quote = models.TextField(null=False, blank=False, verbose_name=_(u"quote"))
    explanation = models.TextField(null=False, blank=True, verbose_name=_(u"explanation"))
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 related_name="quotes",
                                 verbose_name=_(u"employee"))
    external_author = models.CharField(max_length=256, null=False, blank=True,
                                       verbose_name=_(u"external author"))
    created_date = models.DateTimeField(null=False, blank=False, auto_now_add=True,
                                        verbose_name=_(u"created date"))
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                related_name="quotes_created",
                                verbose_name=_(u"author"))
    users_rates = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='quotes_rated',
                                         null=True, blank=True, default=None, through="QuoteScore")

    class Meta:
        verbose_name = _(u"Quote")
        verbose_name_plural = _(u"Quotes")
        ordering = ["-created_date"]

    def __unicode__(self):
        return self.quote
