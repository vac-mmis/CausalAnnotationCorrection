from acheck.checks.file import CSVFormatCheck, CharacterCheck
from os.path import join

from acheck.checking.error import Error, Sequence, ErrorType, Fix, FixCode, ErrorLevel





def test_umlaut(test_dir, symbol_regex,time_regex):
    error_test = CharacterCheck.check_characters(join(test_dir, "annotation_symbols.csv"), 0, symbol_regex,time_regex, -1)[0]
    error_expected = Error(
        join(test_dir, "annotation_symbols.csv"),
        incorrect_sequence=Sequence(26, "ä"),
        fixes=[Fix(fix_code=FixCode.RemoveSequence)],
        error_type=ErrorType.IllegalCharacter,
        line_number=6,
        check_id=0
    )

    assert error_test.to_dict() == error_expected.to_dict()


def test_illegal_symbol(test_dir, symbol_regex, time_regex):
    error_test = CharacterCheck.check_characters(join(test_dir, "annotation_symbols.csv"), 0, symbol_regex,time_regex, -1)[1]
    error_expected = Error(
        join(test_dir, "annotation_symbols.csv"),
        incorrect_sequence=Sequence(21, "."),
        fixes=[Fix(fix_code=FixCode.RemoveSequence)],
        error_type=ErrorType.IllegalCharacter,
        line_number=12,
        check_id=0
    )

    assert error_test == error_expected


def test_is_csv(test_dir):
    error_test = CSVFormatCheck.check_csv_structure(join(test_dir, "example.csv"), 32000,0)
    assert len(error_test) == 0


def test_is_csv_compressed_file(test_dir):
    error_test = CSVFormatCheck.check_csv_structure(join(test_dir, "compressed.csv"), 32000,0)[0]
    assert error_test.error_type is ErrorType.IllegalCSVFile


def test_is_csv_empty(test_dir):
    error_test = CSVFormatCheck.check_csv_structure(join(test_dir, "empty_file.csv"), 32000,0)

    assert len(error_test) == 0


def test_is_csv_nofile(test_dir):
    error_test = CSVFormatCheck.check_csv_structure(test_dir, 32000,0)[0]
    assert error_test.error_type is ErrorType.IllegalCSVFile


def test_is_csv_multi_delimiter(test_dir):
    error_test = CSVFormatCheck.check_csv_structure(join(test_dir, "multi_delimiter.csv"), 32000,0)[0]
    assert error_test.error_type is ErrorType.IllegalCSVFile
