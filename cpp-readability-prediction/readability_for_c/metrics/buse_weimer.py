from enum import Enum
from typing import Callable, List, Dict

from code_processing.analyzer import CodeAnalyzer
from code_processing.lexer import Token, TokenKind, Lexer
from metrics.feature_calculator import FeatureCalculator


def create_bw_feature_calculator(metric_type: str, code: str, lexer: Lexer, **kwargs):
    if metric_type == 'BW_AvgBlankLine':
        return AvgBlankLineBWFC(code, lexer)
    elif metric_type == 'BW_AvgComment':
        return AvgCommentBWFC(code, lexer)
    elif metric_type == 'BW_MaxCharOccurrence':
        return MaxCharOccurrenceBWFC(code, lexer)
    elif metric_type == 'BW_MaxWordOccurrence':
        return MaxWordOccurrenceBWFC(code, lexer)

    assert isinstance(kwargs.get('aggregation', None), Aggregation)
    assert isinstance(kwargs.get('analyzer', None), CodeAnalyzer)
    if metric_type == 'BW_IdentifiersLength':
        return IdentifiersLengthBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Assignment':
        return AssignmentBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Commas':
        return CommasBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Comparison':
        return ComparisonBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Condition':
        return ConditionBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Keyword':
        return KeywordBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Indentation':
        return IndentationBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_LineLength':
        return LineLengthBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Space':
        return SpaceBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Loop':
        return LoopBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_NumberOfIdentifiers':
        return NumberOfIdentifiersBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Number':
        return NumberBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Operator':
        return OperatorBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Parenthesis':
        return ParenthesisBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    elif metric_type == 'BW_Period':
        return PeriodBWFC(kwargs['analyzer'], kwargs['aggregation'], code, lexer)
    else:
        raise ValueError(f'Unknown metric type: {metric_type}')


def get_all_feature_calculators(code: str, lexer: Lexer, analyzer=None) -> Dict[str, FeatureCalculator]:
    results = {}
    for metric in [
        'BW_AvgBlankLine', 'BW_AvgComment', 'BW_MaxCharOccurrence', 'BW_MaxWordOccurrence'
    ]:
        fc = create_bw_feature_calculator(metric, code, lexer)
        results[fc.name] = fc

    assert isinstance(analyzer, CodeAnalyzer)

    for metric in [
        'BW_Assignment', 'BW_Commas', 'BW_Comparison', 'BW_Condition', 'BW_Space',
        'BW_Loop', 'BW_Operator', 'BW_Parenthesis', 'BW_Period',
    ]:
        # Only AVG aggregation
        fc = create_bw_feature_calculator(metric, code, lexer, aggregation=Aggregation.AVG, analyzer=analyzer)
        results[fc.name] = fc

    for metric in [
        'BW_IdentifiersLength', 'BW_Keyword', 'BW_LineLength',
        'BW_NumberOfIdentifiers', 'BW_Number', 'BW_Indentation',
    ]:
        # Both AVG and MAX aggregation
        for agg in Aggregation:
            fc = create_bw_feature_calculator(metric, code, lexer, aggregation=agg, analyzer=analyzer)
            results[fc.name] = fc

    return results


class Aggregation(Enum):
    AVG = 0
    MAX = 1


