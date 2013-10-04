# -*- coding: utf-8 -*-

from django.conf.urls import *

from intranet.api import (
    auth,
    projects,
    parts,
    holidays
)


urlpatterns = patterns('',
    url(r'^login/$', auth.Login.as_view(), name="login"),
    url(r'^logout/$', auth.Logout.as_view(), name="logout"),
    url(r'^reset-password/$', auth.ResetPassword.as_view(), name='reset-password'),
    url(r'^change-password/$', auth.ChangePassword.as_view(), name='change-password'),

    url(r'^projects/$', projects.ProjectList.as_view(), name="project-list"),

    url(r'^parts/$', parts.PartList.as_view(), name="part-list"),
    url(r'^parts/(?P<pk>\d+)/$', parts.PartDetail.as_view(), name="part-detail"),
    url(r'^parts/(?P<pk>\d+)/send/$', parts.PartSend.as_view(), name="part-send"),

    url(r'^holidays-years/$', holidays.HolidaysYearsList.as_view(), name="holidays-years-list"),
    url(r'^holidays-years/(?P<pk>\d+)/$', holidays.HolidaysYearDetail.as_view(), name="holidays-year-detail"),

    url(r'^holidays-requests/$', holidays.HolidaysRequestsList.as_view(), name="holidays-requests-list"),
    url(r'^holidays-requests/(?P<pk>\d+)/$', holidays.HolidaysRequestDetail.as_view(), name="holidays-requests-detail"),

    url(r'^holidays/$', holidays.HolidaysList.as_view(), name="holidays-list"),

)
