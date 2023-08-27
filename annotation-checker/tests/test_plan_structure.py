from os.path import join
from acheck.checking.error import Error, Sequence, ErrorType, Fix, FixCode
from acheck.checks.structure import ExpressionStructureCheck, TimeAscendingCheck, TimeIsNumberCheck


def test_time_asc_nostrict(test_dir):
    error_test = TimeAscendingCheck.check_time_ascending(join(test_dir, "annotation_noasc.csv"), 0,-1,strict=False)[0]
    error_expected = Error(
        file_name=join(test_dir, "annotation_noasc.csv"),
        incorrect_sequence=Sequence(0, "17680"),
        fixes=[Fix('Timestamps need to be ascending',fix_code=FixCode.Alert)],
        error_type=ErrorType.IllegalTimestampNotAscending,
        line_number=5,
        check_id=0
    )
    assert error_test.to_dict() == error_expected.to_dict()


def test_time_asc_strict(test_dir):
    error_test = TimeAscendingCheck.check_time_ascending(join(test_dir, "annotation_noasc.csv"), 0,-1,strict=True)[1]
    error_expected = Error(
        file_name=join(test_dir, "annotation_noasc.csv"),
        incorrect_sequence=Sequence(0, "20000"),
        fixes=[Fix('Timestamps need to be ascending',fix_code=FixCode.Alert)],
        error_type=ErrorType.IllegalTimestampNotAscending,
        line_number=7,
        check_id=0
    )
    assert error_test.to_dict() == error_expected.to_dict()


def test_time_is_no_number(test_dir):
    error_test = TimeIsNumberCheck.check_time_is_number(join(test_dir, "annotation_noint.csv"),0,-1,)[0]
    error_expected = Error(
        file_name=join(test_dir, "annotation_noint.csv"),
        incorrect_sequence=Sequence(0, "Time3640"),
        fixes=[Fix(correct_string='The time values must be either of type integer or of type float')],
        error_type=ErrorType.IllegalTimestampNoNumber,
        line_number=2,
        check_id=0
    )
    assert error_test.to_dict() == error_expected.to_dict()


def test_time_is_number_float(test_dir):
    error_list = TimeIsNumberCheck.check_time_is_number(join(test_dir, "annotation_isfloat.csv"),0,-1,)
    assert len(error_list) == 0


def test_wrong_expression_structure(test_dir, expression_structure_regex):
    error_test = ExpressionStructureCheck.check_expression_structure(join(test_dir, "annotation_noexpr.csv"),
                                                                     expression_structure_regex,0,-1,)[0]
    error_expected = Error(
        join(test_dir, "annotation_noexpr.csv"),
        incorrect_sequence=Sequence(2, 'walk-depot-table_'),
        fixes=[Fix()],
        error_type=ErrorType.IllegalExpressionStructure,
        line_number=1,
        check_id=0
    )
    assert error_test.to_dict() == error_expected.to_dict()
