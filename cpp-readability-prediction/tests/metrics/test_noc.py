import unittest

from code_processing.analyzer import CppCodeAnalyzer
from metrics.noc import NumberOfConceptsFC

code = """int main(int someVar) {
    /*
    'enable' must be true. Otherwise, skip computation.
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


class TestSemanticTextCoherenceFC(unittest.TestCase):
    fc = NumberOfConceptsFC(analyzer=CppCodeAnalyzer(), code=code, lexer=None)

    def test_calculate_metric(self):
        # NOC
        fc = NumberOfConceptsFC(analyzer=CppCodeAnalyzer(), code=code)
        self.assertAlmostEqual(2., fc.calculate_metric())

        # NOC norm
        fc = NumberOfConceptsFC(analyzer=CppCodeAnalyzer(), code=code, eps=0.3, normalized=True)
        self.assertAlmostEqual(0.2857142857142857, fc.calculate_metric())
