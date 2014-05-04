from rest_framework.routers import DefaultRouter, SimpleRouter
from intranet.api import viewsets

router = DefaultRouter()
router.register("holidays-requests", viewsets.HolidaysRequestsViewSet, base_name="holidays-requests")
router.register("holidays-years", viewsets.HolidaysYearsViewSet, base_name="holidays-years")
router.register("holidays", viewsets.HolidaysViewSet, base_name="holidays")
router.register("parts", viewsets.PartViewSet, base_name="parts")
router.register("projects", viewsets.ProjectViewSet, base_name="projects")
router.register("talks", viewsets.TalkViewSet, base_name="talks")
router.register("quotes", viewsets.QuotesViewSet, base_name="quotes")

auth_router = SimpleRouter()
auth_router.register("auth", viewsets.AuthViewSet, base_name="auth")
