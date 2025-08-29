import math
import re
from typing import List, Callable, Dict

import numpy as np
from numpy import fft, std

from code_processing.analyzer import CodeAnalyzer
from code_processing.lexer import Lexer, Token, TokenKind
from code_processing.rse_lexer import RSELexer
from metrics.feature_calculator import FeatureCalculator


def create_dorn_feature_calculator(metric_type: str, code: str, lexer: Lexer, **kwargs):
    lexer = RSELexer(lexer)
    if metric_type == 'Dorn_CharactersAlignmentBlocks':
        return CharactersAlignmentBlocks(code, lexer)
    elif metric_type == 'Dorn_CharactersAlignmentExtent':
        return CharactersAlignmentExtent(code, lexer)

    elif metric_type == 'Dorn_ColorsAreas':
        assert isinstance(kwargs.get('kind', None), TokenKind)
        return ColorsAreas(kwargs.get('kind'), code=code, lexer=lexer)
    elif metric_type == 'Dorn_ColorsMutualAreas':
        assert isinstance(kwargs.get('kind1', None), TokenKind)
        assert isinstance(kwargs.get('kind2', None), TokenKind)
        return ColorsMutualAreas(
            kwargs.get('kind1'), kwargs.get('kind2'),
            code=code, lexer=lexer,
        )

    elif metric_type == 'Dorn_DFTBandwidth':
        assert isinstance(kwargs.get('analyzer', None), CodeAnalyzer)
        analyzer = kwargs.get('analyzer')
        assert isinstance(kwargs.get('kind', None), str)

        return DFTBandwidth(
            kwargs.get('kind'), analyzer,
            code=code, lexer=lexer,
        )
    elif metric_type == 'Dorn_VisualBandwidth2D':
        assert isinstance(kwargs.get('kind', None), TokenKind)
        assert kwargs.get('coordinate', None) in ['X', 'Y']
        return VisualBandwidth2D(
            kwargs.get('coordinate'), kwargs.get('kind'),
            code=code, lexer=lexer,
        )
    else:
        raise ValueError(f'Unknown metric type: {metric_type}')


def get_all_feature_calculators(code: str, lexer: Lexer, analyzer=None) -> Dict[str, FeatureCalculator]:
    results = {}

    for metric in ['Dorn_CharactersAlignmentBlocks', 'Dorn_CharactersAlignmentExtent']:
        fc = create_dorn_feature_calculator(metric, code, lexer)
        results[fc.name] = fc

    for kind in ColorsAreas.ALL_KINDS:
        fc = create_dorn_feature_calculator('Dorn_ColorsAreas', code, lexer, kind=kind)
        results[fc.name] = fc

    for i in range(len(ColorsMutualAreas.ALL_KINDS) - 1):
        for j in range(i + 1, len(ColorsMutualAreas.ALL_KINDS)):
            kind1 = ColorsMutualAreas.ALL_KINDS[j]
            kind2 = ColorsMutualAreas.ALL_KINDS[i]
            fc = create_dorn_feature_calculator(
                'Dorn_ColorsMutualAreas', code, lexer, kind1=kind1, kind2=kind2)
            results[fc.name] = fc

    for kind in DFTBandwidth.ALL_KINDS:
        assert isinstance(analyzer, CodeAnalyzer)
        fc = create_dorn_feature_calculator(
            'Dorn_DFTBandwidth', code, lexer, kind=kind, analyzer=analyzer)
        results[fc.name] = fc

    for kind in VisualBandwidth2D.ALL_KINDS:
        for coordinate in ['X', 'Y']:
            fc = create_dorn_feature_calculator(
                'Dorn_VisualBandwidth2D', code, lexer, coordinate=coordinate, kind=kind)
            results[fc.name] = fc

    return results


