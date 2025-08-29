from typing import Dict, List, Set

import wordnet
from code_processing.analyzer import CodeAnalyzer
from metrics.feature_calculator import FeatureCalculator, TextualFC


def get_all_feature_calculators(code: str, analyzer: CodeAnalyzer) -> Dict[str, FeatureCalculator]:
    fc = ItidNmNmiFc(
        metric=list(ItidNmNmiFc.METRICS.keys())[0],
        aggregation=list(ItidNmNmiFc.METRICS.values())[0][0],
        analyzer=analyzer,
        code=code,
    )
    fc_list = [ProxyItidNmNmiFc(
        metric=metric,
        aggregation=agg,
        ignore_one_letter_word=ignore_one_letter_word,
        fc=fc,
        code=code,
    ) for ignore_one_letter_word in [False, True]
        for metric, aggregations in ItidNmNmiFc.METRICS.items()
        for agg in aggregations]
    return {fc.name: fc for fc in fc_list}


class ItidNmNmiFc(TextualFC):
    """
    ITID: Identifier Terms in Dictionary computes the aggregation of the proportion of identifiers
    that are english words for each line.

    NM: Number of Meanings computes the aggregation of the sum of the numbers of senses of terms for each line.

    NMI: Narrow Meaning Identifiers computes the aggregation of the sum of the distance of each term
    to root node in WordNet hypernym tree for each line.

    Difference from original Java implementation:

    - Aggregation over lines of code instead of terms.
    - Applying the first 3 pre-processing steps for extracting identifier terms. The last step is not necessary.
    - Use Porter algorithm to get stems instead of wordnet as implemented in original Java implementation.
    - Access WordNet using nltk instead of RiTa library.
    """
    _METRIC_TYPE_IDENTIFIERS = 'Identifier Terms in Dictionary'
    _METRIC_TYPE_NUMBER_OF_SENSES = 'Number of Meanings'
    _METRIC_TYPE_ABSTRACTNESS = 'Narrow Meaning Identifiers'

    METRICS = {
        _METRIC_TYPE_IDENTIFIERS: ['MIN', 'AVG'],
        _METRIC_TYPE_NUMBER_OF_SENSES: ['AVG', 'MAX'],
        _METRIC_TYPE_ABSTRACTNESS: ['MIN', 'AVG', 'MAX'],
    }

    AGG_FUNCS = {
        'MIN': min,
        'AVG': lambda vals: sum(vals) / len(vals) if len(vals) > 0 else 0.,
        'MAX': max,
    }

    def __init__(self, metric: str, aggregation: str, ignore_one_letter_word=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert metric in self.METRICS and aggregation in self.METRICS.get(metric, []) and aggregation in self.AGG_FUNCS
        self.metric = metric
        self.aggregation = aggregation
        self._ignore_one_letter_word = ignore_one_letter_word
        self._lines_identifiers = []
        self._source_code = kwargs.get('code', None)

    @property
    def source_code(self):
        return self._source_code

    @source_code.setter
    def source_code(self, value):
        self._source_code = value
        self._lines_identifiers = self.extract_lines_identifier_terms(self._source_code)

    @property
    def ignore_one_letter_word(self):
        return self._ignore_one_letter_word

    @ignore_one_letter_word.setter
    def ignore_one_letter_word(self, value):
        if self._ignore_one_letter_word != value:
            self._lines_identifiers = []
        self._ignore_one_letter_word = value

    @property
    def name(self):
        return f'{self.metric} {self.aggregation}{" (Ignore 1-letter word)" if self.ignore_one_letter_word else ""}'

    def extract_lines_identifier_terms(self, code: str) -> List[Set[str]]:
        lines_identifiers = super().extract_lines_identifier_terms(code)
        if self.ignore_one_letter_word:
            lines_identifiers = [[t for t in terms if len(t) > 1] for terms in lines_identifiers]
        return lines_identifiers

    def calculate_metric(self) -> float:
        if len(self._lines_identifiers) == 0:
            self._lines_identifiers = self.extract_lines_identifier_terms(self.source_code)
        values = []
        for terms in self._lines_identifiers:
            if len(terms) == 0:
                continue
            value = 0
            for term in terms:
                try:
                    int(term)
                    continue
                except ValueError:
                    pass
                word = term.lower()
                pos_result = wordnet.get_best_pos(word)
                if pos_result is None:
                    continue
                pos, word = pos_result
                if self._METRIC_TYPE_IDENTIFIERS == self.metric:
                    value += 1
                elif self._METRIC_TYPE_ABSTRACTNESS == self.metric:
                    value += wordnet.get_distance_to_root_hypernym(word, pos)
                elif self._METRIC_TYPE_NUMBER_OF_SENSES == self.metric:
                    value += wordnet.get_number_of_meanings(word, pos)

            if self._METRIC_TYPE_IDENTIFIERS == self.metric:
                value /= len(terms)

            values.append(float(value))
        return self.AGG_FUNCS[self.aggregation](values)


class ProxyItidNmNmiFc(FeatureCalculator):
    def __init__(self, metric: str, aggregation: str, fc: ItidNmNmiFc, ignore_one_letter_word=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric = metric
        self.aggregation = aggregation
        self.ignore_one_letter_word = ignore_one_letter_word
        self.fc = fc

    @property
    def name(self):
        return f'{self.metric} {self.aggregation}{" (Ignore 1-letter word)" if self.ignore_one_letter_word else ""}'

    def calculate_metric(self) -> float:
        self.fc.metric = self.metric
        self.fc.aggregation = self.aggregation
        self.fc.ignore_one_letter_word = self.ignore_one_letter_word
        return self.fc.calculate_metric()
