import unittest

from code_processing.analyzer import CppCodeAnalyzer
from code_processing.lexer import Token, TokenKind, Location, CLangLexer
from metrics import buse_weimer
from metrics.buse_weimer import Aggregation

CODE = """int main() {
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

ANALYZER = CppCodeAnalyzer()


class TestBuseWeimerFC(unittest.TestCase):
    def test_filter_tokens_by_predicate(self):
        tokens = [Token(
            value='', kind=kind, start_location=Location(1, 1, 0), end_location=Location(1, 1, 0)
        ) for kind in TokenKind]
        tokens = buse_weimer.BuseWeimerFC.filter_tokens_by_predicate(
            tokens, lambda token: token.kind == TokenKind.IDENTIFIER
        )
        self.assertEqual(1, len(tokens))


class TestAvgBlankLineBWFC(unittest.TestCase):
    def setUp(self):
        self.fc = buse_weimer.AvgBlankLineBWFC(code='', lexer=CLangLexer())

    def test_calculate_metric(self):
        code = """void main()
        {
            
            
            
        }"""
        self.fc.code = code
        # 3 blank lines / 6 total lines
        self.assertEqual(0.5, self.fc.calculate_metric())

    def test_calculate_metric2(self):
        fc = buse_weimer.AvgBlankLineBWFC(code=CODE, lexer=CLangLexer())
        # No blank line
        self.assertEqual(0., fc.calculate_metric())


class TestAvgCommentBWFC(unittest.TestCase):
    def setUp(self):
        self.fc = buse_weimer.AvgCommentBWFC(code='', lexer=CLangLexer())

    def test_calculate_metric(self):
        code = """void main()
        {
            /*
               Block comment
                Block comment
               asdasd   */
               /* Oh no block comment */
               /* Oh yes block comment
               */
            
               /*
               Oh yes block comment */
            
               //
               // We need to get any leading <? and <! elements:
               //
        }"""
        self.fc.code = code
        # 12 comment lines / 17 total lines
        self.assertEqual(12. / 17., self.fc.calculate_metric())


class TestMaxCharOccurrenceBWFC(unittest.TestCase):
    def setUp(self):
        self.fc = buse_weimer.MaxCharOccurrenceBWFC(code='', lexer=CLangLexer())

    def test_calculate_metric(self):
        code = """void main()
        {
           // We need to get any leading <? and <! elements:
           int a = b;
        }"""
        self.fc.code = code
        # e: 8
        self.assertEqual(52., self.fc.calculate_metric())

    def test_calculate_metric2(self):
        fc = buse_weimer.MaxCharOccurrenceBWFC(code=CODE, lexer=CLangLexer())
        self.assertEqual(75., fc.calculate_metric())


class TestMaxWordOccurrenceBWFC(unittest.TestCase):
    def setUp(self):
        self.fc = buse_weimer.MaxWordOccurrenceBWFC(code='', lexer=CLangLexer())

    def test_calculate_metric(self):
        code = """void main()
        {
            int b = 0;
            int a = b;
        }"""
        self.fc.code = code
        # Variable b: 2
        self.assertEqual(2., self.fc.calculate_metric())

    def test_calculate_metric2(self):
        fc = buse_weimer.MaxWordOccurrenceBWFC(code=CODE, lexer=CLangLexer())
        self.assertEqual(7., fc.calculate_metric())


class TestIdentifiersLengthBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            int b = 0;
            int a = b;
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.IdentifiersLengthBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        # total length(main, b, a, b) = 7 / 4 identifiers
        self.assertEqual(7. / 4., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.IdentifiersLengthBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        # max length(main, b, a, b) = 4
        self.assertEqual(4., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.IdentifiersLengthBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1.5, fc.calculate_metric())

    def test_max_calculate_metric2(self):
        fc = buse_weimer.IdentifiersLengthBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(4., fc.calculate_metric())


class TestAssignmentBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            int b = 0;
            int a = b;
            b += 1;
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.AssignmentBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        # 3 assignment lines / 6 lines
        self.assertEqual(.5, fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.AssignmentBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(1., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.AssignmentBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        # 3 assignment lines / 11 lines
        self.assertEqual(3 / 11., fc.calculate_metric())


class TestCommasBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            // a = 1, b = 2, c = 3
            foo(a, b, c);
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.CommasBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2. / 4., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.CommasBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.CommasBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        # 1 line has commas / 11 lines
        self.assertEqual(1 / 11., fc.calculate_metric())


class TestComparisonBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            return a == b ? 0 : -1; 
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.ComparisonBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2. / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.ComparisonBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(1., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.ComparisonBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        # 2 comparisons / 11 lines
        self.assertEqual(2 / 11., fc.calculate_metric())


class TestConditionBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            return a == b ? 0 : -1; 
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.ConditionBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(1. / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.ConditionBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(1., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.ConditionBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1 / 11., fc.calculate_metric())


class TestKeywordBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            for (int i=b; i<a; i++) {}
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.KeywordBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(5. / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.KeywordBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.KeywordBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(7 / 11., fc.calculate_metric())

    def test_max_calculate_metric2(self):
        fc = buse_weimer.KeywordBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1., fc.calculate_metric())


class TestIndentationBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
        
    
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.IndentationBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(28. / 5., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.IndentationBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(8., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.IndentationBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(4., fc.calculate_metric())

    def test_max_calculate_metric2(self):
        fc = buse_weimer.IndentationBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(8., fc.calculate_metric())


class TestLineLengthBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            for (int i=b; i<a; i++) {}
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.LineLengthBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(114 / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.LineLengthBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(38., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.LineLengthBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(143 / 11., fc.calculate_metric())

    def test_max_calculate_metric2(self):
        fc = buse_weimer.LineLengthBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(29., fc.calculate_metric())


class TestSpaceBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            for (int i=b; i<a; i++) {}
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.SpaceBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(66. / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.SpaceBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(17., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.SpaceBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(62 / 11., fc.calculate_metric())


class TestLoopBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            for (int i=b; i<a; i++) {}
            while (1) {}
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.LoopBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2. / 7., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.LoopBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(1., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.LoopBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1 / 11., fc.calculate_metric())


class TestNumberOfIdentifiersBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            int b = 0;
            int a = b;
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.NumberOfIdentifiersBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(4. / 5., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.NumberOfIdentifiersBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.NumberOfIdentifiersBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(14 / 11., fc.calculate_metric())

    def test_max_calculate_metric2(self):
        fc = buse_weimer.NumberOfIdentifiersBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(4., fc.calculate_metric())


class TestNumberBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return 1;
            for (int i=0; i<10; i++) {}
            while (1) {}
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.NumberBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(4. / 7., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.NumberBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.NumberBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(3 / 11., fc.calculate_metric())

    def test_max_calculate_metric2(self):
        fc = buse_weimer.NumberBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1., fc.calculate_metric())


class TestOperatorBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return a-b;
            a = a + b;
            return a == b ? a *b : a% b;
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.OperatorBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(4. / 7., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.OperatorBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.OperatorBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1 / 11., fc.calculate_metric())


class TestParenthesisBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            if (a > b)
                return a-b;
            return foo(bar(a),b);
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.ParenthesisBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(5. / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.ParenthesisBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.ParenthesisBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(6 / 11., fc.calculate_metric())


class TestPeriodBWFC(unittest.TestCase):
    def setUp(self):
        self.code = """void main()
        {
            Object a;
            Object b = a.getB();
            return a.getB().foo();
        }"""

    def test_avg_calculate_metric(self):
        fc = buse_weimer.PeriodBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(3. / 6., fc.calculate_metric())

    def test_max_calculate_metric(self):
        fc = buse_weimer.PeriodBWFC(
            aggregation=Aggregation.MAX, analyzer=ANALYZER, code=self.code, lexer=CLangLexer())
        self.assertEqual(2., fc.calculate_metric())

    def test_avg_calculate_metric2(self):
        fc = buse_weimer.PeriodBWFC(
            aggregation=Aggregation.AVG, analyzer=ANALYZER, code=CODE, lexer=CLangLexer())
        self.assertEqual(1 / 11., fc.calculate_metric())
