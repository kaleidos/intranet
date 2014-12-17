from rest_framework import filters

from intranet import models, exceptions

from django.db.models import Count, Sum


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
    def filter_queryset(self, request, queryset, view):
        queryset = super(OrderingTalksFilterBackend, self).filter_queryset(request, queryset, view)

        if request.method  != "GET":
            return queryset

        if "obsolete" in request.QUERY_PARAMS:
            show_obsolete = request.QUERY_PARAMS.get("obsolete", False) == u"true"
            queryset = queryset.filter(obsolete=show_obsolete)

        ordering = request.QUERY_PARAMS.get("ordering", None)
        if ordering == "-created_date":
            queryset = queryset.order_by("-created_date")
        elif ordering == "wanters_count":
            queryset = (queryset.annotate(agg_wanters_count=Count("wanters"))
                                .order_by("agg_wanters_count", "created_date" ))
        elif ordering == "-wanters_count":
            queryset = (queryset.annotate(agg_wanters_count=Count("wanters"))
                                .order_by("-agg_wanters_count", "-created_date"))
        elif ordering == "talkers_count":
            queryset = (queryset.annotate(agg_talkers_count=Count("talkers"))
                                .order_by("agg_talkers_count", "created_date"))
        elif ordering == "-talkers_count":
            queryset = (queryset.annotate(agg_talkers_count=Count("talkers"))
                                .order_by("-agg_talkers_count", "-created_date"))
        elif ordering == "-wanters_count_talkers_ready":
            queryset = (queryset.annotate(agg_wanters_count=Count("wanters"))
                                .order_by("-talkers_are_ready",
                                          "-agg_wanters_count",
                                          "-created_date"))

        if ordering == "-calendar":
            queryset = (queryset.filter(event_date__isnull=False)
                                .order_by("-event_date"))
        else:
            queryset = queryset.filter(event_date__isnull=True)

        return queryset


class QuotesByEmployeeFilterBackend(filters.BaseFilterBackend):
    """
    Filter quotes by employee.
    """
    def filter_queryset(self, request, queryset, view):
        if "employee" in request.QUERY_PARAMS:
            return queryset.filter(employee=request.QUERY_PARAMS["employee"])
        return queryset


class OrderingQuotesFilterBackend(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        queryset = super(OrderingQuotesFilterBackend, self).filter_queryset(request, queryset, view)
        ordering = request.QUERY_PARAMS.get("ordering")
        if ordering == "created_date":
            return queryset.order_by("created_date", "id")
        elif ordering == "-created_date":
            return queryset.order_by("-created_date", "-id")
        elif ordering == "score":
            extra_sql = ("select (sum(intranet_quotescore.score)) from intranet_quotescore "
                         "where intranet_quotescore.quote_id = intranet_quote.id")
            return queryset.extra(select={"score": extra_sql}, order_by=["score", "id"])
        elif ordering == "-score":
            extra_sql = ("select coalesce(sum(intranet_quotescore.score), 0) from intranet_quotescore "
                         "where intranet_quotescore.quote_id = intranet_quote.id")
            return queryset.extra(select={"score": extra_sql}, order_by=["-score", "id"])
        elif ordering == "employee":
            return queryset.order_by("employee", "external_author", "id")
        elif ordering == "-employee":
            return queryset.order_by("-employee", "-external_author", "-id")
        return queryset
