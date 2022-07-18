from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, Q  # changed

from django_filters.rest_framework import CharFilter, FilterSet

from .models import Wine, SearchHeadline 


class WineFilterSet(FilterSet):
    query = CharFilter(method="filter_query")

    
    def filter_query(self, queryset, name, value):
        search_query = Q(Q(search_vector=SearchQuery(value)))
        return (
            queryset.annotate(
                variety_headline=SearchHeadline(F("variety"), SearchQuery(value)),
                winery_headline=SearchHeadline(F("winery"), SearchQuery(value)),
                description_headline=SearchHeadline(F("description"), SearchQuery(value)),
                search_rank=SearchRank(F("search_vector"), SearchQuery(value)),
            )
            .filter(search_query)
            .order_by("-search_rank", "id")
        )

    class Meta:
        model = Wine
        fields = (
            "query",
            "country",
            "points",
        )
