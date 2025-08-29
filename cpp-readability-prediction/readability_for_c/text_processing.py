import re
import string
from typing import Tuple, List


def split_sentences_and_words(text: str) -> Tuple[List[str], List[str]]:
    """
    Extract sentences (phrases) and words from a string.
    A word is a series of alphabetical characters separated by a space or a punctuation symbol.
    A sentence (phrase) is a series of words that ends with a new-line symbol, or a strong punctuation point.

    :param text: input string
    :return: tuple of sentences and words
    """
    sentence_has_words = False
    sentences = []
    words = []
    for line in text.splitlines():
        sent = ''
        word = ''
        for c in line:
            if c.isspace() or c in string.punctuation:
                if word.strip() != '':
                    sentence_has_words = True
                    words.append(word.strip())
                word = ''
            else:
                word += c
            if c in ['.', '!', '?', ':', ';']:
                if sent.strip() != '' and sentence_has_words:
                    sentences.append(sent.strip())
                sent = ''
                sentence_has_words = False
            else:
                sent += c

        if word.strip() != '':
            sentence_has_words = True
            words.append(word.strip())

        if sent.strip() != '' and sentence_has_words:
            sentences.append(sent.strip())

    return sentences, words


def count_syllables(word: str) -> int:
    """
    Count the number of syllables in a word.
    A syllable is “a word or part of a word pronounced with a single, uninterrupted sounding of the voice
    consisting of a single sound of great sonority (usually a vowel) and
    generally one or more sounds of lesser sonority (usually consonants)

    :param word: input word
    :return: number of syllables
    """
    if len(word) <= 3:
        return 1
    word = word.lower()
    word = re.sub('(?:[^laeiouy]es|[^laeiouy]e)$', '', word)  # removed ed|
    word = re.sub('^y', '', word)
    matches = re.findall('[aeiouy]{1,2}', word)
    return max(1, len(matches))
