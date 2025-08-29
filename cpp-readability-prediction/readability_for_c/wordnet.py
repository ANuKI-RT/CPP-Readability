from typing import Optional, List, Tuple

from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

_wln = WordNetLemmatizer()


def get_best_pos(word: str) -> Optional[Tuple[str, str]]:
    """
    Get the POS tag that has the most number of senses (idea from RiTa lib).
    :param word: word that its POS tag is needed
    :return: POS tag of the input word
    """
    normalized_word = word.strip().lower()
    synsets = wn.synsets(normalized_word)
    if len(synsets) == 0:
        normalized_word = _trim_non_letter(word).lower()
        synsets = wn.synsets(normalized_word)

    if len(synsets) == 0:
        return None

    pos_synsets_counter = {}
    for ss in synsets:
        pos = ss.pos()
        if pos not in pos_synsets_counter:
            pos_synsets_counter[pos] = 0
        pos_synsets_counter[pos] += 1

    pos = max(pos_synsets_counter.keys(), key=lambda p: pos_synsets_counter[p])
    return pos, normalized_word


def get_stem(word: str) -> Optional[str]:
    pos_result = get_best_pos(word.lower())
    if pos_result is None:
        return None
    pos, normalized_word = pos_result
    return _wln.lemmatize(normalized_word, pos)


def get_synonyms(word: str) -> List[str]:
    """
    Get list of synonyms based on the 'best' POS tag of this word.
    Synonyms set is the union of:

    - lemma names of the 1st synset of a word.
    - lemma names of all hypernyms of the 1st synset of a word.
    - lemma names of all similar synsets of the 1st synset of a word.
    - lemma names of all also-see synsets of the 1st synset of a word.
    - lemma names of all hyponyms of all  hypernyms of the 1st synset of a word (coordinate synsets).

    (Reference from RiTa library)

    :param word: input word
    :return: list of synonyms
    """
    pos_result = get_best_pos(word)
    if pos_result is None:
        return []
    pos, normalized_word = pos_result
    synset = wn.synsets(normalized_word, pos)[0]
    hypernyms = synset.hypernyms()
    result = [ln for ln in synset.lemma_names() if ln != word]
    result += [ln for hypernym in hypernyms for ln in hypernym.lemma_names() if ln != word]
    result += [ln for similar in synset.similar_tos() for ln in similar.lemma_names() if ln != word]
    result += [ln for also_sees in synset.also_sees() for ln in also_sees.lemma_names() if ln != word]
    result += [ln for hypernym in hypernyms for hyponym in hypernym.hyponyms()
               for ln in hyponym.lemma_names() if ln != word]
    return list(set(result))


def _trim_non_letter(word: str) -> str:
    start = 0
    end = len(word)
    for i in range(len(word)):
        if word[i].isalpha():
            start = i
            break
    for i in range(len(word) - 1, -1, -1):
        if word[i].isalpha():
            end = i + 1
            break
    return word[start:end]


def get_hypernyms(word: str, pos: str) -> List[str]:
    synset = next(iter(wn.synsets(word.lower(), pos)), None)
    if not synset:
        return []
    return [n for hypernym in synset.hypernyms() for n in hypernym.lemma_names()]


def get_distance_to_root_hypernym(word: str, pos: str) -> float:
    synset = next(iter(wn.synsets(word.strip().lower(), pos)), None)
    if synset is None:
        return -1.
    return float(synset.shortest_path_distance(synset.root_hypernyms()[0]))


def get_number_of_meanings(word: str, pos: str) -> int:
    return len(wn.synsets(word.strip().lower(), pos))
