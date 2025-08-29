from typing import Dict, Set, List

import numpy as np

from code_processing import filter_manager
from code_processing.analyzer import CodeAnalyzer
from code_processing.lexer import Lexer
from metrics.feature_calculator import FeatureCalculator, TextualFC


def get_all_feature_calculators(code: str, lexer: Lexer, analyzer: CodeAnalyzer) -> Dict[str, FeatureCalculator]:
    all_fc = {}
    for agg in TextualCoherenceFC.AGG_FUNCS.keys():
        fc = TextualCoherenceFC(agg, lexer=lexer, code=code, analyzer=analyzer, threshold=1)
        all_fc[fc.name] = fc
    return all_fc


class TextualCoherenceFC(TextualFC):
    """
    TC measures the overlap (correlation) of sets of terms of code blocks.

    Difference from original Java implementation:

    - Applying all 4 pre-processing steps for extracting terms to build dictionary.
    - Consider pre-processor blocks as regular code blocks.
    - Handle the case that a code block does not have any term after pre-processing.
    """
    AGGREGATIONS = ['MIN', 'AVG', 'MAX']
    AGG_FUNCS = {
        'MIN': min,
        'AVG': lambda vals: sum(vals) / len(vals) if len(vals) > 0 else 0.,
        'MAX': max,
    }

    def __init__(self, agg: str, threshold=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert agg in self.AGG_FUNCS
        self._agg = agg
        self._agg_func = self.AGG_FUNCS[agg]
        self._threshold = threshold
        self._documents = self._get_documents()
        self._dictionary = self._build_dictionary(self.code)

    @property
    def name(self):
        return f'Text Coherence {self._agg}'

    @property
    def documents(self):
        return self._documents

    @property
    def dictionary(self):
        return self._dictionary

    def calculate_metric(self) -> float:
        cosines = []
        for i in range(len(self._documents) - 1):
            vi = self._get_vector(self._dictionary, self._documents[i])
            if all([v == 0 for v in vi]):
                # There is not any 'term' extracted from the i-th block, so the correlation should be 0.
                cosines.append(0.)
                continue
            for j in range(i + 1, len(self._documents)):
                vj = self._get_vector(self._dictionary, self._documents[j])
                if all([v == 0 for v in vj]):
                    # There is not any 'term' extracted from the j-th block, so the correlation should be 0.
                    cosines.append(0.)
                    continue
                cosine = np.dot(vi, vj) / (np.linalg.norm(vi) * np.linalg.norm(vj))
                cosines.append(cosine)

        if len(cosines) == 0:
            return 0.

        return self._agg_func(cosines)

    def _get_documents(self):
        documents = self._get_code_blocks()
        documents += self._get_preprocessor_blocks()
        documents = [
            doc for doc in documents
            if (len(doc.split('\n')) - 2 >= self._threshold and doc.startswith('{') and doc.endswith('}')) or
               (len(doc.split('\n')) >= self._threshold and not doc.startswith('{'))  # blocks not in brackets
        ]
        return documents

    def _get_code_blocks(self) -> List[str]:
        blocks = []
        stack = []
        for token in self.tokens:
            if token.value == '{':
                stack.append(token)
            elif token.value == '}' and len(stack) > 0:
                opening_token = stack.pop()
                if token.end_location.line - opening_token.start_location.line > 1:
                    # Only count block that has at least a line in between (so that there are statements)
                    block = self.code[opening_token.start_location.offset: token.end_location.offset]
                    blocks.append(block)
        return blocks

    def _get_preprocessor_blocks(self):
        method_implementation_str = self.code
        blocks = []
        preprocessor_keywords = ['#ifdef', '#ifndef', '#if', '#elif', '#else', '#endif']
        pre_pro_text = method_implementation_str
        tmp_text = method_implementation_str
        preprocessor_index_list = []
        for pre_pro_keyword in preprocessor_keywords:
            while tmp_text.count(pre_pro_keyword) > 0:
                preprocessor_index_list.append(tmp_text.index(pre_pro_keyword))
                preprocessor_index_list.append(tmp_text.index(pre_pro_keyword) + len(pre_pro_keyword))
                space_string = ''
                space_idx = 0
                while space_idx < len(pre_pro_keyword):
                    space_string += ' '
                    space_idx += 1
                tmp_text = (tmp_text[:tmp_text.index(pre_pro_keyword)] +
                            space_string +
                            tmp_text[tmp_text.index(pre_pro_keyword) + len(pre_pro_keyword):])
        if len(preprocessor_index_list) > 0:
            start_idx = min(preprocessor_index_list)
            while pre_pro_text[start_idx] != '\n':
                start_idx -= 1
            start_idx += 1
            end_idx = max(preprocessor_index_list)
            preprocessors_lines = pre_pro_text[start_idx:end_idx].split('\n')
            rows_count = len(preprocessors_lines)
            line_lengths = [len(line) for line in preprocessors_lines]
            columns_count = max(line_lengths)
            preprocessors_matrix = [['' for _ in range(columns_count)] for _ in range(rows_count)]
            row_idx = 0
            while row_idx < rows_count:
                row_length = len(preprocessors_lines[row_idx])
                column_idx = 0
                while column_idx < row_length:
                    preprocessors_matrix[row_idx][column_idx] = preprocessors_lines[row_idx][column_idx]
                    column_idx += 1
                row_idx += 1
            row_idx = 0
            block_indexes = []
            while row_idx < rows_count:
                row = preprocessors_matrix[row_idx]
                column_idx = 0
                while row[column_idx] != '#' and column_idx < columns_count - 1:
                    column_idx += 1
                if row[column_idx] == '#' and not (row[column_idx + 1] == 'e' and row[column_idx + 2] == 'n'):
                    row_inner_idx = row_idx + 1
                    start_inner_idx = row_inner_idx
                    while row_inner_idx < rows_count:
                        row_inner = preprocessors_matrix[row_inner_idx]
                        column_inner_idx = 0
                        while row_inner[column_inner_idx] != '#' and column_inner_idx < columns_count - 1:
                            column_inner_idx += 1
                        if row_inner[column_inner_idx] == '#' and column_inner_idx == column_idx:
                            block_indexes.append([start_inner_idx, row_inner_idx])
                            break
                        row_inner_idx += 1
                row_idx += 1
            for item in block_indexes:
                block_text = ''
                start_idx = item[0]
                end_idx = item[1]
                while start_idx < end_idx:
                    column_idx = 0
                    while column_idx < columns_count:
                        block_text = block_text + preprocessors_matrix[start_idx][column_idx]
                        column_idx += 1

                    block_text = block_text + '\n'
                    start_idx += 1
                if block_text.strip() != '':
                    blocks.append(block_text)
        return blocks

    def _build_dictionary(self, source_code: str) -> Set[str]:
        source_code = filter_manager.delete_blank_lines(source_code)
        dict_words = self.extract_identifier_terms(source_code)
        return self.convert_to_stems(dict_words)

    def _get_vector(self, full_dict: Set[str], source_code: str) -> np.array:
        doc_dict = self._build_dictionary(source_code)
        overlap = full_dict.intersection(doc_dict)
        return np.asarray([1 if word in overlap else 0 for word in sorted(list(full_dict))])
