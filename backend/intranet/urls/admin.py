from django.conf.urls import *

from intranet.views.admin import *

urlpatterns = patterns('',
    url(r'^project_summary/(?P<project_id>\d+)/$', ProjectSummary.as_view(), name="project-summary"),
    url(r'^holidays_summary/$', HolidaysSummary.as_view(), name="holidays-summary"),
)
