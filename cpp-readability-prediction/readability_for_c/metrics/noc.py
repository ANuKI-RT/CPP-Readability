from typing import Dict, Set, List

import numpy as np
from sklearn.cluster import DBSCAN

from code_processing import filter_manager
from code_processing.analyzer import CodeAnalyzer
from metrics.feature_calculator import FeatureCalculator, TextualFC


def get_all_feature_calculators(code: str, analyzer: CodeAnalyzer) -> Dict[str, FeatureCalculator]:
    fc_list = [
        NumberOfConceptsFC(analyzer=analyzer, code=code),
        NumberOfConceptsFC(analyzer=analyzer, code=code, eps=0.3, normalized=True),
    ]
    return {fc.name(): fc for fc in fc_list}


class NumberOfConceptsFC(TextualFC):
    """
    Also called Semantic Textual Coherence.
    This feature captures the number of concepts implemented in a snippet at line-level
    by clustering each line based on its set of terms.
    DBSCAN is used for clustering.
    """
    _MIN_SAMPLES = 2

    def __init__(self, eps: float = 0.1, normalized=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normalized = normalized
        self.eps = eps

    def name(self):
        return f'{"Normalized" if self.normalized else "Standard"} Number of Concepts'

    def calculate_metric(self) -> float:
        documents = self._extract_documents(self.code)
        if len(documents) == 0:
            return 0.
        distance_matrix = self._create_distance_matrix(documents)
        dbscan = DBSCAN(eps=self.eps, min_samples=self._MIN_SAMPLES, metric='precomputed')
        labels = dbscan.fit_predict(distance_matrix)
        cluster_size = len(set(labels)) - (1 if -1 in labels else 0)
        return cluster_size / len(documents) if self.normalized else float(cluster_size)

    def _extract_documents(self, source_code) -> List[Set[str]]:
        """
        Extract set of terms foreach line of code.
        :param source_code: the content of snippet
        :return: a list of sets of terms that represent terms each line of code
        """
        source_code = filter_manager.delete_blank_lines(source_code)
        lines_identifier = self.extract_lines_identifier_terms(source_code)
        return [self.convert_to_stems(identifiers) for identifiers in lines_identifier if len(identifiers) > 0]

    @classmethod
    def _get_distance(cls, doc: Set[str], other_doc: Set[str]) -> float:
        """
        Compute the overlap between 2 lines of code based on their terms.
        :param doc: the first set of terms to compute distance
        :param other_doc: the second set of terms to compute distance
        :return: The distance that represents the degree of overlap. Result is smaller means having more overlap.
        """
        intersection = doc.intersection(other_doc)
        union = doc.union(other_doc)
        return 1. - (len(intersection) / len(union)) if len(union) > 0 else 1.

    @classmethod
    def _create_distance_matrix(cls, documents: List[Set[str]]) -> np.array:
        documents_num = len(documents)
        distance_matrix = np.zeros((documents_num, documents_num))

        for i in range(documents_num):
            for j in range(documents_num):
                distance_matrix[i, j] = cls._get_distance(documents[i], documents[j])

        return distance_matrix
