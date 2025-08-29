import unittest

from code_processing.analyzer import CppCodeAnalyzer, CodeAnalyzer

code = """int main(int someVar) {
    /*
    hallo
    allo    llo
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

comment_range_example = """int main(int someVar) {
    // It is a test for counting point sign in the middle. and in the end.
    //  syllables are counted by split [aeiou]
    /* it is a test for detecting star comments.**/
    /** The expected number for phrases is six.
    because of four points and one new line*/
}"""


class TestCodeAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = CodeAnalyzer()

    def test_get_identifier_words(self):
        self.assertEqual(['some', 'Var'], self.analyzer.get_identifier_words('someVar'))
        self.assertEqual(['Some', 'Var'], self.analyzer.get_identifier_words('SomeVar'))
        self.assertEqual(['some', 'var'], self.analyzer.get_identifier_words('some_var'))
        self.assertEqual(['var'], self.analyzer.get_identifier_words('var'))


class TestCppCodeAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = CppCodeAnalyzer()

    def test_get_identifiers_from_source(self):
        identifiers = self.analyzer.get_identifiers_from_source(code)
        self.assertEqual(['main', 'someVar', 'hallo', 'allo', 'llo', 'enable', 'someVar',
                          'x', 'printf', 'someVar', 'does', 'equal'],
                         identifiers[:12])

    def test_get_comments(self):
        comment = self.analyzer.get_comments(code)
        self.assertEqual("\n    hallo\n    allo    llo\n    *. ", comment)

    def test_workaround_get_comments_ranges(self):
        ranges = self.analyzer.workaround_get_comments_ranges(comment_range_example, False)
        self.assertEqual([
            [28, 98], [103, 145], [150, 196], [202, 290]
        ], ranges)
