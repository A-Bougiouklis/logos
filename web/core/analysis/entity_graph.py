from core.analysis.phrase_identifier import Phrase
from web.core.models import EntitySet, Entity


def generate_entity_graph(
    phrases: list[Phrase],
    doc_id: int,
    sent_id: int,
    cached_entities: dict[str, Entity],
    cached_entity_sets: dict[str, EntitySet],
) -> tuple[dict[str, Entity], dict[str, Entity]]:
    """
    It analyse the given sentence by creating or updating the Entity nodes.
    """

    index = 0
    while index < len(phrases):

        phrase = phrases[index]
        entity_node, cached_entities, cached_entity_sets = __get_entity_node(
            phrase, cached_entities, cached_entity_sets
        )

        # Connect sentence relationships
        if next_phrase := phrases[index + 1] if index < len(phrases) - 1 else None:
            next_entity_node, cached_entities, cached_entity_sets = __get_entity_node(
            next_phrase, cached_entities, cached_entity_sets
            )
            entity_node.sentence.connect(
                next_entity_node,
                {
                    "document_id": doc_id,
                    "sentence_id": sent_id,
                    "order": index
                }
            )

        index += 1

    return cached_entities, cached_entity_sets


def __get_entity_node(
        phrase: Phrase,
        cached_entities: dict[str, Entity],
        cached_entity_sets: dict[str, EntitySet]
) -> tuple[Entity, dict[str, Entity], dict[str, EntitySet]]:

    if phrase.node_type == Entity:
        entity_node, cached_entities = __get_node(phrase, cached_entities)
    elif phrase.node_type == EntitySet:
        entity_node, cached_entity_sets = __get_node(
            phrase, cached_entity_sets
        )
        entity_node.set_property(phrase.verb_chunk.text, phrase.adjective_chunk.text)
        entity_node.save()
    else:
        raise ValueError("Wrong node type assigned to phrase.")

    return entity_node, cached_entities, cached_entity_sets


def __get_node(
        phrase: Phrase, cached_nodes: dict[str, Entity]
) -> tuple[Entity, dict[str, Entity]]:
    node = cached_nodes.get(phrase.span.text)
    if node is None:
        node = phrase.node_type.get_or_create(phrase.span)
        cached_nodes[phrase.span.text] = node
    return node, cached_nodes
