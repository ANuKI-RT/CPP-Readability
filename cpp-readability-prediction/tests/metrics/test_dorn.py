import unittest

from code_processing.analyzer import CppCodeAnalyzer
from code_processing.lexer import CLangLexer, TokenKind
from code_processing.rse_lexer import RSELexer
from metrics import dorn


class TestCharactersAlignment(unittest.TestCase):
    def setUp(self):
        self.lexer = RSELexer(lexer=CLangLexer())
        self.code = """int main() {
            int a = 10;
            int b = 20;
            return 0;
        }"""

    def test_blocks_calculate_metric(self):
        fc = dorn.CharactersAlignmentBlocks(code=self.code, lexer=self.lexer)
        self.assertEqual(6., fc.calculate_metric())

    def test_extent_calculate_metric(self):
        fc = dorn.CharactersAlignmentExtent(code=self.code, lexer=self.lexer)
        self.assertEqual(7., fc.calculate_metric())


class TestVisualFeatureCalculator(unittest.TestCase):
    def setUp(self):
        self.lexer = RSELexer(lexer=CLangLexer())
        self.code = """int main() {
            int a = 10;
            /*
            Block comment
            */
            return 0;
        }"""

        self.code2 = """
        int main() {
            /*
            Block comment
            */
            int a = 0;
            int b = 1;
            if (a < b) {
                return foo.bar(a, b);
            }
            while (b < a)
                b = b * 2;
            return b;
        }"""

    def test_color_matrix(self):
        fc = dorn.VisualFeatureCalculator(code=self.code, lexer=self.lexer)
        color_matrix = fc.color_matrix
        self.assertEqual(7, len(color_matrix))
        self.assertEqual(26, len(color_matrix[0]))
        # int a = 10;
        self.assertEqual([3, 3, 3, 0, 1, 0, 4, 0, 7, 7, 4], color_matrix[1][12:23])
        # For block comments
        self.assertEqual([2, 2], color_matrix[2][12:14])
        self.assertEqual([2 for _ in range(26)], color_matrix[3])
        self.assertEqual([2, 2], color_matrix[4][12:14])

    def test_color_matrix2(self):
        fc = dorn.VisualFeatureCalculator(code=self.code2, lexer=self.lexer)
        color_matrix = [line[8:] for line in fc.color_matrix[1:]]
        self.assertEqual(color_matrix, [
            [3, 3, 3, 0, 1, 1, 1, 1, 4, 4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 3, 3, 0, 1, 0, 4, 0, 7, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 3, 3, 0, 1, 0, 4, 0, 7, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 3, 0, 4, 1, 0, 4, 0, 1, 4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 1, 1, 1, 4, 1, 1, 1, 4, 1, 4, 0, 1, 4, 4, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 4, 1, 0, 4, 0, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 4, 0, 1, 0, 4, 0, 7, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ])


class TestColorsAreas(unittest.TestCase):
    def setUp(self):
        self.lexer = RSELexer(lexer=CLangLexer())
        self.code = """int main() {}"""

    def test_calculate_metric(self):
        fc = dorn.ColorsAreas(kind=TokenKind.IDENTIFIER, code=self.code, lexer=self.lexer)
        # len('main') == 4
        self.assertEqual(4 / 13., fc.calculate_metric())


class TestColorsMutualAreas(unittest.TestCase):
    def setUp(self):
        self.lexer = RSELexer(lexer=CLangLexer())
        self.code = """int main() {}"""

    def test_calculate_metric(self):
        fc = dorn.ColorsMutualAreas(
            kind1=TokenKind.IDENTIFIER, kind2=TokenKind.KEYWORD,
            code=self.code, lexer=self.lexer
        )
        # len('main') == 4 and len('int') == 3
        self.assertEqual(4 / 3., fc.calculate_metric())


class TestDFTBandwidth(unittest.TestCase):
    def setUp(self):
        self.lexer = RSELexer(lexer=CLangLexer())
        self.code = """int main() {
            /*
            Block comment
            */
            int a = 0;
            int b = 1;
            if (a < b) {
                return foo.bar(a, b);
            }
            while (b < a)
                b = b * 2;
            return b;
        }"""
        self.fc = dorn.DFTBandwidth(
            kind=dorn.DFTBandwidth.ALL_KINDS[0], analyzer=CppCodeAnalyzer(),
            code=self.code, lexer=self.lexer
        )

    def test_calculate_bandwidth(self):
        self.assertEqual(4., dorn.DFTBandwidth.calculate_bandwidth([1, 2, 3, 4, 5]))

    def test_get_dft_amplitudes(self):
        self.assertEqual([1., 1., 1., 1.], dorn.DFTBandwidth.get_dft_amplitudes([0, 0, 1, 0]))

    def test_get_assignments(self):
        self.assertEqual([0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0], self.fc.get_assignments())

    def test_get_commas(self):
        self.assertEqual([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], self.fc.get_commas())

    def test_get_comments(self):
        self.assertEqual([0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], self.fc.get_comments())

    def test_get_indentations(self):
        self.assertEqual(
            [0.0, 12.0, 12.0, 12.0, 12.0, 16.0, 12.0, 12.0, 16.0, 12.0, 8.0],
            self.fc.get_indentations())

    def test_get_comparisons(self):
        self.assertEqual(
            [0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0],
            self.fc.get_comparisons())

    def test_get_ifs(self):
        self.assertEqual(
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            self.fc.get_ifs())

    def test_get_keywords(self):
        self.assertEqual(
            [1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0],
            self.fc.get_keywords())

    def test_get_line_lengths(self):
        self.assertEqual(
            [len(line) for line in self.code.splitlines(keepends=True)],
            self.fc.get_line_lengths())

    def test_get_loops(self):
        self.assertEqual(
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            self.fc.get_loops())

    def test_get_identifiers(self):
        self.assertEqual(
            [1.0, 0.0, 1.0, 1.0, 2.0, 4.0, 0.0, 2.0, 2.0, 1.0, 0.0],
            self.fc.get_identifiers())

    def test_get_numbers(self):
        self.assertEqual(
            [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            self.fc.get_numbers())

    def test_get_operators(self):
        self.assertEqual(
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            self.fc.get_operators())

    def test_get_parenthesis(self):
        self.assertEqual(
            [2.0, 0.0, 0.0, 0.0, 2.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            self.fc.get_parenthesis())

    def test_get_periods(self):
        self.assertEqual(
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            self.fc.get_periods())

    def test_get_spaces(self):
        self.assertEqual(
            [2.0, 0.0, 15.0, 15.0, 16.0, 18.0, 12.0, 15.0, 20.0, 13.0, 8.0],
            self.fc.get_spaces())

    def test_calculate_metric(self):
        self.assertEqual(10., self.fc.calculate_metric())
