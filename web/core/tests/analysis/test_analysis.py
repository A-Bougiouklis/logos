from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models.entities import db, EntitySet, Entity
from web.core.analysis import document_analysis


class EntitySetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

    def test_document_analysis_creates_entity_graph(self):
        sentence = """The masked language model randomly masks some of the tokens from the input, and the objective is to predict the original vocabulary id of the masked"""

        document_analysis(sentence, {})
        self.assertEqual(4, len(EntitySet.nodes.all()))
        self.assertEqual(22, len(Entity.nodes.all()))
