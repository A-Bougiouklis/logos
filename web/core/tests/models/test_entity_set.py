from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models.entities import db, EntitySet
from web.core.analysis.nlp_models import nlp
from web.core.analysis.entity_graph import generate_entity_graph
from web.core.analysis.chunking import find_chunks
from web.core.analysis.phrase_identifier import group_tokens_to_phrases

class EntitySetNodeSetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

        doc = nlp("The big dog ate some poop.")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})
        self.the_big_dog = phrases[0]

        doc = nlp("The big cat ate some poop.")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})

    def test_similar_entity_set_as(self):
        nodes = EntitySet.nodes.similar_entity_set_as(self.the_big_dog.span)
        self.assertEqual(1, len(nodes))

        self.assertEqual(EntitySet, type(nodes[0]))
        self.assertEqual("The big cat", nodes[0].text)


class EntitySetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

    def test_not_defined_properties(self):
        doc = nlp("The big dog")

        dog_entity_set = EntitySet.get_or_create(doc[2])
        dog_entity_set.set_property("ate", "some poop")
        dog_entity_set.set_property("ate", "a brisket")
        dog_entity_set.set_property("caught", "the ball")

        self.assertEqual(
            {"ate": ["some poop", "a brisket"], "caught": ["the ball"]},
            dog_entity_set.not_defined_properties
        )

    def test_set_property(self):
        doc = nlp("The big dog")

        dog_entity_set = EntitySet.get_or_create(doc[2])

        with self.subTest("create_new_properties"):
            dog_entity_set.set_property("ate", "some poop")
            self.assertEqual(["some poop"], dog_entity_set.ate)

        with self.subTest("does_not_duplicate_properties"):
            dog_entity_set.set_property("ate", "some poop")
            self.assertEqual(["some poop"], dog_entity_set.ate)

        with self.subTest("adds_new_values_in_existing_properties"):
            dog_entity_set.set_property("ate", "some cat food")
            self.assertCountEqual(["some poop", "some cat food"], dog_entity_set.ate)
