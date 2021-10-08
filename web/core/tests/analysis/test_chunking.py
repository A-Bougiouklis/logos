from django.test import TestCase

from web.core.analysis.nlp_models import nlp
from web.core.analysis.chunking import find_chunks, generate_entity_sets
from web.core.models import EntitySet


class FindChunksTests(TestCase):

    def test_find_chunks(self):

        samples = [
            ["the dog ate some poop", [["the dog"], ["ate"], ["some poop"]]],
            ["the big dog ate some poop", [["the big dog"], ["ate"], ["some poop"]]],
            ["the wall was painted by bob", [["the wall"], ["was painted"], ["by bob"]]],
            ["we have eaten some bromiko", [["we"], ["have eaten"], ["some bromiko"]]],
            ["the masked language model randomly masks some of the tokens", [["the masked language model"], ["randomly masks"], ["some of the tokens"]]],
        ]

        for original, expected_chunks in samples:
            with self.subTest(f"chunking: {original}"):
                chunks = find_chunks(nlp(original))[0]
                noun_chunk = chunks[0].text
                verb_chunk = chunks[1].text
                adjective_chunk = chunks[2].text
                self.assertEqual(
                    [[noun_chunk], [verb_chunk], [adjective_chunk]],
                    expected_chunks
                )


class GenerateEntitySetsTests(TestCase):

    def test_generate_entity_sets(self):
        samples = [
            ["the dog ate some poop", ["the dog", "ate", "some poop"]],
            ["the big dog ate some poop", ["the big dog", "ate", "some poop"]],
            ["the wall was painted by bob", ["the wall", "was_painted", "by bob"]],
            ["we have eaten some bromiko", ["we", "have_eaten", "some bromiko"]],
            ["the masked language model randomly masks some of the tokens", ["the masked language model", "randomly_masks","some of the tokens"]],
        ]

        for original, expected_chunks in samples:
            with self.subTest(f"generate entity sets for: {original}"):
                noun_chunk, verb_chunk, adjective_chunk = expected_chunks
                chunks = find_chunks(nlp(original))
                generate_entity_sets(chunks)

                with self.subTest("created_the_entity_set"):
                    entity_set = EntitySet.nodes.get(name=noun_chunk)
                    self.assertIsNotNone(entity_set)

                with self.subTest("creates_the_property"):
                    self.assertTrue(hasattr(entity_set, verb_chunk))
                    self.assertEqual([adjective_chunk], getattr(entity_set, verb_chunk))
