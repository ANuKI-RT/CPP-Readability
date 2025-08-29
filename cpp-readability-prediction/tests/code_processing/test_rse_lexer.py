import unittest

from code_processing.lexer import TokenKind, CLangLexer
from code_processing.rse_lexer import RSELexer


class TestRSELexer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexer = RSELexer(CLangLexer())

    def test_lexing_operators(self):
        code = '+ - * / % ++ -- [ ] ( ) . -> .* ->* << >> | ^ & ~ ' \
               + '= += -= *= /= %= &= |= ^= >>= <<= == != > >= < <= && || ! ? : :: , { } ; ...'
        tokens = self.lexer.lexing(code)
        self.assertEqual([TokenKind.OPERATOR for _ in tokens], [token.kind for token in tokens])
        self.assertEqual('.*', tokens[13].value)
        self.assertEqual('->*', tokens[14].value)
        self.assertEqual('...', tokens[-1].value)

        self.assertEqual('^', tokens[18].value)
        self.assertEqual('^=', tokens[29].value)
        self.assertEqual('~', tokens[20].value)

        self.assertEqual('::', tokens[-6].value)
        self.assertEqual('->', tokens[12].value)
