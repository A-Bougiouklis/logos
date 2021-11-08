from __future__ import annotations
from neomodel import (
    IntegerProperty,
    ArrayProperty,
    StructuredNode,
    StringProperty,
)
from dataclasses import dataclass
from web.core.analysis.phrase_identifier import group_tokens_to_phrases


from web.core.analysis.phrase_identifier import Phrase
from web.core.models.entities import EntitySet, Entity


RULE_CONFIDENCE_REDUCER = 10

class Rule(StructuredNode):
    ...


class ParentalRulePhraseNotEntitySetException(Exception):
    """
    Raised when we attempt to create a ParentalRule from a non EntitySet phrase.
    """
    ...


class ParentalRuleNoSecondaryEntitySetException(Exception):
    """
    Raised when we attempt to create a ParentalRule from a non EntitySet phrase.
    """
    ...


@dataclass
class ParentalRuleResult:
    disjoint: str = "DISJOINT"
    siblings: str = "SIBLINGS"
    es1_parent_es2: str = "ES1 PARENT ES2"
    es2_parent_es1: str = "ES2 PARENT ES1"


class ParentalRule(Rule):
    """
    A rule which sets an entity set as a parent to a second entity set based on
    their common properties.

    sentence_pattern: Is generated out the sentence which made the system __approximate
    the parental relationship between entity sets
    """

    sentence_pattern = StringProperty(unique_index=True, required=True)
    approximations = ArrayProperty(StringProperty(), required=True)
    frequency = IntegerProperty(default=1)

    @classmethod
    def create_or_update(
            cls, entity_set_phrase: Phrase, node_cache: dict[str: Entity]
    ) -> ParentalRule:

        phrases = cls.entity_set_phrases(entity_set_phrase, node_cache)
        sentence_pattern = cls.__sentence_pattern_from_phrases(phrases)

        if rules := cls.nodes.filter(sentence_pattern=sentence_pattern):
            rule = rules[0]
            rule.update(entity_set_phrase, phrases)
        else:
            rule = cls.__create_rule(entity_set_phrase, phrases, sentence_pattern)
        return rule

    @staticmethod
    def entity_set_phrases(
            entity_set_phrase: Phrase, node_cache: dict[str: Entity]
    ) -> list[Phrase]:
        verb_chunks_phrases = group_tokens_to_phrases(entity_set_phrase.verb_chunk, [])
        adjective_chunk_phrases = group_tokens_to_phrases(
            entity_set_phrase.adjective_chunk, []
        )

        phrases = [entity_set_phrase] + verb_chunks_phrases + adjective_chunk_phrases

        for phrase in phrases:
            if node := node_cache.get(phrase.span.text):
                phrase.node = node
            else:
                phrase.node = Entity.nodes.get(phrase.span.text)

        return phrases

    @classmethod
    def __sentence_pattern_from_phrases(cls, phrases: list[Phrase]) -> str:
        """
        Returns the longest generated sentence pattern from the given phrases
        """
        try:
            return cls.__every_sentence_pattern_from_phrases(phrases)[-1]
        except IndexError:
            return ""

    @staticmethod
    def __every_sentence_pattern_from_phrases(phrases: list[Phrase]) -> list[str]:
        """
        Generates every sentence pattern for the given phrases.

        These can be used to query for possible parental rules that can be applied to
        the given phrases.
        """
        patterns = []
        q = ""
        for i, phrase in enumerate(phrases):
            if phrase.node_type == EntitySet:
                q+="(:EntitySet)"
            else:
                q+=f"(:Entity {{text: '{phrase.span.text}'}})"
            patterns.append(q)
            if i<len(phrases)-1:
                q+="-[:SENTENCE]->"

        return patterns

    @classmethod
    def __create_rule(
            cls, entity_set_phrase: Phrase, phrases: list[Phrase], sentence_pattern: str
    ):

        if sentence_pattern.count("EntitySet") < 2:
            raise ParentalRuleNoSecondaryEntitySetException

        return cls(
            approximations = cls.__approximations_for_phrases(entity_set_phrase, phrases),
            sentence_pattern = sentence_pattern
        ).save()

    @classmethod
    def __approximations_for_phrases(
            cls, entity_set_phrase: Phrase, phrases: list[Phrase]
    )-> list[str]:

        return [
            cls.__approximate(entity_set_phrase.node, phrase.node)
            for phrase in phrases
            if phrase.node_type == EntitySet and entity_set_phrase.node != phrase.node
        ]

    @staticmethod
    def __approximate(entity_set_1: EntitySet, entity_set_2: EntitySet) -> str:

        entity_set_1_properties = entity_set_1.not_defined_properties_as_set
        entity_set_2_properties = entity_set_2.not_defined_properties_as_set
        common_properties = entity_set_1_properties.intersection(entity_set_2_properties)

        if not common_properties:
            return ParentalRuleResult.disjoint
        elif entity_set_1_properties == common_properties == entity_set_2_properties:
            return ParentalRuleResult.siblings
        elif entity_set_1_properties == common_properties:
            return ParentalRuleResult.es1_parent_es2
        else:
            return ParentalRuleResult.es1_parent_es2

    def update(self, entity_set_phrase: Phrase, sentence_phrases: list[Phrase]):
        """
        We count how many approximations with the new entity set match the existing
        approximations.
        If most of the match then we bump the frequency counter. Else we decrease it.
        If the frequency counter is equal or less to 0 then we update the approximation
        list with the new approximations.
        """

        new_approximation = self.__approximations_for_phrases(
            entity_set_phrase, sentence_phrases
        )

        score = 0
        for new, old in zip(new_approximation, self.approximations):
            if new == old:
                score += 1
            else:
                score -= 1

        self.frequency = self.frequency + 1 if score > 0 else self.frequency - 1

        if self.frequency <= 0:
            self.approximations = new_approximation
            self.frequency = 1
        self.save()

    @property
    def confidence(self) -> float:
        """
        The confidence is related to how many times we have encountered the approximated
        results in the training set.
        """

        return RULE_CONFIDENCE_REDUCER/self.frequency


class CommonProperiesRule(Rule):
    ...
