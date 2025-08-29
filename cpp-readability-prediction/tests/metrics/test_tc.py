import unittest

from code_processing.analyzer import CppCodeAnalyzer
from code_processing.lexer import CLangLexer
from metrics.tc import TextualCoherenceFC

minimal_example = """void minimal_example(uint32_t       someVar, ///< [in] default parameter <-- BAD
                     bool           enable)
{
    #if defined ARRAY_SIZE
    #define TABLE_SIZE ARRAY_SIZE
    #elif !defined BUFFER_SIZE
    int table[300];
    #else
    #endif

    #ifndef TABLE_SIZE
    int table[200];
    #endif

    #ifdef TABLE_SIZE
    int table[TABLE_SIZE];
    #else
    int table[100];
    #endif

    printf(sizeof(table));

    if(enable)
    {
       if (someVar != 0x00)
       {
	       printf("someVar does not equal 0x00");
       }
       else
       {
          printf("someVar is equal 0x00");
       }
    }
    
    vector<int> v {4, 1, 3, 5, 2, 3, 1, 7};
    sort(v.begin(), v.end(), [](const int& a, const int& b) -> bool
    {
        return a > b;
    });
}"""

java_similar_example = """int main(int someVar) {
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

    for (int i=0; i<5; i++) {
        printf("test loop with bracket");
        for (int j=0; j<5; j++)
            printf("test loop w/o bracket");
    }

    int a[5] = {10, 20, 30, 40, 50};
    for(int x : a){
        printf("test for-range loop");
    }

    int i = 0;
    while (i < 5) {
      i++;
    }

    do {
      i++;
    }
    while (i < 5);

    int day = 4;
    switch (day) {
      case 1: {
        printf("Monday");
        break;
      }
      case 6:
        printf("Saturday");
        printf("Saturday");
        break;
      default:
        printf("Sunday");
        break;
    }

    try {
        throw 505;
    }
    catch (int myNum) {
        printf("Access denied - You must be at least 18 years old.\\n");
        printf("Error number: " + myNum);
    }
}"""

single_block_example = '''int main() {
    printf("Hello World");
}'''


class TestTextualCoherenceFC(unittest.TestCase):
    def test_calculate_metric_minimal_example(self):
        fc = TextualCoherenceFC(
            TextualCoherenceFC.AGGREGATIONS[1],
            lexer=CLangLexer(),
            analyzer=CppCodeAnalyzer(),
            code=minimal_example,
        )
        self.assertEqual(9, len(fc.documents))
        self.assertAlmostEqual(0.3048576037264699, fc.calculate_metric())

    def test_calculate_metric_java_similar_example(self):
        fc = TextualCoherenceFC(
            TextualCoherenceFC.AGGREGATIONS[1],  # avg
            lexer=CLangLexer(),
            analyzer=CppCodeAnalyzer(),
            code=java_similar_example,
        )
        self.assertEqual(12, len(fc.documents))
        self.assertEqual(27, len(fc.dictionary))
        self.assertAlmostEqual(0.22778300077075767, fc.calculate_metric())

    def test_calculate_single_block_example(self):
        fc = TextualCoherenceFC(
            TextualCoherenceFC.AGGREGATIONS[1],  # avg
            lexer=CLangLexer(),
            analyzer=CppCodeAnalyzer(),
            code=single_block_example,
        )
        self.assertEqual(1, len(fc.documents))
        self.assertAlmostEqual(0., fc.calculate_metric())
