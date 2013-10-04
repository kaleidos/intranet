#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.views.generic import View
from django.shortcuts import render_to_response, get_object_or_404
from intranet.models import *
from django.template import RequestContext
from intranet.utils import get_consumed_days_for_user


class HolidaysSummary(View):
    #TODO: security check
    def get(self, request):

        holidays = []

        for holidays_year in HolidaysYear.objects.filter(active=True):
            totals = {}
            for user in User.objects.filter(is_company_team=True):
                consumed_days = get_consumed_days_for_user(user, holidays_year)
                totals[user.get_full_name()] = consumed_days

            holidays.append((holidays_year.year, totals))

        context = {
            'holidays': holidays,
        }
        return render_to_response('admin/intranet/holidays_summary.html', RequestContext(request, context))


class ProjectSummary(View):
    #TODO: security check
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        parts = project.parts.filter(projects__id__in=[project.id])

        # Para calcular el colspan de la columna del año necesitamos saber por
        # cada mes cuantos proyectos imputan y sumar dos
        count_imputations_and_months = {}
        for part in parts:
            imputation = part.data.get(project.id, None)
            year = part.year
            month = part.month

            if year not in count_imputations_and_months:
                count_imputations_and_months[year] = {}

            if month not in count_imputations_and_months[year]:
                count_imputations_and_months[year][month] = []

            count_imputations_and_months[year][month].append(imputation or None)

        for year_key in count_imputations_and_months:
            for month_key in count_imputations_and_months[year_key]:
                count_imputations_and_months[year_key][month_key] = 2 + len(count_imputations_and_months[year_key][month_key])

            count_imputations_and_months[year_key] = 2 + sum(count_imputations_and_months[year_key].values())

        invoices = project.invoices.all()
        unperceived_invoices = invoices.exclude(perception_state=PERCEPTION_STATE_PAYMENT_RECEIVED).order_by('-estimated_perception_date')
        total_perceived = sum(invoices.filter(perception_state=PERCEPTION_STATE_PAYMENT_RECEIVED).values_list('quantity', flat=True))

        context = {
            'parts': parts,
            'count_imputations_and_months': count_imputations_and_months,
            'perception_states': PERCEPTION_STATE_CHOICES,
            'total_perceived': total_perceived,
            'unperceived_invoices': unperceived_invoices,
            'work_in_progress_donde': invoices and not unperceived_invoices,
            'invoices': invoices,
            'project': project,
        }
        return render_to_response('project_summary.html', context)

    def dispatch(self, *args, **kwargs):
        return super(ProjectSummary, self).dispatch(*args, **kwargs)
