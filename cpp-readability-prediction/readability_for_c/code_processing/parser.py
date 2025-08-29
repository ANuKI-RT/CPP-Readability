import dataclasses
import tempfile
from typing import List

import clang


@dataclasses.dataclass
class Method:
    name: str
    content: str


class Parser:
    def parsing(self, code: str):
        raise NotImplementedError('Implement me')

    def extract_methods(self) -> List[str]:
        raise NotImplementedError('Implement me')

    @staticmethod
    def create_parser(language: str) -> "Parser":
        if 'cpp' == language:
            return ClangParser(clang_args=['-emit-cir'])
        raise ValueError(f'Not supported language: {language}')


class ClangParser(Parser):
    def __init__(self, clang_args: List[str] = None):
        self._root_node = None
        self._source_code = None
        self.clang_args = clang_args

    def parse(self, sourcefile_path: str):
        index = clang.cindex.Index.create()
        tu = index.parse(sourcefile_path, self.clang_args)
        self._root_node = tu.cursor
        return self._root_node

    def parsing(self, code: str):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp') as fp:
            fp.write(code)
            fp.flush()
            self.parse(fp.name)
            self._source_code = code

    def extract_methods(self) -> List[Method]:
        """
        Extract a list of method definitions in source code.

        :return: a list of method definitions.
        """
        methods: List[Method] = []
        for child in self._root_node.walk_preorder():
            # print child.kind, child.is_definition() # Added this
            if child.kind == clang.cindex.CursorKind.CXX_METHOD and child.is_definition():
                if self._root_node.extent.start.file.name != child.location.file.name:
                    # This case happens when Clang follows a file that was imported in the current file.
                    with open(child.location.file.name) as f:
                        content = f.read()
                else:
                    content = self._source_code
                method = content[child.extent.start.offset: child.extent.end.offset]
                methods.append(Method(child.spelling, method))
        return methods
