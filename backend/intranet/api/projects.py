# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import permissions, viewsets

from intranet import models
from intranet import serializers
from intranet.api.filters import InEmployeesFilterBackend, ProjectTypeFilterBackend


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (InEmployeesFilterBackend, ProjectTypeFilterBackend)
