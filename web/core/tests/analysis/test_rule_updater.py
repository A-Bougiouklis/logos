from django.test import TestCase
from neomodel import clear_neo4j_database, db
from web.core.analysis.nlp_models import nlp
from web.core.analysis.phrase_identifier import group_tokens_to_phrases, Phrase
from web.core.analysis.chunking import find_chunks
from web.core.analysis.entity_graph import generate_entity_graph
from web.core.analysis.property_setter import property_setter
from web.core.models.entities import Entity
from web.core.models.rules import ParentalRule, ParentalRuleResult, CommonPropertiesRule
from web.core.analysis.rule_updater import update_rules

class RuleUpdaterTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)
        self.cache = {}
        self.analyse_text("The big cat ate some poop.")
        self.analyse_text("The big dog ate some poop.")
        self.analyse_text("The big horse ate some poop.")
        self.analyse_text("a legal entity belongs in a legal corporation")
        self.analyse_text("a counterparty is a legal entity")


    def analyse_text(self, text: str) -> list[Phrase]:
        doc = nlp(text)
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})
        self.cache = {**self.create_cache(phrases), **self.cache}
        phrases, self.cache = property_setter(phrases, self.cache)
        update_rules(phrases, self.cache)
        return phrases

    @staticmethod
    def create_cache(phrases: list[Phrase]) -> dict[str, Entity]:
        return {phrase.span.text: phrase.node for phrase in phrases}

    def test_create_new_rules(self):
        self.assertEqual(1, len(ParentalRule.nodes.all()))
        self.assertEqual(1, len(CommonPropertiesRule.nodes.all()))

    def test_updates_existing_rules(self):

        with self.subTest("updates_parental_rules"):
            old_pr = ParentalRule.nodes.first()
            self.assertEqual([ParentalRuleResult.disjoint], old_pr.approximations)

            self.analyse_text("a counterparty belongs in a legal corporation")
            self.analyse_text("a counterparty is a legal entity")
            new_pr = ParentalRule.nodes.first()
            self.assertEqual([ParentalRuleResult.es1_parent_es2], new_pr.approximations)

        with self.subTest("updates_common_property_rules"):
            old_cpr = CommonPropertiesRule.nodes.first()
            self.assertEqual(3, old_cpr.frequency)

            self.analyse_text("The big fish ate some poop.")
            new_cpr = CommonPropertiesRule.nodes.first()
            self.assertEqual(4, new_cpr.frequency)
