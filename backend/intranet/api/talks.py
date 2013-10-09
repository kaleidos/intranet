# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route

from intranet import models
from intranet import serializers

from intranet.api.filters import OrderingTalksFilterBackend


class TalkViewSet(ModelViewSet):
    queryset = models.Talk.objects.filter(obsolete=False)
    serializer_class = serializers.TalkSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (OrderingTalksFilterBackend,)
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
