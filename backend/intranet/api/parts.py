# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import (
    permissions,
    response,
    status,
    viewsets
)

from rest_framework.decorators import detail_route

from intranet import models
from intranet import serializers
from intranet.api.filters import IsEmployeeFilterBackend, PartTypeFilterBackend


class PartViewSet(viewsets.ModelViewSet):
    queryset = models.Part.objects.all()
    serializer_class = serializers.PartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"
    filter_backends = (IsEmployeeFilterBackend, PartTypeFilterBackend)

    def pre_save(self, obj):
        super(PartViewSet, self).pre_save(obj)
        obj.employee = self.request.user

    @detail_route(methods=["post"])
    def send(self, request, *args, **kwargs):
        part = self.get_object()
        part.state = models.STATE_SENT
        part.save(update_fields=["state"])
        return response.Response(status=status.HTTP_200_OK)
