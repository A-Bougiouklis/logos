from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models.entities import db, Entity
from web.core.analysis.nlp_models import nlp


class EntityTests(TestCase):

    # def setUp(self):
    #     clear_neo4j_database(db)

    def test_get_or_create_span(self):
        doc = nlp("The big dog ate some poop")

        noun_chunk = next(doc.noun_chunks)
        Entity.get_or_create(noun_chunk)

        with self.subTest("creates_entity"):
            entity = Entity.nodes.get(text=noun_chunk.text)
            self.assertEqual(noun_chunk.text, entity.text)
            self.assertEqual([noun_chunk.root.pos_], entity.pos)

        with self.subTest("creates_parent_entity"):
            parent = Entity.nodes.get(text=noun_chunk.root.text)
            self.assertEqual(noun_chunk.root.text, parent.text)
            self.assertEqual([noun_chunk.root.pos_], parent.pos)
            self.assertIsNotNone(entity.parent.relationship(parent))

        with self.subTest("gets_entity_if_already_exits"):
            existing_entity = Entity.get_or_create(noun_chunk)
            self.assertEqual(existing_entity, entity)

    def test_get_or_create_token(self):
        doc = nlp("The big dog ate some poop")
        token = doc[1]
        Entity.get_or_create(token)

        with self.subTest("creates_entity"):
            entity = Entity.nodes.get(text=token.text)
            self.assertEqual(token.text, entity.text)
            self.assertEqual([token.pos_], entity.pos)

        with self.subTest("gets_entity_if_already_exits"):
            existing_entity = Entity.get_or_create(token)
            self.assertEqual(existing_entity, entity)

    def test_get_or_create_adds_new_pos_into_existing_entity(self):
        google_verb = nlp("could you google 'greece' for me")[2]
        google_propn = nlp("I work at google")[3]

        google_verb_node = Entity.get_or_create(google_verb)
        self.assertEqual(["VERB"], google_verb_node.pos)

        google_propn_node = Entity.get_or_create(google_propn)
        self.assertEqual(["VERB", "PROPN"], google_propn_node.pos)

    def test_generate_synonyms(self):

        with self.subTest("do_not_generate_synonyms_when_entities_do_not_exist"):
            token = nlp("dog")[0]
            entity = Entity.get_or_create(token)
            entity.generate_synonyms(token)
            self.assertEqual(1, len(Entity.nodes.all()))

        with self.subTest("generate_synonyms_when_corresponding_entities_exist"):
            token = nlp("dog")[0]
            entity = Entity.get_or_create(token)
            synonym_entity = Entity.get_or_create(nlp("domestic dog")[0:])
            entity.generate_synonyms(token)

            self.assertEqual(2, len(Entity.nodes.all()))
            self.assertIsNotNone(entity.synonym.relationship(synonym_entity))

        with self.subTest("generate_synonyms_for_phrases_with_multiple_tokens"):
            span = nlp("Canis familiaris")[0:]
            entity = Entity.get_or_create(span)
            synonym_entity = Entity.get_or_create(nlp("domestic dog")[0:])
            entity.generate_synonyms(span)

            # The forth entitiy is the root of the "Canis familiaris" -> "familiaris"
            self.assertEqual(4, len(Entity.nodes.all()))
            self.assertIsNotNone(entity.synonym.relationship(synonym_entity))


class EntityNodeSetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)
        self.e1 = Entity(text="the").save()
        self.e2 = Entity(text="big").save()
        self.e3 = Entity(text="dog").save()

    def set_sentence_relationships(self):
        self.e1.sentence.connect(self.e2, {"document_id": 0, "sentence_id": 0})
        self.e1.sentence.connect(self.e3, {"document_id": 0, "sentence_id": 1})
        self.e3.sentence.connect(self.e2, {"document_id": 1, "sentence_id": 2})

    def test_max_document_id(self):

        with self.subTest("is_0_with_no_document_id"):
            self.assertEqual(0, Entity.nodes.max_document_id)

        with self.subTest("max_document_id_otherwise"):
            self.set_sentence_relationships()
            self.assertEqual(1, Entity.nodes.max_document_id)

    def test_max_sentence_id(self):
        with self.subTest("is_0_with_no_sentence_id"):
            self.assertEqual(0, Entity.nodes.max_sentence_id)

        with self.subTest("max_sentence_id_otherwise"):
            self.set_sentence_relationships()
            self.assertEqual(2, Entity.nodes.max_sentence_id)
