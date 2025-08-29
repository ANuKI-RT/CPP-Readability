import unittest

from code_processing.analyzer import CppCodeAnalyzer
from metrics.itid_nm_nmi import get_all_feature_calculators

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
        printf("Access denied - You _must_ be at least 18 years old.\\n");
        printf("Error number: " + myNum);
    }
}"""


class TestItidNmNmiFc(unittest.TestCase):
    fc_list = get_all_feature_calculators(java_similar_example, CppCodeAnalyzer())

    def test_calculate_metric(self):
        # AVG ITID
        self.assertAlmostEqual(0.7607142857142858,
                               self.fc_list['Identifier Terms in Dictionary AVG'].calculate_metric())
        # MAX NM
        self.assertAlmostEqual(37., self.fc_list['Number of Meanings MAX'].calculate_metric())
        # AVG NMI
        self.assertAlmostEqual(11.714285714285714,
                               self.fc_list['Narrow Meaning Identifiers AVG'].calculate_metric())

        # Ignore 1-letter words
        # AVG ITID
        self.assertAlmostEqual(
            0.7205513784461153,
            self.fc_list['Identifier Terms in Dictionary AVG (Ignore 1-letter word)'].calculate_metric())
        # MAX NM
        self.assertAlmostEqual(
            32., self.fc_list['Number of Meanings MAX (Ignore 1-letter word)'].calculate_metric())
        # AVG NMI
        self.assertAlmostEqual(
            9.842105263157896,
            self.fc_list['Narrow Meaning Identifiers AVG (Ignore 1-letter word)'].calculate_metric())
