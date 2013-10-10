# -*- coding: utf-8 -*-

from django.conf.urls import *

from rest_framework.routers import DefaultRouter, SimpleRouter

from intranet.api import (
    auth,
    projects,
    parts,
    holidays,
    talks,
)

router = DefaultRouter()
router.register("holidays-requests", holidays.HolidaysRequestsViewSet, base_name="holidays-requests")
router.register("holidays-years", holidays.HolidaysYearsViewSet, base_name="holidays-years")
router.register("holidays", holidays.HolidaysViewSet, base_name="holidays")
router.register("parts", parts.PartViewSet, base_name="parts")
router.register("projects", projects.ProjectViewSet, base_name="projects")
router.register("talks", talks.TalkViewSet, base_name="talks")

auth_router = SimpleRouter()
auth_router.register("auth", auth.AuthViewSet, base_name="auth")

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^', include(auth_router.urls)),
)
