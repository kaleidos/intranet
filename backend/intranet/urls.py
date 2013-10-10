
from django.conf.urls import *

from intranet.views.admin import *
from intranet.api.routers import router, auth_router

urlpatterns = patterns('',
    url(r'^project_summary/(?P<project_id>\d+)/$', ProjectSummary.as_view(), name="project-summary"),
    url(r'^holidays_summary/$', HolidaysSummary.as_view(), name="holidays-summary"),
    url(r'^', include(router.urls)),
    url(r'^', include(auth_router.urls)),
)