class CharactersAlignmentBlocks(FeatureCalculator):
    @property
    def name(self):
        return 'Dorn align blocks'

    def calculate_metric(self) -> float:
        lines = self.lines
        if len(lines) < 1:
            return 0.0

        max_length = max([len(line) for line in lines])
        blocks = 0
        in_block = False
        last_char = ''

        for i in range(max_length):
            for line in lines:
                if i >= len(line):
                    last_char = ''
                    continue
                if line[i] != last_char:
                    in_block = False
                    last_char = line[i]
                elif not in_block and last_char not in ['', ' ', '\n', '\t']:
                    in_block = True
                    blocks += 1
            in_block = False
            last_char = ''

        return float(blocks)


class CharactersAlignmentExtent(FeatureCalculator):
    @property
    def name(self):
        return 'Dorn align extent'

    def calculate_metric(self) -> float:
        lines = self.lines
        if len(lines) < 1:
            return 0.0

        max_length = max([len(line) for line in lines])
        extent = 0
        last_char = ''

        for i in range(max_length):
            for line in lines:
                if i >= len(line):
                    last_char = ''
                    continue
                if line[i] == last_char and last_char not in ['', ' ', '\n', '\t']:
                    extent += 1
                else:
                    last_char = line[i]
            last_char = ''

        return float(extent)


