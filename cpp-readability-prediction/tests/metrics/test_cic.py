import unittest

from code_processing.analyzer import CppCodeAnalyzer
from metrics.cic import CommentsIdentifierConsistencyFC

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
    def test_cw_calculate_metric(self):
        fc = CommentsIdentifierConsistencyFC(
            analyzer=CppCodeAnalyzer(), use_synonyms=False, code=code)
        self.assertEqual(0.125, fc.calculate_metric())

    def test_scw_calculate_metric(self):
        # Due to the differences in the list of keywords and al library used for extracting synonyms,
        # there are huge differences between regular version and the synonym version.
        fc = CommentsIdentifierConsistencyFC(
            analyzer=CppCodeAnalyzer(), use_synonyms=True, code=code)
        self.assertEqual(0.0023094688221709007, fc.calculate_metric())
