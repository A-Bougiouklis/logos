from django.test import TestCase

from web.core.analysis.nlp_models import nlp
from web.core.analysis.chunking import find_chunks


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
