# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.contrib import admin

import django.contrib.auth.views
from django.conf import settings
from intranet.feeds import HolidaysRequestFeed


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/v1/', include('intranet.urls')),

    url(r'^%s/extra/'%(settings.BASE_ADMIN), include('intranet.urls.admin', namespace='admin-extra')),
    url(r'^%s/'%(settings.BASE_ADMIN), include(admin.site.urls)),
    url(r'^%s/autoreports/'%(settings.BASE_ADMIN), include('autoreports.urls')),

    url(r'^passwd/password_reset/$', 'django.contrib.auth.views.password_reset'),
    url(r'^passwd/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^passwd/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^passwd/reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^feed/holidays/$', HolidaysRequestFeed()),
)