class BuseWeimerFC(FeatureCalculator):
    def __init__(self, aggregation: Aggregation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggregation = aggregation

    @staticmethod
    def filter_tokens_by_predicate(tokens: List[Token], predicate: Callable[[Token], bool]) -> List[Token]:
        return [token for token in tokens if predicate(token)]


class AvgBlankLineBWFC(BuseWeimerFC):
    def __init__(self, *args, **kwargs):
        super().__init__(Aggregation.AVG, *args, **kwargs)

    @property
    def name(self):
        return f'BW {self.aggregation.name} blank lines'

    def calculate_metric(self) -> float:
        return float(len([1 for line in self.lines if len(line.strip()) == 0])) / float(len(self.lines))


class AvgCommentBWFC(BuseWeimerFC):
    def __init__(self, *args, **kwargs):
        super().__init__(Aggregation.AVG, *args, **kwargs)

    @property
    def name(self):
        return f'BW {self.aggregation.name} comments'

    def calculate_metric(self) -> float:
        comment_lines = set()
        for token in self.tokens:
            if token.kind != TokenKind.COMMENT:
                continue
            for i in range(token.start_location.line, token.end_location.line + 1):
                comment_lines.add(i)

        return float(len(comment_lines)) / float(len(self.lines))


class MaxCharOccurrenceBWFC(BuseWeimerFC):
    def __init__(self, *args, **kwargs):
        super().__init__(Aggregation.MAX, *args, **kwargs)

    @property
    def name(self):
        return f'BW {self.aggregation.name} char'

    def calculate_metric(self) -> float:
        char_counts = {}
        for line in self.lines:
            for c in line:
                count = char_counts.get(c, 0)
                char_counts[c] = count + 1
        return float(max(char_counts.values()))


class MaxWordOccurrenceBWFC(BuseWeimerFC):
    def __init__(self, *args, **kwargs):
        super().__init__(Aggregation.MAX, *args, **kwargs)

    @property
    def name(self):
        return f'BW {self.aggregation.name} words'

    def calculate_metric(self) -> float:
        word_counts = {}
        for token in self.tokens:
            for word in token.value.split():
                count = word_counts.get(word, 0)
                word_counts[word] = count + 1
        return float(max(word_counts.values()))


class IdentifiersLengthBWFC(BuseWeimerFC):
    def __init__(self, analyzer: CodeAnalyzer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = analyzer.delete_comments(self.code)

    @property
    def name(self):
        return f'BW {self.aggregation.name} identifiers length'

    def calculate_metric(self) -> float:
        identifiers = self.filter_tokens_by_predicate(self.tokens, lambda token: token.kind == TokenKind.IDENTIFIER)
        if Aggregation.MAX == self.aggregation:
            return float(max([len(identifier.value) for identifier in identifiers]))
        elif Aggregation.AVG == self.aggregation:
            return float(sum([len(identifier.value) for identifier in identifiers])) / float(len(identifiers))
        raise ValueError(f'{self.name} Not supported aggregation: {self.aggregation.name}')


class LineBasedBWFC(BuseWeimerFC):
    def __init__(self, analyzer: CodeAnalyzer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = analyzer.delete_comments(self.code)

    def calculate_line_metric(self, line_tokens: List[Token], line_index: int) -> float:
        raise NotImplementedError()

    def calculate_metric(self) -> float:
        lines_tokens = [[] for _ in self.lines]
        for token in self.tokens:
            lines_tokens[token.start_location.line - 1].append(token)
        scores = [
            self.calculate_line_metric(line_tokens, line_index)
            for line_index, line_tokens in enumerate(lines_tokens)
        ]
        if Aggregation.MAX == self.aggregation:
            return max(scores)
        elif Aggregation.AVG == self.aggregation:
            return sum(scores) / len(lines_tokens)
        raise ValueError(f'{self.__class__.name} Not supported aggregation: {self.aggregation.name}')


class AssignmentBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} assignment'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.OPERATOR and token.value in [
                '=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='
            ]
        )))


class CommasBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} commas'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.value == ','
        )))


class ComparisonBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} comparisons'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.OPERATOR and token.value in ['==', '!=', '>', '>=', '<', '<=']
        )))


class ConditionBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} conditionals'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.KEYWORD and token.value in ['if']
        )))


class KeywordBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} keywords'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.KEYWORD
        )))


class IndentationBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} indentation'

    def calculate_line_metric(self, _: List[Token], line_index: int) -> float:
        line = self.lines[line_index].replace('\t', ''.join([' ' for _ in range(self.tab_size)]))
        return float(len(line) - len(line.lstrip(' ')))


class LineLengthBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} line length'

    def calculate_line_metric(self, _: List[Token], line_index: int) -> float:
        return float(len(self.lines[line_index].strip('\n')))


class SpaceBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} spaces'

    def calculate_line_metric(self, _: List[Token], line_index: int) -> float:
        if self.lines[line_index].strip() == '':
            return 0.
        return float(len(self.lines[line_index].split(' ')) - 1)


class LoopBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} loops'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.KEYWORD and token.value in ['for', 'while']
        )))


class NumberOfIdentifiersBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} number of identifiers'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.IDENTIFIER
        )))


class NumberBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} numbers'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.NUMBER
        )))


class OperatorBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} operators'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.kind == TokenKind.OPERATOR and token.value in ['+', '-', '*', '/', '%']
        )))


class ParenthesisBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} parenthesis'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.value in ['(', '{']
        )))


class PeriodBWFC(LineBasedBWFC):
    @property
    def name(self):
        return f'BW {self.aggregation.name} periods'

    def calculate_line_metric(self, line_tokens: List[Token], _: int) -> float:
        return float(len(self.filter_tokens_by_predicate(
            line_tokens,
            lambda token: token.value == '.'
        )))
