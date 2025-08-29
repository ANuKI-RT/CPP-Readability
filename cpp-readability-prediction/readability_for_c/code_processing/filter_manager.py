import re
from typing import List

from nltk.corpus import stopwords

STOP_WORDS = stopwords.words('english')


def apply_non_word_filter(source_code: str) -> str:
    """
    Removes all non-word characters from the given string
    :param source_code: Source text
    :return: List of words separated by " "
    """
    only_words = workaround_non_word_filter(source_code)
    return re.sub('\\d', '', apply_multiple_spaces_filter(only_words))


def apply_multiple_spaces_filter(source_code: str) -> str:
    """
    Changes all multiple spaces in a single space.
    :param source_code: Source text
    :return: text filtered
    """
    return re.sub(' +(?= )', '', source_code)


def workaround_non_word_filter(source_code: str) -> str:
    result = ''
    for current in source_code:
        if current.isalnum() or current in ['_', ' ', '\n']:
            result += current
        else:
            result += " "
    return result


def delete_blank_lines(source_code: str) -> str:
    result = ''
    source = source_code.replace('\t', '')
    while len(source) != 0:
        if not source.startswith('\n'):
            try:
                index = source.index('\n') + 1
            except ValueError:
                index = len(source)  # Index of the word

            result += source[:index]  # Adds the part to the result
            source = source[index:]  # Erases the added part of the string
        else:
            source = source[1:]  # Erases the '\n'

    return result


def apply_stop_words_filter(words: List[str]) -> List[str]:
    return [w for w in words if w.strip().lower() not in STOP_WORDS]
