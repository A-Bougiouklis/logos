from web.core.models import Token
from spacy.tokens.doc import Doc as spacy_doc

from web.core.analysis.chunking import chunking
from web.core.analysis.token_graph import dependence_sentence_graph
from web.core.analysis.nlp_models import nlp


def document_analysis(document: str):

    doc_id = Token.nodes.max_document_id + 1
    sen_id = Token.nodes.max_sentence_id + 1

    cached_nodes = {}

    doc = nlp(document)
    for sent in doc.sents:
        # We convert the sentence to a doc to remove any index connection between the
        # tokens and the original doc
        cached_nodes = sentence_analysis(sent.as_doc(), doc_id, sen_id, cached_nodes)
        sen_id += 1


def sentence_analysis(
        sent: spacy_doc, doc_id: int, sent_id: int, cached_nodes: dict[str, Token]
) -> dict[str, Token]:
    cached_nodes = dependence_sentence_graph(sent, doc_id, sent_id, cached_nodes)
    chunking(sent)
    return cached_nodes
