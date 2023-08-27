from os.path import join

import enchant
import pytest

from acheck.checks.spelling import SpellCheck
from acheck.checking.error import Error, ErrorType, Sequence


def test_check_spelling_single(test_dir):

    error_test = SpellCheck.check_spelling(join(test_dir, "wrong_spelling.csv"),0,-1,enchant,"en_EN")[0]
    error_expected = Error(
        join(test_dir, "wrong_spelling.csv"),
        incorrect_sequence=Sequence(7, "depo"),
        error_type=ErrorType.WrongSpelling,
        line_number=1,
        check_id=0
    )
    assert error_test.incorrect_sequence == error_expected.incorrect_sequence
    assert error_test.error_type == error_expected.error_type
    assert error_test.line_number == error_expected.line_number


def test_check_spelling_multi_word(test_dir):


    error_test = SpellCheck.check_spelling(join(test_dir, "wrong_spelling.csv"),0,-1,enchant,"en_EN")[1]
    error_expected = Error(
        join(test_dir, "wrong_spelling.csv"),
        incorrect_sequence=Sequence(11, "shelfboard"),
        error_type=ErrorType.WrongSpelling,
        line_number=5,
        check_id=-1
    )
    print(error_test)
    assert error_test.incorrect_sequence == error_expected.incorrect_sequence
    assert error_test.error_type == error_expected.error_type
    assert error_test.line_number == error_expected.line_number
