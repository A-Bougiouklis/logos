from django.test import TestCase
from neomodel import clear_neo4j_database

from web.core.models import db, Entity, EntitySet
from web.core.analysis.nlp_models import nlp
from web.core.analysis.entity_graph import generate_entity_graph
from web.core.analysis.phrase_identifier import group_tokens_to_phrases, Phrase
from web.core.analysis.chunking import find_chunks


class GenerateEntityGraph(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

    def entity_graph_asserts(
            self, phrases: list[Phrase], doc_id: int, sent_id: int
    ):
        for index, phrase in enumerate(phrases[:-1]):

            if phrase.node_type == Entity:
                entity_node = Entity.nodes.get(text=phrase.span.text)
            else:
                entity_node = EntitySet.nodes.get(text=phrase.span.text)

            with self.subTest(f"creates entity -> {phrase.span.text}"):
                self.assertEqual(phrase.span.text, entity_node.text)

            try:
                with self.subTest(
                    f"({phrase.span.text})-[SENTENCE]-({phrases[index+1].span.text})"
                ):
                    next_entity_node = Entity.nodes.get(text=phrases[index+1].span.text)
                    r = entity_node.sentence.relationship(next_entity_node)

                    self.assertIsNotNone(r)
                    self.assertEqual(doc_id, r.document_id)
                    self.assertEqual(sent_id, r.sentence_id)
                    self.assertEqual(index, r.order)
            except IndexError:
                pass

    def test_entity_graph_without_cache(self):

        doc = nlp("the big dog ate some poop and then got away from the police.")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        generate_entity_graph(phrases, 1, 2, {}, {})
        self.entity_graph_asserts(phrases, 1, 2)

    def test_entity_graph_with_cache(self):
        doc = nlp("the big dog ate some poop and then got away from the police.")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        cached_entities, cached_entity_sets = generate_entity_graph(
            phrases, 1, 2, {}, {}
        )

        doc = nlp("the big dog ate a cow.")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        generate_entity_graph(phrases, 2, 3, cached_entities, cached_entity_sets)
        self.entity_graph_asserts(phrases, 2, 3)

    def test_entity_graph_with_existing_entity_set_as_entity(self):

        doc = nlp("the big dog ate some poop and then got away from the police.")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        generate_entity_graph(phrases, 1, 2, {}, {})

        doc = nlp("the police officer caught the big dog")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        generate_entity_graph(phrases, 1, 3, {}, {})

        caught = Entity.nodes.get(text="caught")
        the_big_dog = EntitySet.nodes.get(text="the big dog")
        ate = Entity.nodes.get(text="ate")

        self.assertIsNotNone(caught.sentence.relationship(the_big_dog))
        self.assertIsNotNone(the_big_dog.sentence.relationship(ate))
