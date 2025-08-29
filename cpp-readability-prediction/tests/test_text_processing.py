import unittest

import text_processing


class TestText(unittest.TestCase):
    def test_split_sentences_and_words(self):
        sentences, words = text_processing.split_sentences_and_words(
            ' It is a test\nby split [aeiou].a test for:aA*b_b != Cc. **. +-*/')

        self.assertEqual(
            ['It is a test', 'by split [aeiou]', 'a test for', 'aA*b_b', '= Cc'],
            sentences
        )
        self.assertEqual(
            ['It', 'is', 'a', 'test', 'by', 'split', 'aeiou', 'a', 'test', 'for', 'aA', 'b', 'b', 'Cc'],
            words
        )

    def test_count_syllables(self):
        self.assertEqual(1, text_processing.count_syllables('I'))
        self.assertEqual(3, text_processing.count_syllables('computing'))
        self.assertEqual(3, text_processing.count_syllables('decided'))
        self.assertEqual(3, text_processing.count_syllables('syllable'))
        self.assertEqual(3, text_processing.count_syllables('syllables'))
        self.assertEqual(1, text_processing.count_syllables('stair'))
        self.assertEqual(2, text_processing.count_syllables('cacao'))
        self.assertEqual(3, text_processing.count_syllables('authentic'))
        self.assertEqual(2, text_processing.count_syllables('Bayern'))
        self.assertEqual(2, text_processing.count_syllables('appeal'))
        self.assertEqual(1, text_processing.count_syllables('Sneeze'))
        self.assertEqual(2, text_processing.count_syllables('neither'))
        self.assertEqual(2, text_processing.count_syllables('theory'))
        self.assertEqual(2, text_processing.count_syllables('neutral'))
        self.assertEqual(1, text_processing.count_syllables('they'))
        self.assertEqual(1, text_processing.count_syllables('piece'))
        self.assertEqual(2, text_processing.count_syllables('quiet'))
        self.assertEqual(2, text_processing.count_syllables('union'))
        self.assertEqual(3, text_processing.count_syllables('aquarium'))
        self.assertEqual(2, text_processing.count_syllables('oasis'))
        self.assertEqual(2, text_processing.count_syllables('poetry'))
        self.assertEqual(2, text_processing.count_syllables('toilet'))
        self.assertEqual(1, text_processing.count_syllables('spoon'))
        self.assertEqual(2, text_processing.count_syllables('thousand'))
        self.assertEqual(1, text_processing.count_syllables('boy'))
        self.assertEqual(2, text_processing.count_syllables('royal'))
        self.assertEqual(2, text_processing.count_syllables('equal'))
        self.assertEqual(2, text_processing.count_syllables('guava'))
        self.assertEqual(3, text_processing.count_syllables('sanctuary'))
        self.assertEqual(1, text_processing.count_syllables('build'))
        self.assertEqual(1, text_processing.count_syllables('duo'))
        self.assertEqual(1, text_processing.count_syllables('guy'))
        self.assertEqual(2, text_processing.count_syllables('buyer'))
        self.assertEqual(3, text_processing.count_syllables('loyalty'))
        self.assertEqual(1, text_processing.count_syllables('yearn'))
        self.assertEqual(2, text_processing.count_syllables('lawyer'))
        self.assertEqual(1, text_processing.count_syllables('youth'))
        self.assertEqual(1, text_processing.count_syllables('you'))
        self.assertEqual(2, text_processing.count_syllables('wagyu'))

        self.assertEqual(3, text_processing.count_syllables('aeiou'))
        self.assertEqual(1, text_processing.count_syllables('the'))
        self.assertEqual(3, text_processing.count_syllables('expected'))
        self.assertEqual(2, text_processing.count_syllables('because'))
        self.assertEqual(1, text_processing.count_syllables('phrases'))
        self.assertEqual(1, text_processing.count_syllables('ssss'))
