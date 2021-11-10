from django.test import TestCase

from web.core.analysis.nlp_models import nlp
from web.core.models import Entity, EntitySet
from web.core.analysis.phrase_identifier import group_tokens_to_phrases
from web.core.analysis.chunking import find_chunks


class GroupTokensToPhrasesTests(TestCase):

    def test_without_noun_chunks(self):

        doc = nlp("the dog ate some poop")
        phrases = group_tokens_to_phrases(doc, [])

        with self.subTest("the_text_has_the_correct_order"):
            text = " ".join([phrase.span.text for phrase in phrases])
            self.assertEqual(doc.text, text)

        with self.subTest("every_phrase_is_of_type_Entity"):
            self.assertTrue(all([phrase.node_type == Entity for phrase in phrases]))

    def test_with_one_noun_chunk(self):

        doc = nlp("the dog ate some poop")
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))

        with self.subTest("the_text_has_the_correct_order"):
            text = " ".join([phrase.span.text for phrase in phrases])
            self.assertEqual(doc.text, text)

        with self.subTest("the_first_phrase_is_an_entity_set_and_the_rest_entities"):
            self.assertEqual(phrases[0].node_type, EntitySet)
            self.assertTrue(all([phrase.node_type == Entity for phrase in phrases[1:]]))


    def test_with_many_noun_chunks(self):

        doc = nlp(
            "The dog ate some poop , the human had to scoop the poop , the trash "
            "collector had to collect the poop"
        )
        phrases = group_tokens_to_phrases(doc, find_chunks(doc))

        with self.subTest("the_text_has_the_correct_order"):
            text = " ".join([phrase.span.text for phrase in phrases])
            self.assertEqual(doc.text, text)

        with self.subTest("three_phrases_are_entity_nodes_the_rest_are_entities"):
            self.assertEqual(phrases[0].node_type, EntitySet)
            self.assertEqual(phrases[5].node_type, EntitySet)
            self.assertEqual(phrases[12].node_type, EntitySet)

            self.assertTrue(
                all(
                    [
                        phrase.node_type == Entity
                        for i, phrase in enumerate(phrases)
                        if i not in [0,5,12]
                    ]
                )
            )

    def test_groups_together_phrases(self):
        doc = nlp("You should get out of here")
        phrases = group_tokens_to_phrases(doc, [])

        with self.subTest("the_text_has_the_correct_order"):
            text = " ".join([phrase.span.text for phrase in phrases])
            self.assertEqual(doc.text, text)

        with self.subTest("every_phrase_is_of_type_Entity"):
            self.assertTrue(all([phrase.node_type == Entity for phrase in phrases]))

        with self.subTest("the_tokens_get_and_out_are_grouped_in_one_phrase"):
            self.assertEqual(phrases[2].span.text, "get out")
