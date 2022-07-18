# server/catalog/tests/test_views.py

from rest_framework.test import APIClient, APITestCase
from django.contrib.postgres.search import SearchVector

from catalog.models import Wine
from catalog.serializers import WineSerializer


def setUp(self):
    # Update fixture data search vector fields
    Wine.objects.all().update(
        search_vector=(
            SearchVector("variety", weight="A")
            + SearchVector("winery", weight="A")
            + SearchVector("description", weight="B")
        )
    )

    self.client = APIClient()


class ViewTests(APITestCase):
    fixtures = ["test_wines.json"]

    def setUp(self):
        self.client = APIClient()

    # changed
    def test_empty_query_returns_everything(self):
        response = self.client.get("/api/v1/catalog/wines/")
        wines = Wine.objects.all()
        self.assertJSONEqual(response.content, WineSerializer(wines, many=True).data)

    def test_query_matches_variety(self):
        response = self.client.get("/api/v1/catalog/wines/?query=Cabernet")
        self.assertEquals(1, len(response.data))
        self.assertEquals("58ba903f-85ff-45c2-9bac-6d0732544841", response.data[0]["id"])

    def test_query_matches_winery(self):
        response = self.client.get("/api/v1/catalog/wines/?query=Barnard")
        self.assertEquals(1, len(response.data))
        self.assertEquals("21e40285-cec8-417c-9a26-4f6748b7fa3a", response.data[0]["id"])

    def test_query_matches_description(self):
        response = self.client.get("/api/v1/catalog/wines/?query=wine")
        self.assertEquals(4, len(response.data))
        self.assertCountEqual(
            [
                "58ba903f-85ff-45c2-9bac-6d0732544841",
                "21e40285-cec8-417c-9a26-4f6748b7fa3a",
                "0082f217-3300-405b-abc6-3adcbecffd67",
                "000bbdff-30fc-4897-81c1-7947e11e6d1a",
            ],
            [item["id"] for item in response.data],
        )

    def test_can_filter_on_country(self):
        response = self.client.get("/api/v1/catalog/wines/?country=France")
        self.assertEquals(2, len(response.data))
        self.assertCountEqual(
            [
                "0082f217-3300-405b-abc6-3adcbecffd67",
                "000bbdff-30fc-4897-81c1-7947e11e6d1a",
            ],
            [item["id"] for item in response.data],
        )

    def test_can_filter_on_points(self):
        response = self.client.get("/api/v1/catalog/wines/?points=87")
        self.assertEquals(1, len(response.data))
        self.assertEquals("21e40285-cec8-417c-9a26-4f6748b7fa3a", response.data[0]["id"])

    def test_country_must_be_exact_match(self):
        response = self.client.get("/api/v1/catalog/wines/?country=Frances")
        self.assertEquals(0, len(response.data))
        self.assertJSONEqual(response.content, [])

    def test_search_results_returned_in_correct_order(self):
        response = self.client.get("/api/v1/catalog/wines/?query=Chardonnay")
        self.assertEquals(2, len(response.data))
        self.assertListEqual(
            [
                "0082f217-3300-405b-abc6-3adcbecffd67",
                "000bbdff-30fc-4897-81c1-7947e11e6d1a",
            ],
            [item["id"] for item in response.data],
        )

    def test_search_vector_populated_on_save(self):
        wine = Wine.objects.create(
            country="US", points=80, price=1.99, variety="Pinot Grigio", winery="Charles Shaw"
        )
        wine = Wine.objects.get(id=wine.id)
        self.assertEqual("'charl':3A 'grigio':2A 'pinot':1A 'shaw':4A", wine.search_vector)
