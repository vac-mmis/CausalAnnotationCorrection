from pathlib import Path
from typing import List
from acheck.checking.check_interface import ToolObjectsMeta
from acheck.utils import annotationhelper as ah
from acheck.checking.error import Error, Fix, FixCode
import json
import acheck.utils.filehelper as fh


def compute_fix_request(error_id: int, fix_id: int, fix_same: bool, errors: List[Error], annotation_file, tool_meta,
                        custom_replace: str = None):
    if not fix_same:
        if len(errors) > error_id:
            _fix_error(errors[error_id], fix_id, annotation_file, tool_meta, custom_replace)
    else:
        if len(errors) > error_id:
            _fix_errors(_get_all_errors(errors[error_id], errors), fix_id, annotation_file, tool_meta, custom_replace)


def _fix_add_dictionary(fix: Fix, pwl, pel):

    fh.write_unique_words_to_file(pwl, fix.correct_sequence)
    fh.delete_words_from_file(pel, fix.correct_sequence)


def _fix_whitelist_signature(fix: Fix, signatures_file):
    active_signature = fix.correct_sequence.split("/")

    signatures = json.loads(fh.read_file(signatures_file))
    signatures.update({active_signature[0]: active_signature[1]})
    fh.write_file(signatures_file, json.dumps(signatures))


def _get_all_errors(error: Error, error_list: List[Error]) -> List[Error]:
    errors = [x for x in error_list if
              x.incorrect_sequence.char_sequence == error.incorrect_sequence.char_sequence and x.error_type == error.error_type]
    return errors


def _fix_error(error: Error, fix_id: int, annotation_file: Path, data_paths, custom_replace):
    _fix_errors([error], fix_id, annotation_file, data_paths, custom_replace)


def _fix_errors(errors: List[Error], fix_id: int, annotation_file: Path, data_paths, custom_replace):
    numbers = list(set(n.line_number for n in errors))
    numbers.sort()
    errors_by_line = {y: [x for x in errors if x.line_number == y] for y in numbers}

    for key, value in errors_by_line.items():
        _apply_fixes_inline(value, fix_id, key, annotation_file, data_paths, custom_replace)


def _apply_fixes_inline(errors: List[Error], fix_id: int, line_number: int, annotation_file: Path,
                        tool_meta: ToolObjectsMeta, custom_replace) -> None:
    errors.sort(key=lambda x: x.incorrect_sequence.start_index)

    signatures_file = tool_meta.signatures
    pwl = tool_meta.pwl
    pel = tool_meta.pel

    index_shift = 0

    annotation_list = ah.read_annotation(annotation_file, -1)

    for error in errors:

        fix = error.fixes[fix_id]
        fix_code = fix.fix_code
        incorrect_sequence = error.incorrect_sequence

        if fix_code is FixCode.ReplaceSequence:
            if custom_replace:
                fix.correct_sequence = custom_replace
            annotation_list[line_number - 1] = _replace_string(annotation_list[line_number - 1],
                                                               incorrect_sequence.start_index + index_shift,
                                                               incorrect_sequence.char_sequence, fix.correct_sequence)
            index_shift += len(fix.correct_sequence) - len(incorrect_sequence.char_sequence)

        elif fix_code is FixCode.RemoveSequence:
            annotation_list[line_number - 1] = _replace_string(annotation_list[line_number - 1],
                                                               incorrect_sequence.start_index + index_shift,
                                                               incorrect_sequence.char_sequence)
            index_shift -= len(incorrect_sequence.char_sequence)

        elif fix_code == FixCode.WhitelistSignature:
            _fix_whitelist_signature(fix, signatures_file)
        elif fix_code == FixCode.AddToDict:
            _fix_add_dictionary(fix, pwl,pel)

    ah.write_annotation(annotation_list, annotation_file)


def _replace_string(line: str, start_index, old_string, new_string="") -> str:
    start = line[0:start_index]
    end = line[start_index + len(old_string):]
    return start + new_string + end
