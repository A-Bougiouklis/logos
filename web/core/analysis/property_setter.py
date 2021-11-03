from web.core.analysis.phrase_identifier import Phrase
from web.core.models import EntitySet


def property_setter(phrases: list[Phrase]) -> list[Phrase]:
    """
    It sets the properties for each entity set.
    """

    for phrase in phrases:
        if isinstance(phrase.node, EntitySet):
            phrase.node.set_property(phrase.verb_chunk.text, phrase.adjective_chunk.text)
    return phrases
