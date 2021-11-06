from web.core.analysis.phrase_identifier import Phrase
from web.core.models.entities import EntitySet, Entity


def property_setter(
        phrases: list[Phrase], cached_entities: dict[str, Entity]
) -> tuple[list[Phrase], dict[str, Entity]]:
    """
    - Sets the properties for each entity set.
    - Update the given cache dict.
    """

    for phrase in phrases:
        if isinstance(phrase.node, EntitySet):
            phrase.node.set_property(phrase.verb_chunk.text, phrase.adjective_chunk.text)
            cached_entities[phrase.span.text] = phrase.node
    return phrases, cached_entities
