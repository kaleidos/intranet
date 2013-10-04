# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework import (
    generics,
    permissions
)

from intranet import models
from intranet import serializers
from intranet import exceptions


class ProjectList(generics.ListAPIView):
    model = models.Project
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = settings.API_DEFAULT_PAGE_SIZE
    paginate_by_param = "page_size"

    def get_queryset(self):
        queryset = super(ProjectList, self).get_queryset()

        # User permissions
        queryset = queryset.filter(employees=self.request.user)

        # Filter by type
        project_type = self.request.GET.get("type", 'active')
        if project_type not in ['active', 'inactive', 'all']:
            raise exceptions.InvalidParamError("Invalid type")

        if project_type == "active":
            queryset = queryset.filter(active=True)
        elif project_type == "inactive":
            queryset = queryset.filter(active=False)

        return queryset
