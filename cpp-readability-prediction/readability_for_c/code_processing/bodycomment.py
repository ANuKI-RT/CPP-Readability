import re
from typing import List

import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('words')
nltk.download('stopwords')
nltk.download('wordnet')


# consider actor_4
def is_apostrophe_in_comment_or_string(text, apostrophe_idx):
    trace_start_idx = apostrophe_idx - 1
    if not is_string(apostrophe_idx, text):
        while text[trace_start_idx] != ';' and trace_start_idx >= 1:
            if (text[trace_start_idx - 1] == '/'
                    and
                    (text[trace_start_idx] == '*' or text[trace_start_idx] == '/')):
                return True
            trace_start_idx -= 1
        if text[trace_start_idx] == ';' or trace_start_idx == 0:
            return False
    else:
        return True


def is_string(sign_operator_index, input_text):
    while input_text.count("'") > 1 and input_text.index("'") < sign_operator_index:
        if not is_apostrophe_in_comment_or_string(input_text, input_text.index("'")):
            single_first_index = input_text.index("'")
            input_text = input_text[0:single_first_index] + ' ' + input_text[single_first_index + 1:]
            single_second_index = input_text.index("'")
            input_text = input_text[0:single_second_index] + ' ' + input_text[single_second_index + 1:]
            if single_first_index < sign_operator_index < single_second_index:
                return True
        else:
            input_text = input_text[:input_text.index("'")] + ' ' + input_text[input_text.index("'") + 1:]

    while input_text.count('"') > 1 and input_text.index('"') < sign_operator_index:
        if not is_string(input_text.index('"'), input_text):
            double_first_index = input_text.index('"')
            input_text = input_text[0:double_first_index] + ' ' + input_text[double_first_index + 1:]
            double_second_index = input_text.index('"')
            input_text = input_text[0:double_second_index] + ' ' + input_text[double_second_index + 1:]
            if double_first_index < sign_operator_index < double_second_index:
                return True
        else:
            input_text = input_text[:input_text.index('"')] + ' ' + input_text[input_text.index('"') + 1:]
    return False


