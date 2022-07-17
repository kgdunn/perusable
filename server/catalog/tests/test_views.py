# server/catalog/tests/test_views.py

from rest_framework.test import APIClient, APITestCase

from catalog.models import Wine


class ViewTests(APITestCase):

    def test_empty_query_returns_everything(self):
        wine = Wine.objects.create(
            country='US',
            description='A delicious bottle of wine.',
            points=90,
            price=100.00,
            variety='Cabernet Sauvignon',
            winery='Stag\'s Leap'
        )
        client = APIClient()
        response = client.get('/api/v1/catalog/wines/')
        self.assertJSONEqual(response.content, [{
            'country': 'US',
            'description': 'A delicious bottle of wine.',
            'id': str(wine.id),
            'points': 90,
            'price': '100.00',
            'variety': 'Cabernet Sauvignon',
            'winery': 'Stag\'s Leap',
        }])
