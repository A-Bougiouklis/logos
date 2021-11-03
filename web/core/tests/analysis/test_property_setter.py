from django.test import TestCase
from neomodel import clear_neo4j_database

from web.core.models import db, EntitySet
from web.core.analysis import property_setter
from web.core.analysis.phrase_identifier import group_tokens_to_phrases
from web.core.analysis.entity_graph import generate_entity_graph
from web.core.analysis.chunking import find_chunks
from web.core.analysis.nlp_models import nlp


class PropertySetterTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

    def test_sets_the_properties_to_the_entity_sets(self):

        doc = nlp("the big dog ate some poop")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})
        phrases, _ = property_setter(phrases, {})

        the_big_dog = phrases[0]
        self.assertEqual(
            getattr(the_big_dog.node, the_big_dog.verb_chunk.text),
            [the_big_dog.adjective_chunk.text]
        )

        stored_the_big_dog = EntitySet.nodes.get(text=the_big_dog.span.text)
        self.assertEqual(
            getattr(stored_the_big_dog, the_big_dog.verb_chunk.text),
            [the_big_dog.adjective_chunk.text]
        )

    def test_updates_the_cache(self):

        doc = nlp("the big dog ate some poop")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})

        cache = {phrases[0].span.text: phrases[0].node}

        self.assertFalse(hasattr(phrases[0].node, phrases[0].verb_chunk.text))

        phrases, cache = property_setter(phrases, cache)

        self.assertEqual(
            getattr(cache[phrases[0].span.text], phrases[0].verb_chunk.text),
            [phrases[0].adjective_chunk.text]
        )
