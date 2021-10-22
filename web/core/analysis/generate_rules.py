from .phrase_identifier import Phrase
from core.models import Entity, EntitySet

def generate_rules(phrases: list[Phrase]):

    entity_phrases, entity_set_phrases = split_phrases(phrases)


def split_phrases(phrases: list[Phrase]) -> tuple[list[Phrase], list[Phrase]]:

    entity_phrases = []
    entity_set_phrases = []
    for phrase in phrases:
        if phrase.node_type == Entity:
            entity_phrases.append(phrase)
        elif phrase.node_type == EntitySet:
            entity_set_phrases.append(phrase)
        else:
            raise ValueError("Unknown phrase.node_type")
    return entity_phrases, entity_set_phrases


def rules_from_properties(phrases: list[Phrase]):
    """
    1. I need to identify if there are other entity sets mentioned in the properties.
    2. I need to find the common properties between entity sets
    3. I need to make a conclusion about the words in property
    4. I need to make a query which will represent the entities in the property and the entity sets will be wild cards.
    """
    ...

def rules_from_complimentary_tokens(phrases: list[Phrase]):
    """
    Only if an entity set is structured from multiple tokens
    1. Get all the tokens from the entity set name except the root
    2. Get all the entity sets which include all the tokens from step 1
    3. Search for common properties
    4. I need to make a conclusion about the words in property
    5. I need to make a query which will represent the entities in the property and the entity sets will be wild cards.
    """
    ...
