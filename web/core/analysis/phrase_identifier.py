from spacy.tokens.doc import Doc as spcay_doc
from spacy.tokens.span import Span as spacy_span
from nltk.corpus import wordnet
from dataclasses import dataclass
from typing import Union

from web.core.models import Entity, EntitySet


@dataclass
class Phrase:

    def __init__(
            self, span: spacy_span, node_type: Union[type(Entity), type(EntitySet)]
    ):
        self.span = span
        self.node_type = node_type


MAX_PHRASE_LENGTH = 4


def group_tokens_to_phrases(
        sent: spcay_doc, noun_chunks: list[spacy_span]
) -> list[Phrase]:
    """
    - Group together all the tokens which create a phrase, like "go away"
    - Add the noun_chunks into the phrase list

    Return: The generated list of phrase objects.
    """

    phrases = []
    token_index = 0

    while token_index < len(sent):

        if __does_token_belong_to_noun_chunk(token_index, noun_chunks):
            token_index += 1
            continue

        # Group together the phrases.
        found_phrase = False
        for window in range(MAX_PHRASE_LENGTH, 0, -1):
            span = sent[token_index : token_index + window]
            if __is_phrase(span.text):
                phrases.append(Phrase(span, Entity))
                token_index = token_index + window
                found_phrase = True
                break

        # The token could be missing from the wordnet.
        if not found_phrase:
            # We extract the token as a sub list to ensure that it is of type spaCy_Span
            # and not spaCy_Token
            phrases.append(Phrase(sent[token_index:token_index+1], Entity))
            token_index +=1

    phrases.extend([Phrase(noun_chunk, EntitySet) for noun_chunk in noun_chunks])
    phrases.sort(key=lambda entity: entity.span.start)
    return phrases


def __does_token_belong_to_noun_chunk(
        token_index: int , noun_chunks: list[spacy_span]
) -> bool:
    for noun_chunk in noun_chunks:
        if noun_chunk.start <= token_index < noun_chunk.end:
            return True
    return False


def __is_phrase(phrase: str) -> bool:
    # The phrases in the wordnet have underscores instead of spaces.
    phrase = phrase.replace(" ", "_")
    return bool(wordnet.synsets(phrase))
