import unittest

from code_processing.lexer import CLangLexer
from code_processing.rse_lexer import RSELexer
from metrics import posnett
from metrics.posnett import PosnettLexer


class TestPosnettLexer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexer: PosnettLexer = posnett.PosnettLexer(RSELexer(CLangLexer()))

    def test_lexing_without_string_and_literal(self):
        code = 'bool a = true; std::cout<<(!(this->count - 1 > 0) ? foo(this.x[0], this.*y) : this->*count)++;'
        tokens = self.lexer.lexing(code)
        self.assertEqual(31, self.lexer.vocab_size)
        self.assertEqual(41, self.lexer.program_length)

    def test_lexing_with_literal(self):
        code = "char c = '\\n'; char d = 'a';"
        self.lexer.lexing(code)
        self.assertEqual(7, self.lexer.vocab_size)
        self.assertEqual(10, self.lexer.program_length)

    def test_lexing_with_string(self):
        code = 'char* x = "asdasd hihi"; string z = "\\"\\n\t innerString \\* \\"";'
        self.lexer.lexing(code)
        self.assertEqual(9, self.lexer.vocab_size)
        self.assertEqual(11, self.lexer.program_length)

        code = 'string y = MessageFormat.format("{0} {1}", "hallo", "servus");'
        self.lexer.lexing(code)
        self.assertEqual(13, self.lexer.vocab_size)
        self.assertEqual(14, self.lexer.program_length)

        code = 'string x = "asdasd	hihi";'
        self.lexer.lexing(code)
        self.assertEqual(5, self.lexer.vocab_size)
        self.assertEqual(5, self.lexer.program_length)


lines_test_txt = """// outer comments are included.
if (i >= argc || argv[i][0] == '-') {
// CamelCase test: printError number 1
/*
the new line
*/

   printError("argument to '-i' is missing.");

   return false;
}"""

rules_22_txt = """settings_ptr addsettings( settings_ptr head, int flag, object_ptr symbol,
    list_ptr value )
{
    settings_ptr v;

    /* Look for previous settings. */
    for ( v = head; v; v = v->next )
        if ( object_equal( v->symbol, symbol ) )
            break;

    /* If not previously set, alloc a new. */
    /* If appending, do so. */
    /* Else free old and set new. */
    if ( !v )
    {
        v = settings_freelist;
        if ( v )
            settings_freelist = v->next;
        else
            v = (settings_ptr)BJAM_MALLOC( sizeof( *v ) );

        v->symbol = object_copy( symbol );
        v->value = value;
        v->next = head;
        head = v;
    }
    else if ( flag == VAR_APPEND )
    {
        v->value = list_append( v->value, value );
    }
    else if ( flag != VAR_DEFAULT )
    {
        list_free( v->value );
        v->value = value;
    }
    else
        list_free( value );

    /* Return (new) head of list. */
    return head;
}
"""


class TestPosnettLinesFC(unittest.TestCase):
    def test_number_of_lines(self):
        fc = posnett.PosnettLinesFC(code=lines_test_txt, lexer=None)
        self.assertEqual(11., fc.calculate_metric())

    def test_number_of_lines_top_100(self):
        fc = posnett.PosnettLinesFC(code=rules_22_txt, lexer=None)
        self.assertEqual(42., fc.calculate_metric())


entropy_test_txt = """  Message wait()
  {
    /* syllables are are counted by split [aeiou]. not non EWs same Rados and Ceph**/
    std::unique_lock<std::mutex> lock(mutex_);
  }"""

checkunusedvar_2_txt = """        /** variable is used.. set both read+write */
        void use() {
            _read = true;
            _write = true;
        }
"""


class TestPosnettEntropyFC(unittest.TestCase):
    def test_calculate_metric_entropy_test(self):
        fc = posnett.PosnettEntropyFC(code=entropy_test_txt, lexer=None)
        self.assertEqual(3.2371539371888245, fc.calculate_metric())
        # self.assertEqual({32: 30, 77: 1, 101: 12, 115: 10, 97: 9, 103: 1, 119: 1,
        #                   105: 4, 116: 8, 40: 2, 41: 2, 10: 4, 123: 1, 47: 2, 42: 3,
        #                   121: 2, 108: 6, 98: 2, 114: 2, 99: 3, 111: 7, 117: 6, 110: 6,
        #                   100: 5, 112: 2, 91: 1, 93: 1, 46: 1, 69: 1, 87: 1, 109: 3, 82: 1,
        #                   67: 1, 104: 1, 58: 4, 113: 1, 95: 2, 107: 2, 60: 1, 120: 2, 62: 1, 59: 1, 125: 1},
        #                  fc.snippet_bytes_dict)

    def test_calculate_metric_checkunusedvar_2(self):
        fc = posnett.PosnettEntropyFC(code=checkunusedvar_2_txt, lexer=None)
        self.assertEqual(2.375017021957129, fc.calculate_metric())
        # self.assertEqual({32: 61, 47: 2, 42: 3, 118: 2, 97: 4, 114: 7, 105: 5, 98: 2, 108: 1, 101: 10,
        #                   115: 4, 117: 4, 100: 4, 46: 2, 116: 6, 111: 2, 104: 1, 43: 1, 119: 2, 10: 5,
        #                   40: 1, 41: 1, 123: 1, 95: 2, 61: 2, 59: 2, 125: 1},
        #                  fc.snippet_bytes_dict)


volume_test_code = '''int main(string args[]) {
    int a = 12;
    a += 1;
    a = !(a >= 0) ? a * 10 : a + 10;
    char c = \'\\n\';
    double e = 17.3;
    bool f = true;
    string x = "asdasd	hihi";
    string y = MessageFormat.format("{0} {1}", "hallo", "servus");
    string z = "\\"\\n\t innerString \\* \\"";
    
    if (args.length != 1) {
        System.out.println("Use these arguments: [1] snippet path");
        System.exit(-1);
        return;
    }
    
    for (FeatureCalculator featureCalculator : metrics) {
        featureCalculator.setSource(snippetContent);
        System.out.println(featureCalculator.getName() + ": " + featureCalculator.calculate());
    }
}'''


class TestPosnettVolumeFC(unittest.TestCase):
    def test_calculate_metric(self):
        fc = posnett.PosnettVolumeFC(code=volume_test_code, lexer=PosnettLexer(RSELexer(CLangLexer())))
        self.assertEqual(64, fc.vocab_size)
        self.assertEqual(141, fc.program_length)
        self.assertEqual(846.0, fc.calculate_metric())
