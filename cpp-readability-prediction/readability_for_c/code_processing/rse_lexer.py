import copy
from typing import Generator

from code_processing.lexer import TokenKind, LexerDecorator, Token


class RSELexer(LexerDecorator):
    """
    This class is an adaptation for the JavaLexer of the RSE package

    that is used for implementation of Dorn and Posnett in Java.

    There is a couple of differences in which token the lexer considers as an operator
    between lexer in RSE package and this adaptation.
        - C++ specific operators: '.*', '->*', '...'.
        - Being both C++ and Java operators but having not been handled at all in RSE package: '^', '^=', '~'.
        - Being both C++ and Java operators but having been handled differently: '->', '::'.

    For the first and second cases, this adaptation handles all of those operators even though RSE package did not.

    For the last case, the JavaLexer did not handle those operators correctly that it splits each of them into 2
    separate operators (e.g. '->' -> '-' and '>') because RSE package was developed in Java 7 which had not introduced
    lambda expression features.
    This adaptation also handles these operators similar to '->*' that is considered as
    a single operator.
    """

    _PUNCTUATORS_AS_OPERATORS = [
        ';', '{', '}',
    ]

    def lex(self, sourcefile_path: str) -> Generator[Token, None, None]:
        for token in super().lex(sourcefile_path):
            # Use a copy to prevent messing up with the original one
            token = copy.deepcopy(token)
            if token.kind == TokenKind.PUNCTUATION and token.value in self._PUNCTUATORS_AS_OPERATORS:
                token.kind = TokenKind.OPERATOR
            elif token.kind.value > TokenKind.NUMBER.value:
                token.kind = TokenKind.OTHER
            yield token
