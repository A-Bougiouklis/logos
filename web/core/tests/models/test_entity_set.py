from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models import db, EntitySet
from web.core.analysis.nlp_models import nlp


class EntitySetTests(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

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
