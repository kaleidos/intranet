from rest_framework import filters

from intranet import models, exceptions

from django.db.models import Count


class IsEmployeeFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(employee=request.user)


class InEmployeesFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(employees=request.user)


class YearFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        year = request.QUERY_PARAMS.get('year', None)
        if year:
            return queryset.filter(year__id=year)
        return queryset


class PartTypeFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        part_type = request.QUERY_PARAMS.get("type", "all")
        if part_type not in ["all", "accepted", "rejected", "sent", "pending"]:
            raise exceptions.InvalidParamError("Invalid type")

        if part_type == "accepted":
            return queryset.filter(state=models.STATE_ACCEPTED)
        elif part_type == "rejected":
            return queryset.filter(state=models.STATE_REJECTED)
        elif part_type == "sent":
            return queryset.filter(state=models.STATE_SENT)
        elif part_type == "pending":
            return queryset.filter(state=models.STATE_CREATED)
        return queryset


class ProjectTypeFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        project_type = request.QUERY_PARAMS.get("type", "active")
        if project_type not in ["all", "active", "inactive"]:
            raise exceptions.InvalidParamError("Invalid type")

        if project_type == "active":
            return queryset.filter(active=True)
        elif project_type == "inactive":
            return queryset.filter(active=False)
        return queryset

class OrderingTalksFilterBackend(filters.OrderingFilter):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        queryset = super(OrderingTalksFilterBackend, self).filter_queryset(request, queryset, view)
        ordering = request.QUERY_PARAMS.get("ordering")
        if ordering == "wanters_count":
            return queryset.annotate(agg_wanters_count=Count("wanters")).order_by("agg_wanters_count")
        elif ordering == "-wanters_count":
            return queryset.annotate(agg_wanters_count=Count("wanters")).order_by("-agg_wanters_count")
        elif ordering == "talkers_count":
            return queryset.annotate(agg_talkers_count=Count("talkers")).order_by("agg_talkers_count")
        elif ordering == "-talkers_count":
            return queryset.annotate(agg_talkers_count=Count("talkers")).order_by("-agg_talkers_count")
        elif ordering == "-created_date":
            return queryset.order_by("-created_date", "-id")
        if ordering == "-wanters_count_talkers_ready":
            return queryset.annotate(agg_wanters_count=Count("wanters"),
                                     agg_talkers_count=Count("talkers")).order_by("-talkers_are_ready",
                                                                                  "-agg_talkers_count",
                                                                                  "-agg_wanters_count",)
        return queryset
