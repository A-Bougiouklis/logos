import spacy
from spacy.tokens import Token as spacy_token
from spacy.tokens.span import Span as spacy_sentence

from web.core.models import Token

nlp = spacy.load("en_core_web_sm")

def document_analysis(document: str):

    document_id = Token.nodes.max_document_id + 1
    sentence_id = Token.nodes.max_sentence_id + 1

    cached_nodes = {}

    doc = nlp(document)
    for sent in doc.sents:
        cached_nodes = sentence_analysis(sent, document_id, sentence_id, cached_nodes)
        sentence_id += 1


def sentence_analysis(
        sent: spacy_sentence, doc_id: int, sent_id: int, cached_nodes: dict[str, Token]
) -> dict[str, Token]:
    cached_nodes = dependence_sentence_graph(sent, doc_id, sent_id, cached_nodes)
    return cached_nodes


def dependence_sentence_graph(
    sent: spacy_sentence, doc_id: int, sent_id: int, cached_nodes: dict[str, Token]
) -> dict[str, Token]:
    """
    It analyse the given sentence by creating or updating the Token and Entity nodes.
    """

    index = 0
    while index < len(sent):
        token = sent[index]

        token_node, cached_nodes = get_token_node(token, cached_nodes)
        head_node, cached_nodes = get_token_node(token.head, cached_nodes)
        token_node.dependency.connect(head_node, {"dependency": str(token.dep_)})

        if next_token := sent[index + 1] if index < len(sent) - 1 else None:
            next_token_node, cached_nodes = get_token_node(next_token, cached_nodes)
            token_node.sentence.connect(
                next_token_node,
                {
                    "document_id": doc_id,
                    "sentence_id": sent_id,
                    "order": index
                }
            )

        index += 1
    return cached_nodes


def get_token_node(
        token: spacy_token, cached_nodes: dict[str, Token]
) -> tuple[Token, dict[str, Token]]:
    """
    It fetches the Token node with the given token name either from the cache or
    the database. It also updates the cache.
    """

    node = cached_nodes.get(token.text)
    if node is None:
        node = Token.get_or_create(token)
        cached_nodes[token.text] = node
    return node, cached_nodes
