#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.db.models import Sum, DateTimeField
from django.template import Context, loader

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin import DateFieldListFilter, FieldListFilter

import locale
from datetime import datetime, timedelta, date
from calendar import monthrange, Calendar

from autoreports.admin import ReportAdmin
from autoreports.main import AutoReportChangeList

from dateutil.relativedelta import relativedelta

from intranet.models import (Assignation, Invoice, Project,
                             Part, SpecialDay, Client, Sector, HolidaysRequest,
                             HolidaysYear, User)
from intranet.forms import (UserCreationForm, UserChangeForm)


class AssignationInline(admin.StackedInline):
    model = Assignation
    extra = 0


class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0


def assign_everybody(modeladmin, request, queryset):
    for project in queryset:

        for user in User.objects.filter(is_company_team=True):
            if not Assignation.objects.filter(
                    employee=user,
                    project=project):

                Assignation.objects.create(
                    employee=user,
                    project=project
                )

            month = datetime.now().month
            year = datetime.now().year
            for part in user.parts.filter(year=year, month=month):
                part.save()

assign_everybody.short_description = "Assign to everybody"


class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('summary', 'slug',)
    exclude = ('slug',)
    list_display = ('__unicode__',  'internal_id', 'client', 'last_month_activity', 'active',)
    list_filter = ('active', 'client', 'last_month_activity',)

    inlines = [
        AssignationInline,
        InvoiceInline,
    ]

    actions = [assign_everybody]

    def summary(self, obj):
        #Creation
        if not obj.id:
            return ''

        html_output = '''
<script>
    function set_iframe_height(){
      var cwin=document.getElementById("project-summary");
      if (document.getElementById){
          if (cwin) {
              if (cwin.contentDocument && cwin.contentDocument.body.offsetHeight)
                  cwin.height = cwin.contentDocument.body.offsetHeight;
              else if(cwin.Document && cwin.Document.body.scrollHeight)
                  cwin.height = cwin.Document.body.scrollHeight;
          }
      }
    }
</script>
<iframe onload="javascript:set_iframe_height()" id="project-summary" style="border:none; width:100%%;" src="%s"></iframe>
        ''' % (reverse('admin-extra:project-summary', args=[obj.id]))
        return html_output.replace('\n', '')

    summary.allow_tags = True
    summary.short_description = _(u'Financial info')

admin.site.register(Project, ProjectAdmin)


class PartAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'year', 'month', 'employee', 'state')
    list_filter = ('year', 'month', 'employee__username', 'state')
    readonly_fields = ('calendar_frame',)

    exclude = ('slug',)

    def calendar_frame(self, obj):
        num_days = monthrange(obj.year, obj.month)[1]
        days_imputations = [0 for i in range(num_days)]
        projects_imputations = {}
        for project_id, imputation in obj.data.items():
            hours = map(float, imputation.values())
            projects_imputations[project_id] = {
                'days': hours,
                'project': project_id,
                'total': sum(hours),
            }
            days_imputations = zip(days_imputations, hours)
            days_imputations = map(lambda x: sum(x), days_imputations)

        weekend_days = map(lambda x: x[0], filter(lambda x: x[1] >= 5, Calendar().itermonthdays2(obj.year, obj.month)))
        special_days = [d.day for d in SpecialDay.objects.filter(date__year=obj.year, date__month=obj.month).values_list('date', flat=True)]
        special_days += weekend_days

        total = sum([i['total'] for i in projects_imputations.values()])
        context = Context({
            'num_days': num_days,
            'days_imputations': days_imputations,
            'projects_imputations': projects_imputations,
            'total': total,
            'special_days': special_days,
        })

        t = loader.get_template('calendar_part.html')
        return t.render(context).replace('\n', '')

    calendar_frame.allow_tags = True
    calendar_frame.short_description = _(u'Calendar')

admin.site.register(Part, PartAdmin)


class IntranetProjectInline(admin.StackedInline):
    model = Project.employees.through
    extra = 1
    verbose_name = _(u'projects')
    verbose_name_plural = _(u'projects')


class IntranetUserAdmin(UserAdmin):
    change_inlines = [
        IntranetProjectInline,
    ]
    add_inlines = []
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Company info'), {'fields': ('is_company_team', 'raw_cost', 'chargeability_cost', 'profit_cost')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'reset_password_token')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Company info'), {'fields': ('is_company_team', 'raw_cost', 'chargeability_cost', 'profit_cost')}),
    )
    form = UserChangeForm
    add_form = UserCreationForm

    def add_view(self, request):
        self.inlines=self.add_inlines
        return super(IntranetUserAdmin, self).add_view(request)

    def change_view(self, request, obj_id):
        self.inlines=self.change_inlines
        return super(IntranetUserAdmin, self).change_view(request, obj_id)

admin.site.register(User, IntranetUserAdmin)
admin.site.unregister(Group)


class SpecialDayAdmin(ReportAdmin, admin.ModelAdmin):
    list_display = ('date', 'year', 'month', 'day')
    date_hierarchy = 'date'

admin.site.register(SpecialDay, SpecialDayAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'sector')
    list_filter = ('sector',)

