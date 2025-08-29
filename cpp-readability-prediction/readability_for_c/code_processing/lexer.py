import os
import re
import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import Generator, List

import clang
from clang.cindex import Config


class TokenKind(Enum):
    IDENTIFIER = 1
    COMMENT = 2
    KEYWORD = 3
    OPERATOR = 4
    LITERAL = 5
    STRING = 6
    NUMBER = 7
    PUNCTUATION = 10
    OTHER = 0


@dataclass
class Location:
    line: int
    column: int
    offset: int


@dataclass
class Token:
    """Class for keeping track of a token in source code file."""
    value: str
    start_location: Location
    end_location: Location
    kind: TokenKind

    def __repr__(self):
        return self.value


class Lexer:
    @property
    def file_ext(self):
        raise NotImplementedError('Implement me')

    def lex(self, sourcefile_path) -> Generator[Token, None, None]:
        raise NotImplementedError('Implement me')

    def lexing(self, code: str) -> List[Token]:
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{self.file_ext}') as fp:
            fp.write(code)
            fp.flush()
            tokens = list(self.lex(fp.name))
            return tokens

    @staticmethod
    def create_lexer(language: str) -> "Lexer":
        if 'cpp' == language:
            return CLangLexer()
        raise ValueError(f'Not supported language: {language}')


class LexerDecorator(Lexer):
    """
    For customizing lex method
    """

    def __init__(self, lexer: Lexer):
        self.lexer = lexer

    @property
    def file_ext(self):
        return self.lexer.file_ext

    def lex(self, sourcefile_path) -> Generator[Token, None, None]:
        for token in self.lexer.lex(sourcefile_path):
            yield token


class CachedLexer(LexerDecorator):
    """
    Caching tokens list after lexing by the code content.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokens = []
        self._code = None

    def lexing(self, code: str) -> List[Token]:
        if self._code == code:
            return self.tokens
        self.tokens = super().lexing(code)
        self._code = code
        return self.tokens


class CLangLexer(Lexer):
    CHAR_LITERAL_PATTERN = re.compile('^(u8|u|U|L)?\'.+\'$')
    STRING_LITERAL_PATTERN = re.compile('^(u8|u|U|L)?R?\".*\"$')
    FLOAT_LITERAL_PATTERN = re.compile('^-?\\d*\\.\\d*(e\\d+)?([fF])?([lL])?$')
    INTEGER_LITERAL_PATTERN = re.compile(
        '^((-?\\d+([uU])?(l{1,2}|L{1,2})?)|(0([xX])(\\d|[a-f]|[A-F])+([uU])?(l{1,2}|L{1,2})?))$'
    )

    _token_kinds_mappings = {
        clang.cindex.TokenKind.IDENTIFIER: TokenKind.IDENTIFIER,
        clang.cindex.TokenKind.COMMENT: TokenKind.COMMENT,
        clang.cindex.TokenKind.KEYWORD: TokenKind.KEYWORD,
        clang.cindex.TokenKind.LITERAL: TokenKind.LITERAL,
        clang.cindex.TokenKind.PUNCTUATION: TokenKind.PUNCTUATION,
    }

    # Reference from https://cplusplus.com/doc/tutorial/operators/
    # Operators like new, delete, sizeof are considered as KEYWORD
    _operators = [
        '+', '-', '*', '/', '%',  # Arithmetic
        '++', '--', '[', ']', '(', ')', '.', '->',  # Unary
        '.*', '->*',  # Access pointer
        '<<', '>>', '|', '^', '&', '~',  # Bitwise
        '=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '>>=', '<<=',  # (Compound) assignment
        '==', '!=', '>', '>=', '<', '<=',  # Comparison
        '&&', '||', '!',  # Logical
        '?', ':',  # Conditional
        '::',  # Scope qualifier
        ',',  # Comma separator
        '...',  # Variadic
    ]

    CLANG_LIB_PATH = os.path.join(os.path.dirname(os.path.realpath(clang.__file__)), 'native')
    Config.set_library_path(CLANG_LIB_PATH)
    print('CLANG_LIB_PATH: ', Config.library_path)

    @property
    def file_ext(self):
        return 'cpp'

    def lex(self, sourcefile_path) -> Generator[Token, None, None]:
        index = clang.cindex.Index.create()
        tu = index.parse(sourcefile_path)
        for clang_token in tu.get_tokens(extent=tu.cursor.extent):
            yield self.to_token(clang_token)

    @classmethod
    def to_token(cls, clang_token: clang.cindex.Token) -> Token:
        return Token(
            value=clang_token.spelling,
            start_location=Location(
                line=clang_token.extent.start.line,
                column=clang_token.extent.start.column,
                offset=clang_token.extent.start.offset),
            end_location=Location(
                line=clang_token.extent.end.line,
                column=clang_token.extent.end.column,
                offset=clang_token.extent.end.offset),
            kind=cls.get_token_kind(clang_token),
        )

    @classmethod
    def get_token_kind(cls, token: clang.cindex.Token) -> TokenKind:
        if clang.cindex.TokenKind.LITERAL == token.kind:
            if cls.STRING_LITERAL_PATTERN.match(token.spelling) is not None:
                return TokenKind.STRING
            elif (cls.INTEGER_LITERAL_PATTERN.match(token.spelling) is not None
                  or cls.FLOAT_LITERAL_PATTERN.match(token.spelling) is not None):
                return TokenKind.NUMBER
            return TokenKind.LITERAL
        elif clang.cindex.TokenKind.PUNCTUATION == token.kind and token.spelling in cls._operators:
            return TokenKind.OPERATOR

        return cls._token_kinds_mappings.get(token.kind, TokenKind.OTHER)
