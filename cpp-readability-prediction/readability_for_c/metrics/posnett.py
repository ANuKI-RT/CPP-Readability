import math
from typing import Generator, Union, Dict

from code_processing.lexer import Token, LexerDecorator, TokenKind, Lexer
from code_processing.rse_lexer import RSELexer
from metrics.feature_calculator import FeatureCalculator


def get_all_feature_calculators(code: str, lexer: Lexer) -> Dict[str, FeatureCalculator]:
    results = {}
    for metric in [
        'Posnett_Lines', 'Posnett_Entropy', 'Posnett_Volume',
    ]:
        fc = create_posnett_feature_calculator(metric, code, lexer)
        results[fc.name] = fc
    return results


def create_posnett_feature_calculator(metric_type: str, code: str, lexer: Lexer):
    lexer = RSELexer(lexer)
    if metric_type == 'Posnett_Lines':
        return PosnettLinesFC(code, lexer)
    elif metric_type == 'Posnett_Entropy':
        return PosnettEntropyFC(code, lexer)
    elif metric_type == 'Posnett_Volume':
        return PosnettVolumeFC(code, PosnettLexer(lexer))
    else:
        raise ValueError(f'Unknown metric type: {metric_type}')


class PosnettLexer(LexerDecorator):
    _TOKEN_KINDS = [
        TokenKind.IDENTIFIER,
        TokenKind.KEYWORD,
        TokenKind.OPERATOR,
        TokenKind.LITERAL,
        TokenKind.NUMBER,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dictionary = set()
        self._program_length = 0

    @property
    def vocab_size(self):
        return len(self._dictionary)

    @property
    def program_length(self):
        return self._program_length

    def lex(self, sourcefile_path: str) -> Generator[Token, None, None]:
        self._dictionary.clear()
        self._program_length = 0

        for token in super().lex(sourcefile_path):
            if token.kind in self._TOKEN_KINDS:
                self._update_with_token(token.value)
            elif token.kind == TokenKind.STRING and len(token.value) > 2:
                # Remove opening/closing quotes
                self._update_with_token(token.value[1:-1])

            yield token

    def _update_with_token(self, token_value: str):
        if token_value not in self._dictionary:
            self._dictionary.add(token_value)
        self._program_length += 1


class PosnettLinesFC(FeatureCalculator):
    @property
    def name(self):
        return "Posnett lines"

    def calculate_metric(self) -> float:
        return float(len(self.code.split('\n')))


class PosnettEntropyFC(FeatureCalculator):
    @property
    def name(self):
        return "Posnett entropy"

    def calculate_metric(self) -> float:
        snippet_bytes_dict = dict()
        snippet_bytes = bytes(self.code, 'utf-8')

        for byte in snippet_bytes:
            snippet_bytes_dict[byte] = snippet_bytes_dict.get(byte, 0) + 1
        total_bytes = len(snippet_bytes)

        entropy = 0.
        for unique_byte in snippet_bytes_dict.keys():
            prob_token = snippet_bytes_dict[unique_byte] / total_bytes
            if prob_token > 0:
                entropy += prob_token * math.log(prob_token)

        return -entropy


class PosnettVolumeFC(FeatureCalculator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lexer.lexing(self.code)
        self._posnett_lexer = self._retrieve_posnett_lexer(self.lexer)

    @property
    def name(self):
        return "Posnett volume"

    @property
    def vocab_size(self):
        return self._posnett_lexer.vocab_size

    @property
    def program_length(self):
        return self._posnett_lexer.program_length

    def calculate_metric(self) -> float:
        return self.program_length * (math.log(self.vocab_size) / math.log(2))

    @classmethod
    def _retrieve_posnett_lexer(cls, lexer: Union[LexerDecorator, Lexer]) -> PosnettLexer:
        """
        Find the PosnettLexer in the LexerDecorator
        :param lexer: the current lexer
        :return: the current lexer if it is an instance of PosnettLexer,
        else recursively finding in its child if it is a decorator.
        Otherwise, raise ValueError.
        """

        if isinstance(lexer, PosnettLexer):
            return lexer
        elif isinstance(lexer, LexerDecorator):
            return cls._retrieve_posnett_lexer(lexer.lexer)
        else:
            raise ValueError('lexer must be an instance of LexerDecorator or PosnettLexer')