class VisualFeatureCalculator(FeatureCalculator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lines = self.lines
        self.rows = len(lines)
        self.cols = max([len(line) for line in lines]) if len(lines) > 0 else 0
        self._color_matrix = None

    @property
    def color_matrix(self):
        if self._color_matrix is not None:
            return self._color_matrix
        self._color_matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for token in self.tokens:
            if token.kind == TokenKind.COMMENT and token.start_location.line != token.end_location.line:
                block_comment_lines = token.value.splitlines(keepends=True)
                start_j = token.start_location.column - 1
                for i, line in enumerate(block_comment_lines):
                    for j in range(start_j, start_j + len(line)):
                        self._color_matrix[i + token.start_location.line - 1][j] = token.kind.value
                    start_j = 0
            elif token.start_location.line == token.end_location.line:
                for j in range(token.start_location.column - 1, token.end_location.column - 1):
                    self._color_matrix[token.start_location.line - 1][j] = token.kind.value
            else:
                raise RuntimeError(f'Unknown multi-lines token: {token.value} - {token.kind.name}')
        return self._color_matrix


class ColorsAreas(VisualFeatureCalculator):
    ALL_KINDS = [
        TokenKind.IDENTIFIER,
        TokenKind.COMMENT,
        TokenKind.KEYWORD,
        TokenKind.OPERATOR,
        TokenKind.NUMBER,
        TokenKind.STRING,
        TokenKind.LITERAL,
    ]

    def __init__(self, kind: TokenKind, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind

    @property
    def name(self):
        return f'Dorn Areas {self.kind.name}s'

    def calculate_metric(self) -> float:
        color_matrix = self.color_matrix
        total = 0
        total_color = 0
        for i in range(self.rows):
            first_char = False
            for j in range(self.cols - 1, -1, -1):
                if color_matrix[i][j] != 0 or first_char:
                    first_char = True
                    total += 1
                    if color_matrix[i][j] == self.kind.value:
                        total_color += 1

        return float(total_color) / total if total > 0 else 0.


class ColorsMutualAreas(VisualFeatureCalculator):
    ALL_KINDS = [
        TokenKind.COMMENT,
        TokenKind.IDENTIFIER,
        TokenKind.KEYWORD,
        TokenKind.NUMBER,
        TokenKind.STRING,
        TokenKind.LITERAL,
        TokenKind.OPERATOR,
    ]

    def __init__(self, kind1: TokenKind, kind2: TokenKind, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind1 = kind1
        self.kind2 = kind2

    @property
    def name(self):
        return f'Dorn Areas {self.kind1.name}s / {self.kind2.name}s'

    @classmethod
    def get_all_features(cls, lexer: RSELexer) -> List["ColorsMutualAreas"]:
        return [
            ColorsMutualAreas(cls.ALL_KINDS[i], cls.ALL_KINDS[j], lexer=lexer)
            for i in range(len(cls.ALL_KINDS) - 1)
            for j in range(i + 1, len(cls.ALL_KINDS))
        ]

    def calculate_metric(self) -> float:
        color_matrix = self.color_matrix
        total_color1 = 0
        total_color2 = 0
        for i in range(self.rows):
            first_char = False
            for j in range(self.cols - 1, -1, -1):
                if color_matrix[i][j] != 0 or first_char:
                    first_char = True
                    if color_matrix[i][j] == self.kind1.value:
                        total_color1 += 1
                    if color_matrix[i][j] == self.kind2.value:
                        total_color2 += 1

        return float(total_color1) / total_color2 if total_color2 > 0 else 0.


class DFTBandwidth(VisualFeatureCalculator):
    ALL_KINDS = [
        'Assignments',
        'Commas',
        'Comments',
        'Comparisons',
        'Conditionals',
        'Indentations',
        'Keywords',
        'LineLengths',
        'Loops',
        'Identifiers',
        'Numbers',
        'Operators',
        'Parenthesis',
        'Periods',
        'Spaces',
    ]

    def __init__(self, kind: str, analyzer: CodeAnalyzer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
        self.analyzer = analyzer
        self._features_func = [
            self.get_assignments,
            self.get_commas,
            self.get_comments,
            self.get_comparisons,
            self.get_ifs,
            self.get_indentations,
            self.get_keywords,
            self.get_line_lengths,
            self.get_loops,
            self.get_identifiers,
            self.get_numbers,
            self.get_operators,
            self.get_parenthesis,
            self.get_periods,
            self.get_spaces,
        ]

    @property
    def name(self):
        return f'Dorn DFT {self.kind}'

    def calculate_metric(self) -> float:
        amplitudes = self.get_dft_amplitudes(self.get_features())
        return self.calculate_bandwidth(amplitudes) + 1

    @staticmethod
    def calculate_bandwidth(vector: List[float]) -> float:
        std_value = std(vector)
        for i in range(len(vector) - 1, -1, -1):
            if vector[i] > std_value:
                return float(i)
        return 0.0

    @staticmethod
    def get_dft_amplitudes(signals: List[float]) -> List[float]:
        if len(signals) == 0:
            return []
        coefficients = fft.fft(signals + [0.0 for _ in range(len(signals))], n=len(signals)).view(np.float64)
        amplitudes = [
            math.sqrt(
                (coefficients[2 * i] * coefficients[2 * i]) + (coefficients[2 * i + 1] * coefficients[2 * i + 1])
            )
            for i in range(len(signals))
        ]
        return amplitudes

    def get_features(self) -> List[float]:
        func = None
        for i, kind in enumerate(self.ALL_KINDS):
            if kind == self.kind:
                func = self._features_func[i]
        if func:
            return func()
        return []

    def get_assignments(self) -> List[float]:
        return self._get_len_split_by_pattern(r'[^=]=[^=]')

    def get_commas(self) -> List[float]:
        return self._get_len_split_by_delimiter(',')

    def get_comments(self) -> List[float]:
        color_matrix = self.color_matrix
        return [
            0.0 if any([
                color_matrix[i][j] not in [0, TokenKind.COMMENT.value] for j in range(len(color_matrix[i]))
            ]) or TokenKind.COMMENT.value not in color_matrix[i]
            else 1.0
            for i in range(len(color_matrix))
        ]

    def get_indentations(self) -> List[float]:
        code = self.analyzer.delete_comments(self.code)
        lines = code.splitlines()
        indentations = [0.0 for _ in range(len(lines))]
        for i, line in enumerate(lines):
            indentation_length = 0
            for j in range(len(line)):
                if line[j] not in [' ', '\t']:
                    break
                indentation_length += 1 if line[j] == ' ' else 4
            indentations[i] += indentation_length
        return indentations

    def get_comparisons(self) -> List[float]:
        return self._get_len_split_by_pattern(r'(==|<=|>=|!=|<|>)')

    def get_ifs(self) -> List[float]:
        return self._count_tokens(lambda token: token.kind == TokenKind.KEYWORD and token.value == 'if')

    def get_keywords(self) -> List[float]:
        return self._count_tokens(lambda token: token.kind == TokenKind.KEYWORD)

    def get_line_lengths(self) -> List[float]:
        return [len(line) for line in self.lines]

    def get_loops(self) -> List[float]:
        return self._count_tokens(lambda token: token.kind == TokenKind.KEYWORD and token.value in ['while', 'for'])

    def get_identifiers(self) -> List[float]:
        return self._count_tokens(lambda token: token.kind == TokenKind.IDENTIFIER)

    def get_numbers(self) -> List[float]:
        return self._get_len_split_by_pattern(r'[^A-Za-z]\d+\.?\d*')

    def get_operators(self) -> List[float]:
        return self._get_len_split_by_pattern(r'[+\-*/%]')

    def get_parenthesis(self) -> List[float]:
        return self._get_len_split_by_pattern(r'[({]')

    def get_periods(self) -> List[float]:
        return self._get_len_split_by_delimiter('.')

    def get_spaces(self) -> List[float]:
        code = self.analyzer.delete_comments(self.code)
        lines = code.splitlines()
        return [
            0. if line.strip() == '' else float(len(line.split(' ')) - 1)
            for line in lines
        ]

    def _get_len_split_by_pattern(self, pattern: str) -> List[float]:
        code = self.analyzer.delete_comments(self.code)
        lines = code.splitlines()
        return [
            float(len(re.split(pattern, line)) - 1)
            for line in lines
        ]

    def _get_len_split_by_delimiter(self, delimiter: str) -> List[float]:
        code = self.analyzer.delete_comments(self.code)
        lines = code.splitlines()
        return [
            float(len(line.split(delimiter)) - 1)
            for line in lines
        ]

    def _count_tokens(self, predicate: Callable[[Token], bool]) -> List[float]:
        code = self.analyzer.delete_comments(self.code)
        tokens = self.lexer.lexing(code)
        results = [0.0 for _ in range(len(code.splitlines()))]
        for token in tokens:
            if predicate(token):
                results[token.start_location.line - 1] += 1.0
        return results


class VisualBandwidth2D(VisualFeatureCalculator):
    ALL_KINDS = [
        TokenKind.COMMENT,
        TokenKind.IDENTIFIER,
        TokenKind.KEYWORD,
        TokenKind.NUMBER,
        TokenKind.STRING,
        TokenKind.LITERAL,
        TokenKind.OPERATOR,
    ]

    def __init__(self, coordinate: str, kind: TokenKind, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinate = coordinate
        self.kind = kind

    @property
    def name(self):
        return f'Dorn Visual {self.coordinate} {self.kind.name}'

    def calculate_metric(self) -> float:
        color_matrix = self.get_matrix()
        amplitudes = self.get_dft_amplitudes(color_matrix)
        if len(color_matrix) == 0 or len(color_matrix[0]) == 0:
            return 0.
        rows, cols = len(color_matrix), len(color_matrix[0])
        ndarray = np.asarray(amplitudes)
        size = rows if self.coordinate == 'X' else cols
        total = sum([
            DFTBandwidth.calculate_bandwidth(
                (ndarray[i, :] if self.coordinate == 'X' else ndarray[:, i]).tolist()
            ) for i in range(size)
        ])
        return total / size

    @staticmethod
    def get_dft_amplitudes(signals: List[List[float]]) -> List[List[float]]:
        if len(signals) == 0 or len(signals[0]) == 0:
            return []

        coefficients = (fft.fft2(np.asarray(signals)).reshape((1, len(signals) * len(signals[0])))
                        .view(np.float64).reshape((len(signals), 2 * len(signals[0]))))
        amplitudes = [
            [
                math.sqrt(
                    (coefficients[i][2 * j] * coefficients[i][2 * j])
                    + (coefficients[i][2 * j + 1] * coefficients[i][2 * j + 1])
                )
                for j in range(len(signals[i]))
            ] for i in range(len(signals))
        ]
        return amplitudes

    def get_matrix(self) -> List[List[float]]:
        color_matrix = self.color_matrix
        matrix = []
        for i in range(self.rows):
            matrix.append([])
            for j in range(self.cols):
                matrix[i].append(1.0 if color_matrix[i][j] == self.kind.value else 0.0)
        return matrix