def get_body_comment(source_code: str) -> List[str]:
    body_comment = []
    snippet = source_code
    pattern_star = r'\/\*((?:.|\n)*?)\*\/'
    pattern_slash = r'\/\/(.+?)(?:\r?\n|$)'
    pattern_star = re.compile(pattern_star)
    pattern_slash = re.compile(pattern_slash)
    star_matches = pattern_star.findall(snippet)
    slash_matches = pattern_slash.findall(snippet)
    star_comment_txt = snippet
    slash_comment_txt = snippet
    extracted_star_comment = []
    extracted_slash_comment = []
    comment_lines = ""
    star_matches = sorted(star_matches, key=len, reverse=True)
    for star_match in star_matches:
        star_comment_flag = True
        # consider async_tcp_echo_server_2.txt
        while star_comment_txt.count(star_match) > 0 and star_comment_flag:
            star_match_start_index = star_comment_txt.index(star_match) - 1
            star_match_end_index = star_comment_txt.index(star_match) + len(star_match)
            star_match_str = star_match

            while (star_comment_txt[star_match_start_index] == ' '
                   or star_comment_txt[star_match_start_index] == '*'):
                star_match_str = star_comment_txt[star_match_start_index] + star_match_str
                star_match_start_index -= 1

            while star_comment_txt[star_match_end_index] == ' ' or star_comment_txt[star_match_end_index] == '*':
                star_match_str = star_match_str + star_comment_txt[star_match_end_index]
                star_match_end_index += 1

            if star_comment_txt[star_match_end_index] == '/' and star_comment_txt[star_match_start_index] == '/':
                star_match_str = '/' + star_match_str + '/'
                # There must be a string check for comments
                # consider 'snippets_cppcheck-2.12.0\cmdlineparser_26_split.txt'.
                # The following code is related to method arguments in the form of comment which should not been removed
                # also string comments
                star_start_index = star_comment_txt.index(star_match_str)
                star_end_index = 0
                while (not star_comment_txt[star_start_index] == '(') and star_start_index > 0:
                    star_start_index = star_start_index - 1
                if star_comment_txt[star_start_index] == '(':
                    star_end_index = star_start_index
                    while not star_comment_txt[star_end_index] == ')' and star_end_index < len(star_comment_txt):
                        star_end_index = star_end_index + 1

                star_match_str_index = star_comment_txt.index(star_match_str)
                starting_star_index = star_match_str_index
                ending_star_index = starting_star_index + len(star_match_str) - 1
                if (not star_end_index > star_match_str_index and
                        not is_string(snippet.index(star_match_str), snippet)):
                    extracted_star_comment.append([starting_star_index, ending_star_index, len(star_match_str)])
                    while (star_comment_txt[starting_star_index] == '/' or
                           star_comment_txt[starting_star_index] == '*' or
                           star_comment_txt[starting_star_index] == ' ' or
                           star_comment_txt[starting_star_index] == '\n'):
                        starting_star_index += 1
                    while (star_comment_txt[ending_star_index] == '/' or
                           star_comment_txt[ending_star_index] == '*' or
                           star_comment_txt[ending_star_index] == ' ' or
                           star_comment_txt[ending_star_index] == '\n'):
                        ending_star_index -= 1
                    star_match = star_comment_txt[starting_star_index:ending_star_index + 1]
                    comment_lines = star_match + '\n' + comment_lines
                    star_comment_flag = False
            space_string = ''
            space_count = 0
            while space_count < len(star_match_str):
                space_string += ' '
                space_count += 1
            star_comment_txt = (star_comment_txt[:star_comment_txt.index(star_match_str)] +
                                space_string +
                                star_comment_txt[
                                star_comment_txt.index(star_match_str) + len(star_match_str):])

    slash_matches = sorted(slash_matches, key=len, reverse=True)
    for slash_match in slash_matches:
        slash_comment_flag = True
        while slash_comment_txt.count(slash_match) > 0 and slash_comment_flag:
            slash_match_index = slash_comment_txt.index(slash_match) - 1
            slash_match_str = slash_match
            while slash_comment_txt[slash_match_index] == ' ':
                slash_match_str = slash_comment_txt[slash_match_index] + slash_match_str
                slash_match_index -= 1

            if slash_comment_txt[slash_match_index] == '/' and slash_comment_txt[slash_match_index - 1] == '/':
                slash_match_str = '//' + slash_match_str
                slash_start_index = slash_comment_txt.index(slash_match_str)
                slash_end_index = 0
                # The following code is related to method arguments in the form of comment which should not been removed
                while not slash_comment_txt[slash_start_index] == '(' and slash_start_index >= 0:
                    slash_start_index = slash_start_index - 1
                if slash_comment_txt[slash_start_index] == '(':
                    slash_end_index = slash_start_index
                    while (not slash_comment_txt[slash_end_index] == ')' and
                           slash_end_index < len(slash_comment_txt)):
                        slash_end_index = slash_end_index + 1
                slash_match_index = slash_comment_txt.index(slash_match_str)
                if (not slash_end_index > slash_match_index and
                        not is_string(snippet.index(slash_match_str), snippet)):
                    extracted_slash_comment.append([slash_comment_txt.index(slash_match_str),
                                                    slash_comment_txt.index(slash_match_str) +
                                                    len(slash_match_str) - 1,
                                                    len(slash_match_str)])
                    comment_lines = slash_match + '\n' + comment_lines
                    slash_comment_flag = False
            space_string = ''
            space_count = 0
            while space_count < len(slash_match_str):
                space_string += ' '
                space_count += 1
            slash_comment_txt = (slash_comment_txt[:slash_comment_txt.index(slash_match_str)] + space_string +
                                 slash_comment_txt[slash_comment_txt.index(slash_match_str) + len(slash_match_str):])

    # when there is no blank line in the start of method re could not detect keyword placed at the start of sentence
    for item in extracted_star_comment:
        space_string = ''
        space_count = 0
        while space_count < item[2]:
            space_string += ' '
            space_count += 1
        snippet = snippet[0:item[0]] + space_string + snippet[item[1] + 1:]
    for item in extracted_slash_comment:
        space_string = ''
        space_count = 0
        while space_count < item[2]:
            space_string += ' '
            space_count += 1
        snippet = snippet[0:item[0]] + space_string + snippet[item[1] + 1:]
    snippet = '\n' + snippet
    body_comment.append(snippet)
    body_comment.append(comment_lines)
    return body_comment


def get_body_and_inline_comment(source_code: str) -> List[str]:
    snippet = source_code
    snippet_lines = snippet.split('\n')
    method_body_lines = \
        [item for item in get_body_comment(source_code)[0].split('\n') if not re.match(r'^\s*$', item)]
    method_declaration_start_line = 0
    for snippet_line in snippet_lines:
        if snippet_line.startswith(method_body_lines[0]):
            method_declaration_start_line = snippet_lines.index(snippet_line)
    body_and_inline_comments_list = []
    iterate_index = method_declaration_start_line
    while iterate_index < len(snippet_lines):
        if not re.match(r'^\s*$', snippet_lines[iterate_index]):
            body_and_inline_comments_list.append(snippet_lines[iterate_index])
        iterate_index = iterate_index + 1
    body_and_inline_comments_str = ''
    for item in body_and_inline_comments_list:
        body_and_inline_comments_str = body_and_inline_comments_str + '\n' + item
    return body_and_inline_comments_str


