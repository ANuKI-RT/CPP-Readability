import os
import unittest

import clang
from clang.cindex import Config

from code_processing.parser import ClangParser

example = """class Foo
{
    public:
        Foo();

    void bar(int input);

    void another(int input, double & output);
};

void Foo::bar(int input)
{
  input += 1;
}

void Foo::another(int input, double & output)
{
  input += 1;
  output = input * 1.2345;
}"""

CLANG_LIB_PATH = os.path.join(os.path.dirname(os.path.realpath(clang.__file__)), 'native')
Config.set_library_path(CLANG_LIB_PATH)


class TestClangParser(unittest.TestCase):
    def setUp(self):
        self.parser = ClangParser(clang_args=['-x', 'c++'])
        self.parser.parsing(example)

    def test_extract_methods(self):
        methods = self.parser.extract_methods()
        self.assertEqual(2, len(methods), "There must be 2 methods")
        self.assertEqual('another', methods[1].name, "There must be 2 methods")
