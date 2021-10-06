import spacy
from web.core.models import Token

nlp = spacy.load("en_core_web_sm")

def document_analysis(document: str):
    # need to walk the entire tree and create Token, Entities and EntitySets

    document_id = Token.nodes.max_document_id + 1
    sentence_id = Token.nodes.max_sentence_id + 1

    doc = nlp(document)
    for sent in doc.sents:
        print(document_id," ", sentence_id)
        print()
        # print(sent.root, sent.root.children)
        for token in sent:
            print(token, token.dep_, token.head)

        sentence_id += 1


import spacy.tokens.token