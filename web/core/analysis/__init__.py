import spacy
from web.core.models import Token

nlp = spacy.load("en_core_web_sm")

def document_analysis(document: str):
    # need to walk the entire tree and create Token, Entities and EntitySets

    document_id = Token.nodes.max_document_id + 1
    sentence_id = Token.nodes.max_sentence_id + 1

    cached_tokens = {}

    doc = nlp(document)
    for sent in doc.sents:
        print(document_id," ", sentence_id)
        print()
        # print(sent.root, sent.root.children)
        for token in sent:

            token_node = cached_tokens.get(token.text)
            if token_node is None:
                token_node = Token.get_or_create({"token": token.text})[0].save()
                cached_tokens[token.text] = token_node

            head_node = cached_tokens.get(token.head)
            if head_node is None:
                head_node = Token.get_or_create({"token": token.head})[0].save()
                cached_tokens[token.head] = head_node

            token_node.dependency.connect(head_node, {"dependency" : token.dep_})
            print(token_node, head_node)
            print(token, token.dep_, token.head)

        sentence_id += 1

import spacy.tokens.token