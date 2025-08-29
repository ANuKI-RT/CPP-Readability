from typing import List, Dict, Any, Set

from nltk.stem import PorterStemmer

from code_processing import filter_manager
from code_processing.analyzer import CodeAnalyzer
from code_processing.lexer import Lexer


class FeatureCalculator:
    code: str
    language: str
    parameters: Dict[str, Any]
    feature_calculators: List["FeatureCalculator"]

    def __init__(self, code: str, lexer: Lexer = None, tab_size=4):
        self.code = code.replace('\t', ''.join([' ' for _ in range(tab_size)]))
        self.lexer = lexer
        self.tab_size = tab_size
        self._tokens = []

    @property
    def name(self):
        raise NotImplemented()

    @property
    def lines(self):
        if self.code is None:
            return []
        return self.code.splitlines(keepends=True)

    @property
    def tokens(self):
        assert self.lexer is not None, "Cannot tokenize without a lexer"
        if len(self._tokens) == 0:
            self._tokens = self.lexer.lexing(self.code)
        return self._tokens

    def calculate_metric(self) -> float:
        raise NotImplemented()


class TextualFC(FeatureCalculator):
    """
    Textual features proposed by S. Scalabrino et al.
    https://sscalabrino.github.io/files/2018/JSEP2018AComprehensiveModel.pdf
    """

    def __init__(self, analyzer: CodeAnalyzer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analyzer = analyzer

    @property
    def analyzer(self):
        return self._analyzer

    def extract_comment_terms(self, code: str) -> Set[str]:
        """
        Extract comment terms from comments in source code. 4 pre-processing steps in the paper is applied.
        :param code: source code without blank line
        :return: a set of terms
        """
        comments = self._analyzer.get_comments(code)

        # Apply the first 3 steps
        terms = self._extract_terms(comments.replace('\n', ' '))

        # Apply the last step
        return self.convert_to_stems(terms)

    def extract_identifier_terms(self, code: str) -> Set[str]:
        """
        Extract identifier terms from source code. Only the first 3 pre-processing steps in the paper is applied.
        :param code: source code without blank line
        :return: a set of terms
        """
        source_code = self._analyzer.delete_comments(code)

        # Apply the first 3 steps
        return self._extract_terms(source_code)

    def extract_lines_identifier_terms(self, code: str) -> List[Set[str]]:
        """
        Extract identifier terms for each line of code. Only the first 3 pre-processing steps in the paper is applied.
        :param code: source code
        :return: a list of sets of terms that contains terms of every line
        """
        source_code = filter_manager.delete_blank_lines(code)
        source_code = self._analyzer.delete_comments(source_code)
        lines = [line for line in source_code.splitlines() if line.strip() != '']

        # Apply the first 3 steps
        return [self._extract_terms(line) for line in lines]

    def _extract_terms(self, text: str) -> Set[str]:
        """
        Apply the first 3 steps of 4 preprocessing steps as mentioned in the paper.

        *Note*: Original Java implementation did not filter out stop words but ours did.
        :param text: the source code or comment text without blank line
        :return: a set of terms without converting to stems extracted from the input text
        """

        # Remove non-textual tokens from the corpora, e.g., operators, special symbols,
        # and programming language keywords
        split_words = self._analyzer.get_identifiers_from_source(text)

        # Split the remaining tokens into separate words by using the underscore or camel case separators
        # e.g., getText is split into get and text
        terms = [t.strip().lower() for w in split_words for t in CodeAnalyzer.get_identifier_words(w) if t != '']

        # Remove words belonging to a stop-word list (e.g., articles, adverbs)
        return set(filter_manager.apply_stop_words_filter(terms))

    @staticmethod
    def convert_to_stems(terms: Set[str]) -> Set[str]:
        """
        Apply the last preprocessing step as mentioned in the paper that convert term to stem.

        *Note*: Original Java implementation used RiTa wordnet library to extract stem, while ours used Porter algorithm
        :param terms: a set of terms without converting to stems
        :return: a set of stems
        """

        # Extract stems from terms by using the Porter algorithm
        return {PorterStemmer().stem(t) for t in terms}