admin.site.register(Client, ClientAdmin)


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ('number', 'perception_state', 'quantity', 'quantity_iva',
                  'iva', 'concept', 'payment_conditions', 'payment', 'client',
                  'project', 'estimated_through_date', 'through_date',
                  'estimated_perception_date', 'perception_date', 'invoice_file',
                  'comments',)

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['quantity_iva'].widget.attrs['readonly'] = True


class CustomDateFieldFilterSpec(DateFieldListFilter):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(CustomDateFieldFilterSpec, self).__init__(f, request, params, model,
                                                        model_admin,
                                                        field_path=field_path)

        today = date.today()
        one_week_ago = today - timedelta(days=7)
        one_month_ago = today - relativedelta(months=1)
        today_str = (isinstance(self.field, DateTimeField)
                     and today.strftime('%Y-%m-%d 23:59:59')
                     or today.strftime('%Y-%m-%d'))

        self.links = (
            (_('Any date'), {}),
            (_('Today'), {'%s__year' % self.field_path: str(today.year),
                          '%s__month' % self.field_path: str(today.month),
                          '%s__day' % self.field_path: str(today.day)}),
            (_('Past 7 days'), {'%s__gte' % self.field_path: one_week_ago.strftime('%Y-%m-%d'),
                                '%s__lte' % self.field_path: today_str}),
            (_('Last month'), {'%s__year' % self.field_path: str(one_month_ago.year),
                               '%s__month' % self.field_path: str(one_month_ago.month)}),
            (_('This month'), {'%s__year' % self.field_path: str(today.year),
                               '%s__month' % self.field_path: str(today.month)}),
            (_('This year'), {'%s__year' % self.field_path: str(today.year)})
        )


FieldListFilter.register(lambda f: f.name == 'estimated_through_date', DateFieldListFilter)
FieldListFilter.register(lambda f: f.name == 'through_date', DateFieldListFilter)
FieldListFilter.register(lambda f: f.name == 'estimated_perception_date', DateFieldListFilter)
FieldListFilter.register(lambda f: f.name == 'perception_date', DateFieldListFilter)


class InvoiceChangeList(ChangeList):

    columns_with_total = [
        {
            'column': 'quantity',
            'name': 'Quantity total',
            'lambda': lambda x: x,
        },
        {
            'column': 'quantity_iva',
            'name': 'Quantity total (IVA included)',
            'lambda': lambda x: x,
        }
    ]

    #TOTALS SUPPORT IN FILTERING
    def get_results(self, *args, **kwargs):
        super(InvoiceChangeList, self).get_results(*args, **kwargs)

        self.totals = {}
        if hasattr(self, 'columns_with_total'):
            for column_info in self.columns_with_total:
                #In autoreports listing this generates an error
                try:
                    q = self.result_list.aggregate(quantity_sum=Sum(column_info['column']))
                    total = q['quantity_sum']
                    self.totals[column_info['name']] = column_info['lambda'](total)
                except:
                    pass


class InvoiceAutoReportChangeList(AutoReportChangeList, InvoiceChangeList):
    pass


class InvoiceAdmin(ReportAdmin, admin.ModelAdmin):
    list_display = ('number', 'highlighted_status', 'client', 'project',
                    'concept', 'payment_conditions',
                    'quantity_iva_formatted', 'quantity_formatted',
                    'estimated_through_date', 'through_date',
                    'estimated_perception_date', 'perception_date',
                    'perception_state')
    list_filter = ('payment', 'perception_state', 'client',
                   'estimated_through_date', 'through_date',
                   'estimated_perception_date', 'perception_date', 'project',)
    ordering = ('estimated_through_date',)
    form = InvoiceForm

    ReportChangeList = InvoiceAutoReportChangeList

    def get_changelist(self, request):
        return InvoiceChangeList

    def quantity_formatted(self, obj):
        locale.setlocale(locale.LC_ALL, settings.LOCALE)
        return mark_safe('<div style="text-align:right">' +
                         locale.currency(obj.quantity, grouping=True) +
                         '</div>')

    quantity_formatted.admin_order_field = 'quantity'
    quantity_formatted.allow_tags = True
    quantity_formatted.short_description = _(u'Quantity')

    def quantity_iva_formatted(self, obj):
        locale.setlocale(locale.LC_ALL, settings.LOCALE)
        return mark_safe('<div style="text-align:right">' +
                         locale.currency(obj.quantity_iva, grouping=True) +
                         '</div>')

    quantity_iva_formatted.admin_order_field = 'quantity_iva'
    quantity_iva_formatted.allow_tags = True
    quantity_iva_formatted.short_description = _(u'Quantity (IVA included)')

    # A template for a very customized change view:
    change_list_template = 'admin/intranet/invoices_change_list.html'

admin.site.register(Invoice, InvoiceAdmin)

admin.site.register(Sector)


class HolidaysRequestAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'employee', 'status', 'beginning', 'ending')
    list_filter = ('status', 'employee')

admin.site.register(HolidaysRequest, HolidaysRequestAdmin)

admin.site.register(HolidaysYear)
