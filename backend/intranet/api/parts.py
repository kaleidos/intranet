# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import (
    generics,
    permissions,
    response,
    status
)

from intranet import models
from intranet import serializers
from intranet import exceptions


class PartList(generics.ListCreateAPIView):
    model = models.Part
    serializer_class = serializers.PartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"

    def get_queryset(self):
        queryset = self.request.user.parts.all()

        # Filter by type
        if "type" in self.request.GET.keys():
            part_type = self.request.GET["type"] or "all"
            if part_type not in ["all", "accepted", "rejected", "sent", "pending"]:
                raise exceptions.InvalidParamError("Invalid type")

            if part_type == "accepted":
                queryset = queryset.filter(state=models.STATE_ACCEPTED)
            elif part_type == "rejected":
                queryset = queryset.filter(state=models.STATE_REJECTED)
            elif part_type == "sent":
                queryset = queryset.filter(state=models.STATE_SENT)
            elif part_type == "pending":
                queryset = queryset.filter(state=models.STATE_CREATED)

        return queryset

    def pre_save(self, obj):
        super(PartList, self).pre_save(obj)
        obj.employee = self.request.user


class PartDetail(generics.RetrieveUpdateAPIView):
    model = models.Part
    serializer_class = serializers.PartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "pk"

    def pre_save(self, obj):
        super(PartDetail, self).pre_save(obj)
        obj.employee = self.request.user


class PartSend(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "pk"

    def get_queryset(self):
        return self.request.user.parts.all()

    def post(self, request, *args, **kwargs):
        part = self.get_object()
        part.state = models.STATE_SENT
        part.save(update_fields=["state"])
        return response.Response(status=status.HTTP_200_OK)
