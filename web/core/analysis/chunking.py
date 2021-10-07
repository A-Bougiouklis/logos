from spacy.tokens.span import Span
import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans


def chunking(sent: Span) -> list[list[Span, Span, Span]]:
    chunks = []
    verb_chunks = __verb_chunks(sent)

    # pairs the correct noun and verb chunks together
    for noun_chunk in __noun_chunks(sent):
        for verb_index, verb_chunk in enumerate(verb_chunks):
            if noun_chunk.root.head in verb_chunk:
                adjective_chunk = adjective_chunks(sent, verb_chunk, noun_chunk)
                chunks.append([noun_chunk, verb_chunk, " ".join(adjective_chunk)])
                verb_chunks.pop(verb_index)
                break

    print(chunks, "\n")
    return chunks


def __noun_chunks(sent: Span) -> list[Span]:
    spans = []
    for chunk in sent.noun_chunks:
        if chunk.root.dep_ in ["nsubj", "nsubjpass"]:
            spans.append(chunk)
    return spans


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


def __verb_chunks(sent: Span) -> list[Span]:
    spans = [sent[start:end] for _, start, end in verb_phrase_matcher(sent)]
    return filter_spans(spans)


def adjective_chunks(sent: Span, verb_chunk: Span, noun_chunk: Span):
    nodes = []
    for t in sent:
        if t.head in verb_chunk and t.dep_ in ["xcomp", "acomp", "dobj"] and not t in noun_chunk and not t in verb_chunk:
            nodes.extend(walk(t, nodes))

    # This could bring tokens which are mentioned before the verb phrase.
    return [t.text for t in sent if t in nodes]


def walk(root, nodes):
    nodes.append(root)
    for child in root.children:
        nodes.append(child)
        nodes = walk(child, nodes)
    return nodes