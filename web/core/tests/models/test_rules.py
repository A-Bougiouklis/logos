from django.test import TestCase
from neomodel import clear_neo4j_database, db
from web.core.analysis.nlp_models import nlp
from web.core.models.rules import *
from web.core.analysis.phrase_identifier import group_tokens_to_phrases, Phrase
from web.core.analysis.chunking import find_chunks
from web.core.analysis.entity_graph import generate_entity_graph
from web.core.analysis.property_setter import property_setter
from web.core.models.entities import Entity


class ParentalRuleNodeSetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

        self.phrases = self.analyse_sentence("a legal entity belongs in a legal corporation")
        self.cache = self.create_cache(self.phrases)
        self.phrases = self.analyse_sentence("a counterparty is a legal entity")
        self.cache = {**self.create_cache(self.phrases), **self.cache}
        self.a_counterparty = self.phrases[0]
        self.a_legal_entity = self.phrases[2]

    @staticmethod
    def analyse_sentence(text: str) -> list[Phrase]:
        doc = nlp(text)
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))
        _, phrases = generate_entity_graph(phrases, 1, 2, {})
        property_setter(phrases, {})

        return phrases

    @staticmethod
    def create_cache(phrases: list[Phrase]) -> dict[str, Entity]:
        return {phrase.span.text: phrase.node for phrase in phrases}

    def test_create_or_update_create_new_rule(self):
        rule = ParentalRule.create_or_update(self.a_counterparty, self.cache)

        self.assertEqual(1, len(ParentalRule.nodes.all()))
        self.assertEqual([ParentalRuleResult.disjoint], rule.approximations)
        self.assertEqual(
            "(:EntitySet)-[:SENTENCE]->(:Entity {text: 'is'})-[:SENTENCE]->(:EntitySet)",
            rule.pattern
        )
        self.assertEqual(1, rule.frequency)

    def test_create_or_update_create_updates_existing_rule(self):
        ParentalRule.create_or_update(self.a_counterparty, self.cache)
        rule = ParentalRule.create_or_update(self.a_counterparty, self.cache)

        self.assertEqual([ParentalRuleResult.disjoint], rule.approximations)
        self.assertEqual(
            "(:EntitySet)-[:SENTENCE]->(:Entity {text: 'is'})-[:SENTENCE]->(:EntitySet)",
            rule.pattern
        )
        self.assertEqual(2, rule.frequency)

    def test_updates_rule_positively(self):
        rule = ParentalRule.create_or_update(self.a_counterparty, self.cache)

        phrases = ParentalRule.entity_set_phrases(self.a_counterparty, self.cache)
        rule.update(self.a_counterparty, phrases)

        self.assertEqual([ParentalRuleResult.disjoint], rule.approximations)
        self.assertEqual(
            "(:EntitySet)-[:SENTENCE]->(:Entity {text: 'is'})-[:SENTENCE]->(:EntitySet)",
            rule.pattern
        )
        self.assertEqual(2, rule.frequency)

    def test_updates_rule_negatively(self):
        ParentalRule.create_or_update(self.a_counterparty, self.cache)
        rule = ParentalRule.create_or_update(self.a_counterparty, self.cache)

        self.a_legal_entity.node.set_property("is", "a legal entity")
        self.cache[self.a_legal_entity.span.text] = self.a_legal_entity.node
        phrases = ParentalRule.entity_set_phrases(self.a_counterparty, self.cache)

        rule.update(self.a_counterparty, phrases)

        self.assertEqual([ParentalRuleResult.disjoint], rule.approximations)
        self.assertEqual(
            "(:EntitySet)-[:SENTENCE]->(:Entity {text: 'is'})-[:SENTENCE]->(:EntitySet)",
            rule.pattern
        )
        self.assertEqual(1, rule.frequency)

    def test_updates_approximation(self):
        rule = ParentalRule.create_or_update(self.a_counterparty, self.cache)

        self.a_legal_entity.node.set_property("is", "a legal entity")
        self.cache[self.a_legal_entity.span.text] = self.a_legal_entity.node

        phrases = ParentalRule.entity_set_phrases(self.a_counterparty, self.cache)

        self.assertEqual([ParentalRuleResult.disjoint], rule.approximations)

        rule.update(self.a_counterparty, phrases)

        self.assertEqual([ParentalRuleResult.es1_parent_es2], rule.approximations)
        self.assertEqual(
            "(:EntitySet)-[:SENTENCE]->(:Entity {text: 'is'})-[:SENTENCE]->(:EntitySet)",
            rule.pattern
        )
        self.assertEqual(1, rule.frequency)


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
