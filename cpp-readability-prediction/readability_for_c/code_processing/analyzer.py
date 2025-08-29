import re
from typing import List

from code_processing import filter_manager, bodycomment


class CodeAnalyzer:
    def delete_comments(self, code: str) -> str:
        raise NotImplementedError()

    def delete_inline_comments(self, code: str) -> str:
        raise NotImplementedError()

    def get_identifiers_from_source(self, source_code: str) -> List[str]:
        raise NotImplementedError()

    def get_comments(self, source_code: str) -> str:
        raise NotImplementedError()

    @staticmethod
    def get_identifier_words(identifier: str) -> List[str]:
        """
        Split camel case or snake case identifier name into separate words.
        :param identifier: The identifier name.
        :return: list of words that form the identifier name.
        """
        result = re.sub(
            '(?<=[A-Z])(?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z])|(?<=[A-Za-z])(?=[^A-Za-z])',
            ' ',
            identifier
        ).replace('_', ' ')

        return (re.sub(' +(?= )', '', result)
                .replace('\n', '')
                .split(' '))

    @staticmethod
    def create_analyzer(language: str) -> "CodeAnalyzer":
        if 'cpp' == language:
            return CppCodeAnalyzer()
        raise ValueError(f'Not supported language: {language}')


class CppCodeAnalyzer(CodeAnalyzer):
    def delete_comments(self, code: str) -> str:
        return self.workaround_remove_comments(self.delete_inline_comments(code))

    def delete_inline_comments(self, code: str) -> str:
        return re.sub(r'(?://[^\n]*\n)', '', code)

    def get_identifiers_from_source(self, source_code: str) -> List[str]:
        keywords = bodycomment.get_cpp_keywords()
        words = (filter_manager
                 .apply_non_word_filter(source_code)
                 .replace('\n', '')
                 .split(' '))
        return [word.strip() for word in words if word.strip() != '' and word.strip() not in keywords]

    def get_comments(self, source_code: str) -> str:
        consider = self.workaround_get_comments_ranges(source_code, False)
        result = ''
        for comment_range in consider:
            substring = source_code[comment_range[0] + 2: comment_range[1]]
            result += substring + '. '
        return result

    @classmethod
    def workaround_remove_comments(cls, code: str) -> str:
        ignores = cls.workaround_get_comments_ranges(code, True)
        if len(ignores) == 0:
            return code

        current_ignore = 0
        result = ''

        for i in range(len(code)):
            if current_ignore == len(ignores):
                current_range = [len(code), len(code) + 1]
            else:
                current_range = ignores[current_ignore]
            if i < current_range[0]:
                result += code[i]
            elif i == current_range[1]:
                current_ignore += 1

        return result

    @staticmethod
    def workaround_get_comments_ranges(code: str, multiline_only: bool) -> List[List[int]]:
        # State list:
        # 0: Normal code
        # 1: "/" found
        # 2: "/*" found( in comment)
        # 3: "*" found(maybe exit)
        start_comment = 0
        state = 0
        ignores = []

        for i in range(len(code)):
            current = code[i]
            if 0 == state:
                if current == '/':
                    state = 1
            elif 1 == state:
                if current == '*':
                    state = 2
                    start_comment = i - 1
                elif not multiline_only and current == '/':
                    state = 4
                    start_comment = i - 1
                else:
                    state = 0
            elif 2 == state:
                if current == '*':
                    state = 3
            elif 3 == state:
                if current == '/':
                    ignores.append([start_comment, i])
                    state = 0
                elif current != '*':
                    state = 2
            elif 4 == state:
                if current == '\n':
                    ignores.append([start_comment, i])
                    state = 0

        return ignores
