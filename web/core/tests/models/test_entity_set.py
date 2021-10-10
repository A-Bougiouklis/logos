from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models import db, EntitySet, Token
from web.core.analysis.nlp_models import nlp


class EntitySetTests(TestCase):

    # def setUp(self):
    #     clear_neo4j_database(db)

    def test_get_or_create_for_token(self):
        doc = nlp("The big dog")

        EntitySet.get_or_create(doc[2])

        with self.subTest("creates_entity_set"):
            dog_entity_set = EntitySet.nodes.get(name="dog")
            self.assertEqual("dog", dog_entity_set.name)

        with self.subTest("creates_token"):
            dog_token = Token.nodes.get(token="dog")
            self.assertEqual("dog", dog_token.token)

        with self.subTest("relationship_between_token_and_entity_set"):
            r = dog_entity_set.token.relationship(dog_token)
            self.assertEqual(0, r.order)

    def test_get_or_create_for_noun_chunk(self):
        doc = nlp("The big dog ate the poop.")

        EntitySet.get_or_create(doc[0:3])

        with self.subTest("creates_entity_set"):
            dog_entity_set = EntitySet.nodes.get(name="The big dog")
            self.assertEqual("The big dog", dog_entity_set.name)

        with self.subTest("gets_entity_set_if_already_exits"):
            existing_dog_entity_set = EntitySet.get_or_create(doc[0:3])
            self.assertEqual(existing_dog_entity_set, dog_entity_set)

        with self.subTest("creates_root_entity_set"):
            root_entity_set = EntitySet.nodes.get(name="dog")
            self.assertEqual("dog", root_entity_set.name)

        with self.subTest("creates_tokens"):
            the_token = Token.nodes.get(token="The")
            big_token = Token.nodes.get(token="big")
            dog_token = Token.nodes.get(token="dog")
            self.assertEqual("The", the_token.token)
            self.assertEqual("big", big_token.token)
            self.assertEqual("dog", dog_token.token)

        with self.subTest("relationship_between_tokens_and_entity_set"):
            r0 = dog_entity_set.token.relationship(the_token)
            self.assertEqual(0, r0.order)
            r1 = dog_entity_set.token.relationship(big_token)
            self.assertEqual(1, r1.order)
            r2 = dog_entity_set.token.relationship(dog_token)
            self.assertEqual(2, r2.order)

    def test_set_property(self):
        doc = nlp("The big dog")

        dog_entity_set = EntitySet.get_or_create(doc[2])

        with self.subTest("create_new_properties"):
            dog_entity_set.set_property("ate", "some poop")
            self.assertEqual(["some poop"], dog_entity_set.ate)

        with self.subTest("does_not_duplicate_properties"):
            dog_entity_set.set_property("ate", "some poop")
            self.assertEqual(["some poop"], dog_entity_set.ate)

        with self.subTest("adds_new_values_in_existing_properties"):
            dog_entity_set.set_property("ate", "some cat food")
            self.assertCountEqual(["some poop", "some cat food"], dog_entity_set.ate)
