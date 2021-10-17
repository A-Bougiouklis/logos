from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models import db, Entity
from web.core.analysis.nlp_models import nlp


class EntityTests(TestCase):

    def setUp(self):
        # clear_neo4j_database(db)
        ...

    def test_get_or_create(self):
        doc = nlp("The big dog")

        Entity.get_or_create(doc[2])

        with self.subTest("creates_entity"):
            dog_entity = Entity.nodes.get(lemma="dog")
            self.assertEqual("dog", dog_entity.lemma)
            self.assertEqual(["NOUN"], dog_entity.pos)
            self.assertEqual(["xxx"], dog_entity.shape)

        with self.subTest("gets_token_if_already_exits"):
            existing_dog_entity = Entity.get_or_create(doc[2])
            self.assertEqual(existing_dog_entity, dog_entity)

        with self.subTest("add_new_pos_into_existing_entity"):
            google_verb = nlp("could you google 'greece' for me")[2]
            google_propn = nlp("I work at google")[3]

            google_verb_node = Entity.get_or_create(google_verb)
            self.assertEqual(["VERB"], google_verb_node.pos)

            google_propn_node = Entity.get_or_create(google_propn)
            self.assertEqual(["VERB", "PROPN"], google_propn_node.pos)
