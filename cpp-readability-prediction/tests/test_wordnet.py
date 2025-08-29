import unittest

import wordnet


class TestWordnet(unittest.TestCase):
    def test_get_best_pos(self):
        pos, normalized_word = wordnet.get_best_pos('_must_')
        self.assertEqual('n', pos)
        self.assertEqual('must', normalized_word)
