from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models import db, Entity, Token
from web.core.analysis.nlp_models import nlp


class TokenTests(TestCase):

    def setUp(self):
        # clear_neo4j_database(db)
        ...

    def test_get_or_create(self):
        doc = nlp("The big dog")

        Token.get_or_create(doc[2])

        with self.subTest("creates_token"):
            dog_token = Token.nodes.get(token="dog")
            self.assertEqual("dog", dog_token.token)

        with self.subTest("gets_token_if_already_exits"):
            existing_dog_token = Token.get_or_create(doc[2])
            self.assertEqual(existing_dog_token, dog_token)

        with self.subTest("creates_entity"):
            dog_entity = Entity.nodes.get(lemma="dog")
            self.assertEqual("dog", dog_entity.lemma)
            self.assertEqual(["xxx"], dog_entity.shape)
            self.assertEqual(["NOUN"], dog_entity.pos)

        with self.subTest("relationship_between_token_and_entity"):
            self.assertIsNotNone(dog_token.lemma.relationship(dog_entity))


class TokenNodeSetTests(TestCase):

    def setUp(self):
        # clear_neo4j_database(db)
        self.t1 = Token(token="the").save()
        self.t2 = Token(token="big").save()
        self.t3 = Token(token="dog").save()

    def set_sentence_relationships(self):
        self.t1.sentence.connect(self.t2, {"document_id": 0, "sentence_id": 0})
        self.t1.sentence.connect(self.t3, {"document_id": 0, "sentence_id": 1})
        self.t3.sentence.connect(self.t2, {"document_id": 1, "sentence_id": 2})

    def test_max_document_id(self):

        with self.subTest("is_0_with_no_document_id"):
            self.assertEqual(0, Token.nodes.max_document_id)

        with self.subTest("max_document_id_otherwise"):
            self.set_sentence_relationships()
            self.assertEqual(1, Token.nodes.max_document_id)

    def test_max_sentence_id(self):
        with self.subTest("is_0_with_no_sentence_id"):
            self.assertEqual(0, Token.nodes.max_sentence_id)

        with self.subTest("max_sentence_id_otherwise"):
            self.set_sentence_relationships()
            self.assertEqual(2, Token.nodes.max_sentence_id)
