from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import CharField, F, Func, Q, TextField, Value  

from django_filters.rest_framework import CharFilter, FilterSet

from .models import Wine


class WineFilterSet(FilterSet):
    query = CharFilter(method="filter_query")

   
    def filter_query(self, queryset, name, value):
        search_query = Q(Q(search_vector=SearchQuery(value)))
        return (
            queryset.annotate(
                variety_headline=Func(
                    F("variety"),
                    SearchQuery(value, output_field=CharField()),
                    Value(
                        "StartSel = <mark>, StopSel = </mark>, HighlightAll=TRUE",
                        output_field=CharField(),
                    ),
                    function="ts_headline",
                ),
                winery_headline=Func(
                    F("winery"),
                    SearchQuery(value, output_field=CharField()),
                    Value(
                        "StartSel = <mark>, StopSel = </mark>, HighlightAll=TRUE",
                        output_field=CharField(),
                    ),
                    function="ts_headline",
                ),
                description_headline=Func(
                    F("description"),
                    SearchQuery(value, output_field=TextField()),
                    Value(
                        "StartSel = <mark>, StopSel = </mark>, HighlightAll=TRUE",
                        output_field=TextField(),
                    ),
                    function="ts_headline",
                ),
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
