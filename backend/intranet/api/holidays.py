# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response

from intranet import models
from intranet import serializers
from intranet.permissions import HolidaysPermission
from intranet.api.filters import IsEmployeeFilterBackend, YearFilterBackend


class HolidaysYearsViewSet(ModelViewSet):
    queryset = models.HolidaysYear.objects.filter(active=True)
    serializer_class = serializers.HolidaysYearSerializer
    permission_classes = (permissions.IsAuthenticated,)


class HolidaysRequestsViewSet(ModelViewSet):
    model = models.HolidaysRequest
    serializer_class = serializers.HolidaysRequestSerializer
    permission_classes = (HolidaysPermission,)
    filter_backends = (IsEmployeeFilterBackend, YearFilterBackend)

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
