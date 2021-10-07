import spacy

from web.core.models import Token
from .sentence_to_nodes import sentence_analysis

nlp = spacy.load("en_core_web_sm")

def document_analysis(document: str):

    document_id = Token.nodes.max_document_id + 1
    sentence_id = Token.nodes.max_sentence_id + 1

    cached_nodes = {}
    print()
    doc = nlp(document)
    for sent in doc.sents:
        cached_nodes = sentence_analysis(sent, document_id, sentence_id, cached_nodes)
        sentence_id += 1
