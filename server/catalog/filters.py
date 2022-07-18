from django_filters.rest_framework import CharFilter, FilterSet

from .models import Wine


class WineFilterSet(FilterSet):
    query = CharFilter(method="filter_query")

    def filter_query(self, queryset, name, value):
        return queryset.search(value)

    class Meta:
        model = Wine
        fields = (
            "query",
            "country",
            "points",
        )
