from django.test import TestCase
from neomodel import clear_neo4j_database

from web.core.models import Token
from neomodel import db


class TokenNodeSetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

    def test_max_document_id_with_no_ralationships_with_document_id_properties(self):
        self.assertEqual(0, Token.nodes.max_document_id)

    def test_max_document_id_when_relationships_with_document_id_properties_exist(self):
        token_0 = Token(token="example_0").save()
        token_1 = Token(token="example_1").save()
        token_2 = Token(token="example_2").save()

        token_0.sentence.connect(token_1, {"document_id": 0})
        token_1.sentence.connect(token_2, {"document_id": 1})
        token_2.sentence.connect(token_0, {"document_id": 2})

        self.assertEqual(2, Token.nodes.max_document_id)
