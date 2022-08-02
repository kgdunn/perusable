from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Term
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from . import constants  # new
from .models import Wine  # , WineSearchWord
from .serializers import WineSerializer  # , WineSearchWordSerializer
from .filters import WineFilterSet  # t, WineSearchWordFilterSet


class WinesView(ListAPIView):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    filterset_class = WineFilterSet


class WineSearchWordsView(ListAPIView):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    filterset_class = WineFilterSet


class ESWinesView(APIView):
    def get(self, request, *args, **kwargs):
        query = self.request.query_params.get("query")

        # Build Elasticsearch query.
        search = Search(index=constants.ES_INDEX)  # changed
        response = (
            search.query(
                "bool",
                should=[Match(variety=query), Match(winery=query), Match(description=query)],
            )
            .params(size=100)
            .execute()
        )

        if response.hits.total.value > 0:
            return Response(
                data=[
                    {
                        "id": hit.meta.id,
                        "country": hit.country,
                        "description": hit.description,
                        "points": hit.points,
                        "price": hit.price,
                        "variety": hit.variety,
                        "winery": hit.winery,
                    }
                    for hit in response
                ]
            )
        else:
            return Response(data=[])
