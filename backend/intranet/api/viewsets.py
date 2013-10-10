# -*- coding: utf-8 -*-

from django.contrib import auth
from django.conf import settings

from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework import permissions

from intranet import models
from intranet import services
from intranet.api import api_permissions
from intranet.api import serializers
from intranet.api import filters


class AuthViewSet(ViewSet):
    @list_route(methods=["post"])
    def login(self, request, format=None):
        username = request.DATA.get("username", None)
        password = request.DATA.get("password", None)
        user_service = services.UserService()

        user = user_service.authenticate(username=username, password=password)
        auth.login(request, user)

        serializer = serializers.LoginSerializer(serializers.UserLogged(**{
            "token": request.session.session_key,
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "is_staff":  request.user.is_staff,
            "is_superuser":  request.user.is_superuser,
            "date_joined": request.user.date_joined,
            "last_login": request.user.last_login,
        }))
        return Response(serializer.data)

    @list_route(methods=["post"])
    def logout(self, request, format=None):
        auth.logout(request)
        return Response({"detail": u"Logout successfully."})

    @list_route(methods=["post"])
    def reset_password(self, request, format=None):
        username = request.DATA.get("username", None)
        domain = request.DATA.get("client_domain", settings.CLIENT_DOMAIN)
        use_https = request.DATA.get("use_https", settings.CLIENT_USE_HTTPS)

        user_service = services.UserService()
        user_service.reset_password(username=username, domain=domain, use_https=use_https)

        return Response({"detail": u"The reset password email has been sent successfully."})

    @list_route(methods=["post"])
    def change_password(self, request, format=None):
        user = request.user
        token = request.DATA.get("token", None)
        password1 = request.DATA.get("password1", None)
        password2 = request.DATA.get("password2", None)

        if not password1 or password1 != password2:
            return Response({"detail": u"Password empty or not matchs"},
                            status.HTTP_400_BAD_REQUEST)

        user_service = services.UserService()
        if token:
            user_service.change_password(token, password1)
        elif user and not user.is_anonymous():
            user_service.change_password_to_user(user, password1)
        else:
            return Response({"detail": u"You don\'t have permission to do that."},
                            status.HTTP_401_UNAUTHORIZED)
        return Response({"detail": "The password has beeen changed successfully."})


class HolidaysYearsViewSet(ModelViewSet):
    queryset = models.HolidaysYear.objects.filter(active=True)
    serializer_class = serializers.HolidaysYearSerializer
    permission_classes = (permissions.IsAuthenticated,)


class HolidaysRequestsViewSet(ModelViewSet):
    model = models.HolidaysRequest
    serializer_class = serializers.HolidaysRequestSerializer
    permission_classes = (api_permissions.HolidaysPermission,)
    filter_backends = (filters.IsEmployeeFilterBackend, filters.YearFilterBackend)

    def pre_save(self, obj):
        super(HolidaysRequestsViewSet, self).pre_save(obj)
        obj.employee = self.request.user
        obj.status = 0


class HolidaysViewSet(ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, format=None):
        days = sum([hr.get_working_days() for hr in request.user.holidays_requests.all()], [])

        year = self.request.QUERY_PARAMS.get('year', None)
        days = filter(lambda d: str(d.year) == year, days) if year else days

        month = self.request.QUERY_PARAMS.get('month', None)
        days = filter(lambda d: str(d.month) == month, days) if month else days

        return Response([serializers.DaySerializer(d).data for d in days])


class PartViewSet(ModelViewSet):
    queryset = models.Part.objects.all()
    serializer_class = serializers.PartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"
    filter_backends = (filters.IsEmployeeFilterBackend, filters.PartTypeFilterBackend)

    def pre_save(self, obj):
        super(PartViewSet, self).pre_save(obj)
        obj.employee = self.request.user

    @detail_route(methods=["post"])
    def send(self, request, *args, **kwargs):
        part = self.get_object()
        part.state = models.STATE_SENT
        part.save(update_fields=["state"])
        return Response(status=status.HTTP_200_OK)


class ProjectViewSet(ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.InEmployeesFilterBackend, filters.ProjectTypeFilterBackend)


class TalkViewSet(ModelViewSet):
    queryset = models.Talk.objects.filter(obsolete=False)
    serializer_class = serializers.TalkSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingTalksFilterBackend,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"

    @detail_route(methods=["post"])
    def i_want(self, request, pk=None, format=None):
        talk = self.get_object()
        talk.wanters.add(request.user)
        return Response({"detail": u"Talk marked as wanted."})

    @detail_route(methods=["post"])
    def i_talk(self, request, pk=None, format=None):
        talk = self.get_object()
        talk.talkers.add(request.user)
        return Response({"detail": u"Talk marked me as talker."})
