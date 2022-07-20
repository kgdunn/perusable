import json
import pathlib
from unittest.mock import patch
import uuid

from django.conf import settings
from django.contrib.postgres.search import SearchVector

from elasticsearch_dsl import connections
from rest_framework.test import APIClient, APITestCase

from catalog.constants import ES_MAPPING
from catalog.models import Wine, WineSearchWord
from catalog.serializers import WineSerializer


class ViewTests(APITestCase):
    fixtures = ["test_wines.json"]


class ESViewTests(APITestCase):
    def setUp(self):
        self.index = f"test-wine-{uuid.uuid4()}"
        self.connection = connections.get_connection()
        self.connection.indices.create(
            index=self.index,
            body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                },
                "mappings": {
                    "properties": {
                        "variety": {
                            "type": "text",
                            "analyzer": "english",
                        },
                        "winery": {
                            "type": "text",
                            "analyzer": "english",
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "english",
                        },
                    }
                },
            },
        )

        # Load fixture data
        fixture_path = pathlib.Path(settings.BASE_DIR / "catalog" / "fixtures" / "test_wines.json")
        with open(fixture_path, "rt") as fixture_file:
            fixture_data = json.loads(fixture_file.read())
            for wine in fixture_data:
                fields = wine["fields"]
                self.connection.create(
                    index=self.index,
                    id=fields["id"],
                    body={
                        "description": fields["description"],
                        "variety": fields["variety"],
                        "winery": fields["winery"],
                    },
                    refresh=True,
                )

    def test_query_matches_variety(self):
        response = self.client.get("/api/v1/catalog/es-wines/?query=Cabernet")
        self.assertEquals(1, len(response.data))
        self.assertEquals("58ba903f-85ff-45c2-9bac-6d0732544841", response.data[0]["id"])

    def tearDown(self):
        self.connection.indices.delete(index=self.index)
