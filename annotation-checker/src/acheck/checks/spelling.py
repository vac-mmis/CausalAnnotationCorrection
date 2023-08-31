import re
from typing import List, Dict
import difflib

from collections import Counter
from acheck.config import config
from acheck.checking.check_interface import Check, ToolObjectsMeta, CheckGroup
from acheck.checking.error import Error, ErrorType, Sequence, Fix, FixCode, ErrorLevel
from acheck.utils.annotationhelper import parse_annotation
import logging

logger = logging.getLogger(__name__)



class SpellCheck(Check):
    """Checks whether the given annotation has spelling mistakes

    :Options:
        - language:
            Supported languages if installed correctly: en_US, en_GB, de_DE
    """

    language = config.load("Annotation","lang")

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()
        try:
            import enchant.checker
        except Exception:
            self.logs.append(f"An error occurred during import. Try to install the enchant C-library")
            raise

        pwl = self.tool_meta.pwl
        pel = self.tool_meta.pel
        return self._check_spelling(annotation_file=annotation_file,
                                   pwl=pwl,
                                   pel=pel,
                                   auto_add=False,
                                   check_id=self.id,
                                   ench=enchant,
                                   lang=self.options.get("language", self.language),
                                   line_limit=line_limit,
                                   )

    @staticmethod
    def _check_spelling(annotation_file, check_id, line_limit, ench, lang, pwl=None, pel=None, auto_add=False):
        """

        :param lang:
        :param ench:
        :param line_limit:
        :param check_id:
        :param annotation_file:
        :param pwl:
        :param pel:
        :param auto_add:
        :return:
        """

        error_list = []
        term_divider = config.load("Annotation","term_divider")
        whitespace_divider = config.load("Annotation","whitespace_divider")
        candidates_number = config.load("SpellCheck","candidates")

        times, divs, expressions = parse_annotation(annotation_file, line_limit)
        enchant_dict = ench.DictWithPWL(lang, pwl, pel)
        if (pwl or pel) is None:
            logger.error("Trying to access enchant without initialized dictionary. \n"
                         "Try to initialize it before you run the spellcheck. \n"
                         "Otherwise it won't work properly")
            enchant_dict = ench.DictWithPWL(lang, "deleteme", "deleteme")

        frequency_list = _count_words(" ".join(expressions), whitespace_divider, term_divider)
        candidates_dict = {}

        for line_index, expression in enumerate(expressions, start=1):
            if expression.strip() == "":
                continue

            words = expression.replace(whitespace_divider, " ").replace(term_divider, " ")
            words_split = words.split(" ")

            start_index = len(times[line_index - 1]) + len(divs[line_index - 1])
            for word in words_split:
                if " " in word or word == "":

                    for char in word:
                        if char == " ":
                            start_index += 1
                    continue
                if word in candidates_dict.keys():
                    error_list.append(
                        Error(
                            file_name=annotation_file,
                            error_type=ErrorType.WrongSpelling,
                            fixes=[Fix(x, fix_code=FixCode.ReplaceSequence) for x in candidates_dict[word]] + [
                                Fix("{{custom}}", fix_code=FixCode.ReplaceSequence)] + [Fix(fix_code=FixCode.AddToDict,correct_string=word)] +
                                  [Fix(fix_code=FixCode.RemoveSequence)]
                                  ,
                            line_number=line_index,
                            incorrect_sequence=Sequence(start_index, word),
                            error_level=ErrorLevel.Warning,
                            check_id=check_id
                        )
                    )
                    start_index += len(word) + 1
                    continue
                if not enchant_dict.check(word):

                    suggestions = enchant_dict.suggest(word)

                    if auto_add:
                        suggestions = [x.replace(" ", "").replace("-", "") if " " in x else x for x in suggestions]

                        # eliminate duplicates
                        suggestions_without_duplicates = []
                        [suggestions_without_duplicates.append(x) for x in suggestions if
                         x not in suggestions_without_duplicates]

                        matches = difflib.get_close_matches(word, suggestions, candidates_number)

                    else:
                        #maybe not eliminate uppercase letters
                        suggestions = [x for x in suggestions if
                                       " " not in x and "-" not in x and not bool(re.match(r'\w*[A-Z]\w*', x))]
                        matches = difflib.get_close_matches(word, suggestions, candidates_number)

                    if set(matches).intersection(frequency_list.keys()):
                        matches.sort(key=lambda x: _frequency_in_text(x, frequency_list), reverse=True)

                    error_list.append(
                        Error(
                            file_name=annotation_file,
                            error_type=ErrorType.WrongSpelling,
                            fixes=[Fix(x, fix_code=FixCode.ReplaceSequence) for x in matches] + [
                                Fix("{{custom}}", fix_code=FixCode.ReplaceSequence)]+ [Fix(fix_code=FixCode.AddToDict,correct_string=word)]  + [
                                      Fix(fix_code=FixCode.RemoveSequence)],
                            line_number=line_index,
                            incorrect_sequence=Sequence(start_index, word),
                            error_level=ErrorLevel.Warning,
                            check_id=check_id
                        )
                    )
                    candidates_dict.update({word: matches})
                start_index += len(word) + 1

        return error_list


def _frequency_in_text(word: str, frequency_list: dict):
    frequency = 0
    if word in frequency_list.keys():
        frequency = frequency_list.get(word)
    return frequency


def _count_words(text: str, *divider: str) -> Dict:
    text = text.replace("\n", " ")
    for div in divider:
        text = text.replace(div, " ")
    return {x: y for x, y in Counter(text.split(" ")).items() if y > 1 and len(x) > 1}
