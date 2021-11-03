from spacy.tokens.doc import Doc as spacy_doc

from web.core.models import Entity, EntitySet
from .chunking import find_chunks
from .entity_graph import generate_entity_graph
from .phrase_identifier import group_tokens_to_phrases
from .property_setter import property_setter
from web.core.analysis.nlp_models import nlp


def document_analysis(document: str):

    doc_id = Entity.nodes.max_document_id + 1
    sen_id = Entity.nodes.max_sentence_id + 1

    cached_entity_nodes = {}

    doc = nlp(document)
    for sent in doc.sents:
        # We convert the sentence to a doc to remove any index connection between the
        # tokens and the original doc.
        cached_entity_nodes, cached_entity_set_nodes = sentence_analysis(
            sent.as_doc(),
            doc_id,
            sen_id,
            cached_entity_nodes,
        )
        sen_id += 1


def sentence_analysis(
        sent: spacy_doc,
        doc_id: int,
        sent_id: int,
        cached_entity_nodes: dict[str, Entity],
) -> type[dict[str, Entity], dict[str, EntitySet]]:

    phrases = group_tokens_to_phrases(sent, find_chunks(sent))
    cached_entity_nodes, phrases = generate_entity_graph(
        phrases, doc_id, sent_id, cached_entity_nodes
    )
    phrases, cached_entity_nodes = property_setter(phrases, cached_entity_nodes)


    return cached_entity_nodes