def is_english_word(token):
    if token in nltk.corpus.words.words() or len(wn.synsets(token)) > 0:
        return True
    else:
        return False


def convert_camel_case(str_camel_case):
    letter_index = 0
    str_list = list(str_camel_case)
    while letter_index < len(str_list) - 1:
        if str_list[letter_index].isupper() and str_list[letter_index + 1].islower():
            str_list[letter_index] = str_list[letter_index].lower()
            if str_list[letter_index - 1].islower():
                str_list.insert(letter_index, ' ')
        letter_index = letter_index + 1
    new_str = ''
    for letter in str_list:
        new_str = new_str + letter
    str_separated = new_str
    return str_separated


def get_cpp_keywords() -> List[str]:
    """
    Get list cpp keywords (https://en.cppreference.com/w/cpp/keyword)

    :return: List of cpp keywords
    """
    cpp_keywords = ['alignas', 'alignof', 'and', 'and_eq', 'asm', 'atomic_cancel', 'atomic_commit',
                    'atomic_noexcept', 'auto', 'bitand', 'bitor', 'bool', 'break', 'case', 'catch', 'char',
                    'char8_t', 'char16_t', 'char32_t', 'class', 'compl', 'concept', 'const', 'consteval',
                    'constexpr', 'constinit', 'const_cast', 'continue', 'co_await', 'co_return', 'co_yield',
                    'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit',
                    'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if', 'inline', 'int', 'long',
                    'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr', 'operator', 'or',
                    'or_eq', 'private', 'protected', 'public', 'reflexpr', 'register', 'reinterpret_cast',
                    'requires', 'return', 'short', 'signed', 'sizeof', 'static', 'static_assert', 'static_cast',
                    'struct', 'switch', 'synchronized', 'template', 'this', 'thread_local', 'throw', 'true',
                    'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void',
                    'volatile', 'wchar_t', 'while', 'xor', 'xor_eq', 'if', 'elif', 'else', 'endif', 'ifdef', 'ifndef',
                    'elifdef', 'elifndef']
    return cpp_keywords


# Find the Part Of Speech role of a word
# The function is required because existing methods of library define POS tag of a token in a sentence
# While there is no actual sentence in method body that negatively effects on those APIs' accuracy
def get_pos(word):
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    syn_list = wn.synsets(word)
    possible_pos_tags = set()
    for ss_ in syn_list:
        for lemma_ in ss_.lemma_names():
            # synonyms are base form of verbs and single form of nouns
            if (word == lemma_.lower() or lemmatizer.lemmatize(word, "v") == lemma_.lower() or
                    lemmatizer.lemmatize(word, "n") == lemma_.lower()):
                possible_pos_tags.add(ss_.pos())
                break
    if len(possible_pos_tags) == 0:
        for ss_ in syn_list:
            for lemma_ in ss_.lemma_names():
                if stemmer.stem(word) == lemma_.lower():
                    possible_pos_tags.add(ss_.pos())
                    break
    return possible_pos_tags


def get_base_form(words_list):
    lemmatizer = WordNetLemmatizer()
    words_list_base = list(words_list)
    base_form_list = list()
    removing_list = list()
    for word in words_list_base:
        base_form_set = set()
        removing_set = set()
        pos_list = get_pos(word)
        if 'v' in pos_list:
            if len(pos_list) == 1:
                words_list_base[words_list_base.index(word)] = lemmatizer.lemmatize(word, "v")
            elif not word == lemmatizer.lemmatize(word, "v"):
                removing_set.add(word)
                base_form_set.add(lemmatizer.lemmatize(word, "v"))
        if 'n' in pos_list:
            if len(pos_list) == 1:
                words_list_base[words_list_base.index(word)] = lemmatizer.lemmatize(word, "n")
            elif not word == lemmatizer.lemmatize(word, "n"):
                removing_set.add(word)
                base_form_set.add(lemmatizer.lemmatize(word, "n"))
        for base_form_item in base_form_set:
            base_form_list.append(base_form_item)
        for removing_item in removing_set:
            removing_list.append(removing_item)

    for removing_item in removing_list:
        words_list_base.remove(removing_item)
    for base_form in base_form_list:
        words_list_base.append(base_form)
    return words_list_base
