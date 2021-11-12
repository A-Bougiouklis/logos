from django.test import TestCase
from neomodel import clear_neo4j_database, db
from web.core.analysis.nlp_models import nlp
from web.core.models.rules import *
from web.core.analysis.phrase_identifier import group_tokens_to_phrases, Phrase
from web.core.analysis.chunking import find_chunks
from web.core.analysis.entity_graph import generate_entity_graph
from web.core.analysis.property_setter import property_setter


class CommonPropertiesRuleTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

        self.analyse_text("The big cat ate some poop.")
        phrases = self.analyse_text("The big dog ate some poop.")
        self.the_big_dog = phrases[0]

    @staticmethod
    def analyse_text(text: str) -> list[Phrase]:
        doc = nlp(text)
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})
        property_setter(phrases, {})
        return phrases

    def test_create_or_update_with_no_common_properties(self):
        with self.assertRaises(NoCommonPropertiesException):
            CommonPropertiesRule.create_or_update(self.the_big_dog)

    def test_create_or_update_creates_new_rule(self):
        self.analyse_text("The big horse ate some poop.")
        rule = CommonPropertiesRule.create_or_update(self.the_big_dog)

        self.assertEqual(
            EntitySet.nodes.similar_entity_set_pattern(self.the_big_dog.span),
            rule.pattern
        )
        self.assertEqual(3, rule.frequency)
        self.assertEqual(["ate : ['some poop']"], rule.properties)
