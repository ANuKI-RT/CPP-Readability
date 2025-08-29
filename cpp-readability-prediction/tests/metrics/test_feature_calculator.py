import unittest

from code_processing.analyzer import CppCodeAnalyzer
from metrics.feature_calculator import TextualFC

code = """int main(int someVar) {
    /*
    'enable' _must_ be true. Otherwise, skip computation.
    Depending on the value of someVar, respective text will be displayed.
    */
    if(enable)
    {
       if (someVar != 0x00)
       {
	       printf("someVar does not equal 0x00");
       }
       else if (someVar == 0x01)

           printf("someVar may equal 0x00");

       else
       {
          printf("someVar is equal 0x00");
       }
    }
}"""


class TestCommentsIdentifierConsistencyFC(unittest.TestCase):
    def setUp(self):
        self.fc = TextualFC(code='', analyzer=CppCodeAnalyzer())

    def test_extract_comment_terms(self):
        terms = self.fc.extract_comment_terms(code)
        self.assertEqual({
            'enabl', 'must', 'otherwis', 'skip', 'comput', 'depend', 'valu', 'var', 'respect', 'text', 'display'
        }, terms)

    def test_extract_identifier_terms(self):
        terms = self.fc.extract_identifier_terms(code)
        self.assertEqual({
            'main', 'var', 'enable', 'printf', 'equal', 'x', 'may'
        }, terms)

    def test_extract_lines_identifier_terms(self):
        lines_terms = self.fc.extract_lines_identifier_terms(code)
        self.assertEqual([
            {'main', 'var'}, {'enable'}, set(), {'var', 'x'}, set(), {'equal', 'printf', 'var', 'x'}, set(),
            {'var', 'x'}, {'equal', 'may', 'printf', 'var', 'x'}, set(), set(),
            {'equal', 'printf', 'var', 'x'}, set(), set(), set()
        ], lines_terms)

    def test_convert_to_stems(self):
        terms = self.fc.convert_to_stems({
            'enable', 'must', 'true', 'otherwise', 'skip', 'computation',
            'depending', 'value', 'var', 'respective', 'text', 'displayed'
        })
        self.assertEqual({
            'enabl', 'must', 'true', 'otherwis', 'skip', 'comput', 'depend', 'valu', 'var', 'respect', 'text', 'display'
        }, terms)
