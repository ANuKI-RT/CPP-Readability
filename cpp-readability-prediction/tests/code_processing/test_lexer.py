import unittest

from code_processing.lexer import Token, TokenKind, Location, CLangLexer


class TestCLangLexer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexer = CLangLexer()

    def test_lexing_operators(self):
        code = '''std::cout<<(!(this->count - 1 > 0) ? foo(this.x[0], this.*y) : this->*count)++;'''
        tokens = self.lexer.lexing(code)
        self.assertEqual(Token('::', Location(1, 4, 3), Location(1, 6, 5), TokenKind.OPERATOR), tokens[1])
        self.assertEqual(Token('<<', Location(1, 10, 9), Location(1, 12, 11), TokenKind.OPERATOR), tokens[3])
        self.assertEqual(Token('(', Location(1, 12, 11), Location(1, 13, 12), TokenKind.OPERATOR), tokens[4])
        self.assertEqual(Token('!', Location(1, 13, 12), Location(1, 14, 13), TokenKind.OPERATOR), tokens[5])
        self.assertEqual(Token('->', Location(1, 19, 18), Location(1, 21, 20), TokenKind.OPERATOR), tokens[8])
        self.assertEqual(Token('-', Location(1, 27, 26), Location(1, 28, 27), TokenKind.OPERATOR), tokens[10])
        self.assertEqual(Token('>', Location(1, 31, 30), Location(1, 32, 31), TokenKind.OPERATOR), tokens[12])
        self.assertEqual(Token(')', Location(1, 34, 33), Location(1, 35, 34), TokenKind.OPERATOR), tokens[14])
        self.assertEqual(Token('?', Location(1, 36, 35), Location(1, 37, 36), TokenKind.OPERATOR), tokens[15])
        self.assertEqual(Token('.', Location(1, 46, 45), Location(1, 47, 46), TokenKind.OPERATOR), tokens[19])
        self.assertEqual(Token('[', Location(1, 48, 47), Location(1, 49, 48), TokenKind.OPERATOR), tokens[21])
        self.assertEqual(Token(']', Location(1, 50, 49), Location(1, 51, 50), TokenKind.OPERATOR), tokens[23])
        self.assertEqual(Token(',', Location(1, 51, 50), Location(1, 52, 51), TokenKind.OPERATOR), tokens[24])
        self.assertEqual(Token('.*', Location(1, 57, 56), Location(1, 59, 58), TokenKind.OPERATOR), tokens[26])
        self.assertEqual(Token(':', Location(1, 62, 61), Location(1, 63, 62), TokenKind.OPERATOR), tokens[29])
        self.assertEqual(Token('->*', Location(1, 68, 67), Location(1, 71, 70), TokenKind.OPERATOR), tokens[31])
        self.assertEqual(Token('++', Location(1, 77, 76), Location(1, 79, 78), TokenKind.OPERATOR), tokens[34])

    def test_lexing_variadic_functions(self):
        code = '''void simple_printf(const char* fmt...) { }'''
        tokens = self.lexer.lexing(code)
        self.assertEqual(Token('...', Location(1, 35, 34), Location(1, 38, 37), TokenKind.OPERATOR), tokens[7])

    def test_lexing_string(self):
        code = 'char* x = "asdasd hihi"; string z = "\\"\\n\t innerString \\* \\"";'
        tokens = self.lexer.lexing(code)
        self.assertEqual(
            Token('"asdasd hihi"', Location(line=1, column=11, offset=10),
                  Location(line=1, column=24, offset=23), TokenKind.STRING),
            tokens[4])
        self.assertEqual(
            Token('"\\"\\n\t innerString \\* \\""', Location(line=1, column=37, offset=36),
                  Location(line=1, column=62, offset=61), TokenKind.STRING),
            tokens[9])

    def test_lexing_number(self):
        code = """
        double a = 12.;
        double b = .12;
        double c = 17.3;
        double d = 3.4028234e38;
        float e = 12.f;
        float f = .12f;
        float g = 17.3f;
        float h = 3.4028234e38f
        auto i = 3.4028234e38l;
        int d = 42;
        int o = 052;
        int x = 0x2a;
        int X = 0X2A;
        auto l0 = 42u;
        auto l1 = 42l;
        auto l2 = 42ll;
        auto l3 = 42ul;
        auto l4 = 18446744073709550592ull;
        """
        tokens = self.lexer.lexing(code)
        expected = {
            '12.': 3, '.12': 8, '17.3': 13, '3.4028234e38': 18, '12.f': 23,
            '.12f': 28, '17.3f': 33, '3.4028234e38f': 38, '3.4028234e38l': 42,
            '42': 47, '052': 52, '0x2a': 57, '0X2A': 62, '42u': 67, '42l': 72,
            '42ll': 77, '42ul': 82, '18446744073709550592ull': 87,
        }
        for k, v in expected.items():
            self.assertEqual(k, tokens[v].value)
            self.assertEqual(TokenKind.NUMBER, tokens[v].kind)

    def test_lexing_bool(self):
        # From the compiler point of view, true and false are both keywords instead of literals
        code = "bool a = true; bool b = false;"
        tokens = self.lexer.lexing(code)
        self.assertEqual(Token('true', Location(1, 10, 9), Location(1, 14, 13), TokenKind.KEYWORD), tokens[3])
        self.assertEqual(Token('false', Location(1, 25, 24), Location(1, 30, 29), TokenKind.KEYWORD), tokens[8])

    def test_lexing_char(self):
        code = "char a = '\\n'; char b = 'b';"
        tokens = self.lexer.lexing(code)
        self.assertEqual(Token("'\\n'", Location(1, 10, 9), Location(1, 14, 13), TokenKind.LITERAL), tokens[3])
        self.assertEqual(Token("'b'", Location(1, 25, 24), Location(1, 28, 27), TokenKind.LITERAL), tokens[8])
