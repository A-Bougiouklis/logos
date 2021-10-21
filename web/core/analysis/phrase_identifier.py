from spacy.tokens.doc import Doc as spcay_doc
from spacy.tokens.span import Span as spacy_span
from nltk.corpus import wordnet
from dataclasses import dataclass
from typing import Union

from web.core.models import Entity, EntitySet


class EntitiesDoNotHaveAssignedChunks(Exception):
    """
    Raised when somebody attempts to access the verb or adjective chunk of a Phrase
    object with node_type = Entity.
    """
    ...


@dataclass
class Phrase:

    def __init__(
            self,
            span: spacy_span,
            node_type: Union[type(Entity), type(EntitySet)],
            verb_chunk: spacy_span = None,
            adjective_chunks: spacy_span = None
    ):
        self.span = span
        self.node_type = node_type
        self.__verb_span = verb_chunk
        self.__adjective_chunks = adjective_chunks

    @property
    def verb_chunk(self):
        if self.node_type == EntitySet:
            return self.__verb_span
        else:
            raise EntitiesDoNotHaveAssignedChunks

    @property
    def adjective_chunks(self):
        if self.node_type == EntitySet:
            return self.__adjective_chunks
        else:
            raise EntitiesDoNotHaveAssignedChunks


def group_tokens_to_phrases(
        sent: spcay_doc, chunks: list[list[spacy_span, spacy_span, spacy_span]]
) -> list[Phrase]:
    """
    - Group together all the tokens which create a phrase, like "go away"
    - Add the noun_chunks into the phrase list

    Return: The generated list of phrase objects.
    """

    phrases = []
    token_index = 0
    noun_chunks = [chunk[0] for chunk in chunks]

    while token_index < len(sent):

        if __does_token_belong_to_noun_chunk(token_index, noun_chunks):
            token_index += 1
            continue

        next_phrase, token_index = __find_next_phrase(sent, token_index)
        phrases.append(next_phrase)

    phrases.extend(__chunks_to_phrases(chunks))
    phrases.sort(key=lambda entity: entity.span.start)
    return phrases


def __does_token_belong_to_noun_chunk(
        token_index: int , noun_chunks: list[spacy_span]
) -> bool:
    for noun_chunk in noun_chunks:
        if noun_chunk.start <= token_index < noun_chunk.end:
            return True
    return False


MAX_PHRASE_LENGTH = 4


def __find_next_phrase(sent: spcay_doc, token_index: int) -> tuple[Phrase, int]:

    for window in range(MAX_PHRASE_LENGTH, 0, -1):
        span = sent[token_index: token_index + window]
        if __is_phrase(span.text):
            return  Phrase(span, Entity), token_index + window

    # If we end up here the token is missing from the wordnet.
    # We extract the token as a sub list to ensure that it is of type spaCy_Span
    # and not spaCy_Token.
    return Phrase(sent[token_index:token_index + 1], Entity), token_index + 1


def __is_phrase(phrase: str) -> bool:
    # The phrases in the wordnet have underscores instead of spaces.
    phrase = phrase.replace(" ", "_")
    return bool(wordnet.synsets(phrase))


def __chunks_to_phrases(
        chunks: list[list[spacy_span, spacy_span, spacy_span]]
) -> list[Phrase]:

    return [
            Phrase(noun_chunk, EntitySet, verb_chunk, adjective_chunks)
            for noun_chunk, verb_chunk, adjective_chunks in chunks
    ]