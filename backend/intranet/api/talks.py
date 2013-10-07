# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from intranet import models
from intranet import serializers


class TalkViewSet(ModelViewSet):
    queryset = models.Talk.objects.filter(obsolete=False)
    serializer_class = serializers.TalkSerializer
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"
