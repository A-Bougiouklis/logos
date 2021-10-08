from spacy.tokens.span import Span
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from spacy.util import filter_spans
from typing import Optional

from web.core.models import EntitySet
from web.core.analysis.nlp_models import verb_phrase_matcher


def chunking(sent: Doc) -> list[list[Span, Span, Span]]:
    chunks = find_chunks(sent)
    generate_entity_sets(chunks)
    return chunks


def find_chunks(sent: Doc) -> list[list[Span, Span, Span]]:
    chunks = []
    verb_chunks = __verb_chunks(sent)

    # pairs the correct noun, verb chunks and adjective_chunk together
    for noun_chunk in __noun_chunks(sent):
        for verb_index, verb_chunk in enumerate(verb_chunks):
            if noun_chunk.root.head in verb_chunk:
                adjective_chunk = __adjective_chunks(sent, verb_chunk, noun_chunk)
                if adjective_chunk:
                    chunks.append([noun_chunk, verb_chunk, adjective_chunk])
                verb_chunks.pop(verb_index)
                break

    return chunks


def __noun_chunks(sent: Doc) -> list[Span]:
    spans = []
    for chunk in sent.noun_chunks:
        if chunk.root.dep_ in ["nsubj", "nsubjpass"]:
            spans.append(chunk)
    return spans


def __verb_chunks(sent: Doc) -> list[Span]:
    spans = [sent[start:end] for _, start, end in verb_phrase_matcher(sent)]
    return filter_spans(spans)


def __adjective_chunks(sent: Doc, verb_chunk: Span, noun_chunk: Span) -> Optional[Span]:

    begin, end = None, None
    for token in sent:
        if ___is_adjective(token, verb_chunk, noun_chunk):
            if begin is None or token.left_edge.i < begin:
                begin = token.left_edge.i
            if end is None or token.right_edge.i > end:
                end = token.right_edge.i
    if begin is not None and end is not None:
        return sent[begin:end]


def ___is_adjective(token: Token, verb_chunk: Span, noun_chunk: Span) -> bool:
    """
    Checks whether the given token is part of the adjective chunk

    spaCy glossary https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
    """
    return (
            token.head in verb_chunk and
            token.dep_ in ["xcomp", "acomp", "dobj"] and
            not token in noun_chunk and
            not token in verb_chunk
    )


def generate_entity_sets(chunks: list[list[Span, Span, Span]]):
    for noun_chunk, verb_chunk, adjective_chunk in chunks:
        entity_set = EntitySet.get_or_create(noun_chunk)
        entity_set.set_property(verb_chunk.text.replace(" ", "_"), adjective_chunk.text)
        entity_set.save()
