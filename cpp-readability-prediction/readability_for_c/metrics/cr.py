from typing import Dict, Tuple

import text_processing
from code_processing import filter_manager
from code_processing.analyzer import CodeAnalyzer
from metrics.feature_calculator import FeatureCalculator


def get_all_feature_calculators(code: str, analyzer: CodeAnalyzer) -> Dict[str, FeatureCalculator]:
    fc = CommentsReadabilityFC(code=code, analyzer=analyzer)
    return {fc.name(): fc}


class CommentsReadabilityFC(FeatureCalculator):
    def __init__(self, analyzer: CodeAnalyzer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analyzer = analyzer

    def name(self):
        return "Comments Readability"

    def calculate_metric(self) -> float:
        source_code = filter_manager.delete_blank_lines(self.code)
        comment = self._analyzer.get_comments(source_code)
        syllables, words, sentences = self._extract_nl_features(comment)
        if words != 0 and sentences != 0:
            result = (206.835 -
                      1.015 * (words // sentences) -
                      84.600 * (syllables // words))
            return result
        return 0.

    @staticmethod
    def _extract_nl_features(text: str) -> Tuple[int, int, int]:
        sentences, words = text_processing.split_sentences_and_words(text)
        syllables = 0
        for word in words:
            count = text_processing.count_syllables(word)
            syllables += count
        return syllables, len(words), len(sentences)
