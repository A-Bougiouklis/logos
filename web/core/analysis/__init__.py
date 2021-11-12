from spacy.tokens.doc import Doc as spacy_doc

from web.core.models.entities import Entity, EntitySet
from .chunking import find_chunks
from .entity_graph import generate_entity_graph
from .phrase_identifier import group_tokens_to_phrases
from .property_setter import property_setter
from .rule_updater import update_rules
from web.core.analysis.nlp_models import nlp


def document_analysis(document: str, cached_nodes):
    """
    It divides the given document into sentences and then it generates the entity graph.
    """

    doc_id = Entity.nodes.max_document_id + 1
    sen_id = Entity.nodes.max_sentence_id + 1

    # cached_entity_nodes = {}

    doc = nlp(document)
    for sent in doc.sents:
        # We convert the sentence to a doc to remove any index connection between the
        # tokens and the original doc.
        cached_nodes = sentence_analysis(
            sent.as_doc(),
            doc_id,
            sen_id,
            cached_nodes,
        )
        sen_id += 1
    return cached_nodes


def sentence_analysis(
        sent: spacy_doc,
        doc_id: int,
        sent_id: int,
        cached_nodes: dict[str, Entity],
) -> type[dict[str, Entity], dict[str, EntitySet]]:

    chunks = find_chunks(sent)
    phrases = group_tokens_to_phrases(sent, chunks)
    cached_nodes, phrases = generate_entity_graph(phrases, doc_id, sent_id, cached_nodes)
    phrases, cached_nodes = property_setter(phrases, cached_nodes)
    update_rules(phrases, cached_nodes)

    return cached_nodes
