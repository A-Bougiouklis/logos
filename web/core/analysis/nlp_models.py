import spacy
from spacy.matcher import Matcher


nlp = spacy.load('en_core_web_sm')


VERB_PATTERNS = [
    [
        {'POS': 'VERB', 'OP': '?'},
        {'POS': 'ADV', 'OP': '*'},
        {'POS': 'AUX', 'OP': '*'},
        {'POS': 'VERB', 'OP': '+'},
    ],
    [
        {'POS': 'AUX', 'OP': '*'}
    ],
]
verb_phrase_matcher = Matcher(nlp.vocab)
verb_phrase_matcher.add("Verb phrase", VERB_PATTERNS)