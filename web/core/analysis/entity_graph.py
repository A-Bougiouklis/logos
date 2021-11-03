from core.analysis.phrase_identifier import Phrase
from web.core.models import EntitySet, Entity


def generate_entity_graph(
    phrases: list[Phrase],
    doc_id: int,
    sent_id: int,
    cached_entities: dict[str, Entity],
) -> dict[str, Entity]:
    """
    It analyse the given sentence by creating or updating the Entity nodes.
    """

    index = 0
    while index < len(phrases):

        phrase = phrases[index]
        entity_node, cached_entities = __get_node(phrase, cached_entities)

        # Connect sentence relationships
        if next_phrase := phrases[index + 1] if index < len(phrases) - 1 else None:
            next_entity_node, cached_entities = __get_node(next_phrase, cached_entities)
            entity_node.sentence.connect(
                next_entity_node,
                {
                    "document_id": doc_id,
                    "sentence_id": sent_id,
                    "order": index
                }
            )

        index += 1

    return cached_entities


def __get_node(
        phrase: Phrase, cached_nodes: dict[str, Entity]
) -> tuple[Entity, dict[str, Entity]]:
    node = cached_nodes.get(phrase.span.text)
    if node is None:
        node = phrase.node_type.get_or_create(phrase.span)
        node.generate_synonyms(phrase.span)
        cached_nodes[phrase.span.text] = node
    return node, cached_nodes
