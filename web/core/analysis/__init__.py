import spacy


nlp = spacy.load("en_core_web_sm")

def document_analysis(document: str):
    doc = nlp(document)
    for sent in doc.sents:
        for token in sent:
            print(token.text, token.pos_, token.shape_)
