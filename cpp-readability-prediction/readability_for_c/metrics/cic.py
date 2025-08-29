from typing import Dict

import wordnet
from code_processing import filter_manager
from code_processing.analyzer import CodeAnalyzer
from metrics.feature_calculator import FeatureCalculator, TextualFC


def get_all_feature_calculators(code: str, analyzer: CodeAnalyzer) -> Dict[str, FeatureCalculator]:
    fc_list = [CommentsIdentifierConsistencyFC(
        analyzer=analyzer,
        use_synonyms=use_synonyms,
        code=code,
    ) for use_synonyms in [False, True]]
    return {fc.name(): fc for fc in fc_list}


class CommentsIdentifierConsistencyFC(TextualFC):
    """
    Comments and Identifiers Consistency (CIC) by measuring the overlap between the terms used in a method comment
    and the terms used in the method body.
    The synonym version of CIC takes into account the synonyms of identifiers.
    Difference from original Java implementation:

    - There is no aggregation. This implementation calculates the overlap between terms in comment and source code.
    - Applying all 4 pre-processing steps for both comment and identifier terms in advance.
    - Use Porter algorithm to get stems instead of wordnet as implemented in original Java implementation.
    - Access WordNet using nltk instead of RiTa library.
    """

    def __init__(self, use_synonyms=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_synonyms = use_synonyms

    def name(self):
        if self.use_synonyms:
            return 'Synonym Comments and Identifiers Consistency'
        return 'Comments and Identifiers Consistency'

    def calculate_metric(self) -> float:
        source_code = filter_manager.delete_blank_lines(self.code)

        comment_words = self.extract_comment_terms(source_code)
        original_identifiers = self.extract_identifier_terms(source_code)
        identifiers = self.convert_to_stems(original_identifiers)

        if self.use_synonyms:
            syn_identifiers = set()
            for term in original_identifiers:
                for synonym in wordnet.get_synonyms(term):
                    try:
                        int(synonym)
                    except ValueError:
                        syn_identifiers.add(synonym)
            identifiers = identifiers.union(self.convert_to_stems(syn_identifiers))

        return len(identifiers.intersection(comment_words)) / len(identifiers.union(comment_words))
