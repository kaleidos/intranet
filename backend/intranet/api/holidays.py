# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import (
    generics,
    permissions
)
from rest_framework.views import APIView
from rest_framework.response import Response

from intranet import models
from intranet import serializers
from intranet.permissions import HolidaysPermission


class HolidaysYearsList(generics.ListAPIView):
    model = models.HolidaysYear
    serializer_class = serializers.HolidaysYearSerializer
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"

    def get_queryset(self):
        queryset = super(HolidaysYearsList, self).get_queryset()
        queryset = queryset.filter(active=True)
        return queryset


class HolidaysYearDetail(generics.RetrieveAPIView):
    model = models.HolidaysYear
    serializer_class = serializers.HolidaysYearSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "pk"

    def get_queryset(self):
        queryset = self.request.user.holidays_requests.all()

        return queryset

class HolidaysRequestsList(generics.ListCreateAPIView):
    model = models.HolidaysRequest
    serializer_class = serializers.HolidaysRequestSerializer
    permission_classes = (HolidaysPermission,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"

    def get_queryset(self):
        queryset = self.request.user.holidays_requests.all()
        queryset = queryset.filter(year__active=True)
        year = self.request.GET.get('year', None)
        if year:
            queryset = queryset.filter(year__id=year)

        return queryset

    def pre_save(self, obj):
        super(HolidaysRequestsList, self).pre_save(obj)
        obj.employee = self.request.user
        obj.status = 0


class HolidaysRequestDetail(generics.RetrieveAPIView, generics.DestroyAPIView):
    model = models.HolidaysRequest
    serializer_class = serializers.HolidaysRequestSerializer
    permission_classes = (HolidaysPermission,)
    lookup_field = "pk"


class HolidaysList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        days = sum([hr.get_working_days() for hr in request.user.holidays_requests.all()], [])

        year = self.request.GET.get('year', None)
        if year:
            days = [d for d in days if str(d.year)==year]

        month = self.request.GET.get('month', None)
        if month:
            days = [d for d in days if str(d.month)==month]

        return Response([serializers.DaySerializer(d).data for d in days])


