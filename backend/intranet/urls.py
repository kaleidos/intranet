
from django.conf.urls import *

from django.conf import settings

from intranet.views.admin import *
from intranet.api.routers import router, auth_router

urlpatterns = patterns('',
    url(r'^%s/project_summary/(?P<project_id>\d+)/$' % (settings.BASE_ADMIN,), ProjectSummary.as_view(), name="project-summary"),
    url(r'^%s/holidays_summary/$' % (settings.BASE_ADMIN,), HolidaysSummary.as_view(), name="holidays-summary"),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include(auth_router.urls)),
)
