from rest_framework.generics import ListAPIView

from .filters import WineFilterSet
from .models import Wine
from .serializers import WineSerializer


class WinesView(ListAPIView):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    filterset_class = WineFilterSet
