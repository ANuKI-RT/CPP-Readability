import unittest

from code_processing.analyzer import CppCodeAnalyzer
from metrics.cr import CommentsReadabilityFC

phrases_count_txt = """int main(int someVar) {
    // It is a test for counting point sign in the middle. and in the end.
    //  syllables are counted by split [aeiou]
    /* it is a test for detecting star comments.**/
    /** The expected number for phrases is six.
    because of four points and one new line*/
}"""

variable_4_txt = """static void var_dump( OBJECT * symbol, LIST * value, const char * what )
{
    out_printf( "%s %s = ", what, object_str( symbol ) );
    list_print( value );
    out_printf( "\n" );
}
"""


class TestCrFC(unittest.TestCase):
    fc = CommentsReadabilityFC(code=phrases_count_txt, analyzer=CppCodeAnalyzer())

    def test_calculate_metric(self):
        self.assertAlmostEqual(115.13, self.fc.calculate_metric())

    def test_calculate_metric_variable_4(self):
        fc = CommentsReadabilityFC(code=variable_4_txt, analyzer=CppCodeAnalyzer())
        self.assertEqual(0., fc.calculate_metric())
