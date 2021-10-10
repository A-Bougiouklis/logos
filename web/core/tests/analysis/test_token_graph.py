from django.test import TestCase

from web.core.analysis.nlp_models import nlp
from web.core.analysis.token_graph import dependency_sentence_graph
from neomodel import clear_neo4j_database
from web.core.models import db, Token
from spacy.tokens.doc import Doc as spcay_doc


class DependencySentenceGraphTests(TestCase):

    # def setUp(self):
    #     clear_neo4j_database(db)

    def dependence_sentence_graph_asserts(
            self, doc: spcay_doc, doc_id: int, sent_id: int
    ):
        for index, token in enumerate(doc):

            token_node = Token.nodes.get(token=token.text)
            with self.subTest(f"creates token -> {token}"):
                self.assertEqual(token.text, token_node.token)

            with self.subTest(f"dependency -> {token} - [{token.dep_}] - {token.head}"):
                head_node = Token.nodes.get(token=token.head.text)
                r = token_node.dependency.relationship(head_node)
                if token.dep_ == "ROOT":
                    self.assertIsNone(r)
                else:
                    self.assertEqual(token.dep_, r.dependency)

            try:
                with self.subTest(f"sentence -> {token}-[order:{index}]-{doc[index+1]}"):
                    next_node = Token.nodes.get(token=doc[index+1].text)
                    r = token_node.sentence.relationship(next_node)
                    self.assertEqual(doc_id, r.document_id)
                    self.assertEqual(sent_id, r.sentence_id)
                    self.assertEqual(index, r.order)
            except IndexError:
                pass

    def test_dependency_sentence_graph_without_cache(self):

        doc = nlp("we have eaten some bromiko")
        dependency_sentence_graph(doc, 1, 2, {})

        self.dependence_sentence_graph_asserts(doc, 1, 2)

    def test_dependency_sentence_graph_cache(self):

        doc = nlp("the big dog ate a huge turd")
        cached_nodes = {}
        for token in doc:
            cached_nodes[token.text]= Token.get_or_create(token)

        dependency_sentence_graph(doc, 2, 3, cached_nodes)
        self.dependence_sentence_graph_asserts(doc, 2, 3)
