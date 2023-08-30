import logging
import pprint
from enum import Enum, auto, IntEnum
import json
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)
"""Register logging"""


class ErrorType(Enum):
    """All different error types that a check can display"""

    IllegalFile = auto()
    """There is an error when opening or reading the file"""
    IllegalCSVFile = auto()
    """There is an error when opening or reading a csv file"""
    WrongSpelling = auto()
    """There a spelling mistake"""
    IllegalCharacter = auto()
    """There are symbols in the annotation that are not allowed"""
    IllegalTimestampNoNumber = auto()
    """The time slice of an annotation is not a number"""
    IllegalTimestampNotAscending = auto()
    """The time stamps of the actions are equal and or not ascending"""
    IllegalExpressionStructure = auto()
    """The structure of the expressions does not correspond to the predefined structure of an annotation expression"""
    UnknownAction = auto()
    """An action is not defined in the domain"""
    UnknownObject = auto()
    """Another object is not known in the domain"""
    IllegalSignature = auto()
    """The signature of an action is not correct or marked as correct"""
    PlanValidationError = auto()
    """An error occurred when validating the plan resulting from the annotation."""
    IllegalDomainDescription = auto()
    """The PDDL description is not correct"""
    IllegalProblemDescription = auto()
    """The PDDL description is not correct"""


class FixCode(Enum):
    """All different types of fixes which can be proposed as solutions to work with in the tool"""

    Alert = auto()
    """A message is displayed in the tool"""
    ReplaceSequence = auto()
    """An incorrect character sequence can be replaced by a correct one"""
    RemoveSequence = auto()
    """An incorrect character sequence can be removed"""
    WhitelistSignature = auto()
    """a special signature of an action is locked as currently correct signature"""
    AdaptModel = auto()
    """The model must be adapted"""
    AddToDict = auto()
    """The model must be adapted"""


class ErrorLevel(IntEnum):
    """Different error levels enable the division of errors into two groups"""

    Warning = 0
    """Warnings are displayed, but they do not cause direct interference and do not cancel the program"""
    Error = 1
    """Errors are serious problems that require direct intervention to keep the program running."""


class Fix:
    """
    An object that holds information about how to fix the error or warning

    :param str correct_string: If there is a corrected character sequence, then it can be saved here. Defaults to "None".
    :param FixCode fix_code: Specifies the type of fix. Defaults to "FixCode.Alert".
    """

    def __init__(self, correct_string: str = None, fix_code: FixCode = FixCode.Alert):
        self.correct_sequence = correct_string
        self.fix_code = fix_code

    def __eq__(self, other):
        return self.correct_sequence == other.correct_sequence and self.fix_code == other.fix_code

    def __str__(self):
        return f"{self.fix_code.name}: {self.correct_sequence}"


class Sequence:
    """
    An object that holds information about the incorrect character sequence

    :param int start_index: Specifies the index at the position of the line where the incorrect character sequence starts. Defaults to "0".
    :param str char_sequence: If there is an incorrect character sequence, then it can be saved here. Defaults to "".
    """

    def __getstate__(self):
        return {
            "start_index": self.start_index,
            "char_sequence": self.char_sequence
        }

    def __setstate__(self, state):
        self.start_index = state["start_index"]
        self.char_sequence = state["char_sequence"]

    def __init__(self, start_index=0, char_sequence=""):
        self.start_index = start_index
        self.char_sequence = char_sequence

    def __eq__(self, other):
        return self.start_index == other.start_index and self.char_sequence == other.char_sequence

    def __str__(self):
        return f"{self.start_index}: {self.char_sequence}"


class Error:
    """
    Specifies an error that holds all information about the problem found in the annotation.

    :param Path file_name: Path of the file.
    :param ErrorType error_type: Specifies the type of the error.
    :param int check_id: To identify the error by check.
    :param int line_number: In which line did the error occur. Defaults to "-1", if the error cannot be assigned to a line.
    :param Sequence incorrect_sequence: Specifies the character sequence that might be wrong. Defaults to "None", if there is no sequence.
    :param List[Fix] fixes: A list of fix objects that can be used to correct the error.
    :param ErrorLevel error_level: Specifies the error level. Defaults to "ErrorLevel.Error".
    :param str advice: A specific message that describes the error in more detail and contains important information. It is usually generated automatically based on all other attributes.
    """

    def __init__(self,
                 file_name: Path,
                 error_type: ErrorType,
                 check_id: int,
                 line_number: int = -1,
                 incorrect_sequence: Sequence = None,
                 fixes: List[Fix] = None,
                 error_level=ErrorLevel.Error,
                 advice: str = None):
        if fixes is None:
            fixes = [Fix()]
        if incorrect_sequence is None:
            incorrect_sequence = Sequence()
        if advice is None:
            advice = build_advice(error_type, line_number, incorrect_sequence, fixes, error_level)

        self.file_name = file_name
        self.incorrect_sequence = incorrect_sequence
        self.line_number = line_number
        self.error_type = error_type
        self.advice = advice
        self.fixes = fixes
        self.error_level = error_level
        self.check_id = check_id

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return {x: self.to_dict()[x] for x in self.to_dict() if x != "advice"} == \
                   {x: other.to_dict()[x] for x in other.to_dict() if x != "advice"}
        return False

    def __lt__(self, other):
        if self.line_number == other.line_number:
            return self.incorrect_sequence.start_index < other.incorrect_sequence.start_index
        return self.line_number < other.line_number

    def __str__(self):
        return self.advice

    def to_dict(self):
        """
        Returns the error object as dictionary.

        :rtype: Dict
        """

        return {
            "file_name": self.file_name,
            "incorrect_sequence": [self.incorrect_sequence.start_index, self.incorrect_sequence.char_sequence],
            "fixes": [[x.correct_sequence, x.fix_code.name] for x in self.fixes],
            "line_number": self.line_number,
            "advice": self.advice,
            "error_type": self.error_type.name,
            "error_level": self.error_level,
            "check_id": self.check_id
        }


def from_dict(error_dict):
    """
    Takes an error as dictionary and creates an error object.

    :param error_dict: Error object as dictionary.
    :return: Error object
    """
    return Error(
        file_name=error_dict["file_name"],
        incorrect_sequence=Sequence(error_dict["incorrect_sequence"][0], error_dict["incorrect_sequence"][1]),
        fixes=[Fix(x[0], FixCode[x[1]]) for x in error_dict["fixes"]],
        advice=error_dict["advice"],
        error_type=ErrorType[error_dict["error_type"]],
        line_number=error_dict["line_number"],
        error_level=error_dict["error_level"],
        check_id=error_dict["check_id"]
    )


def write_list(file_name, error_list) -> None:
    """
    Writes a list of errors into a json file.

    :param file_name: Path of the file
    :param error_list: List of error objects
    """
    error_list_json = json.dumps([x.to_dict() for x in error_list])
    try:
        with open(file_name, "w") as out_file:
            out_file.write(error_list_json)
    except (IOError, Exception):
        logger.error("An error occurred during writing the error list")


def write_groups(file_name, error_list: List[Error]) -> None:
    """
    Takes a list of errors and writes the json groups file.

    :param file_name: Path of the file
    :param error_list: List of error objects
    """
    errors_by_line = group_errors_by_line(error_list)

    error_list_json = {}

    for key, value in errors_by_line.items():

        groups_inline = group_errors_inline(value)

        temp_dict = {}
        for k, v in groups_inline.items():
            temp_dict.update({f"{k[0]},{k[1]}": [x.to_dict() for x in v]})
        # sorted_temp_dict = sorted(temp_dict.items(), key=lambda x: x[0][0])

        error_list_json.update({key: temp_dict})

    json_data = json.dumps(error_list_json)

    try:
        with open(file_name, "w") as out_file:
            out_file.write(json_data)
    except (IOError, Exception):
        logger.error("An error occurred during writing the error list")


def read_list(file_name) -> List[Error] or None:
    """
    Reads a error list file from json and creates a list of error objects
    :param file_name: Path of the file
    :return: List of error objects
    :rtype: List[Error] or None, if there is an error with the list.
    :raises IOError: If an error occurred during reading the error list file.
    """
    try:
        with open(file_name, "r") as infile:
            error_list_json = json.load(infile)
    except IOError:
        logger.error("An error occurred during reading the error list file")
        return None
    return [from_dict(e) for e in error_list_json]


def build_advice(error_type, line_number, incorrect_sequence, fixes, error_level) -> str:
    """
    Takes error parameters and builds an advice message
    :return str: A nicely formatted message that contains all information about the error.
    """
    return f'[{error_level.name}] {error_type.name} \'{incorrect_sequence.char_sequence}\' ' \
           f'l:{line_number} p:{incorrect_sequence.start_index} fixes: {[str(fix) for fix in fixes]}'


def group_errors_by_line(error_list: List[Error]) -> dict:
    """
    Group errors by line
    :param error_list: List of errors
    :return: A dictionary that contains all errors by line. It has each line as a key and the values are all associated errors in a list.
    """
    mapped_errors = {}

    line_numbers = list(set(x.line_number for x in error_list))
    line_numbers.sort()

    for line in line_numbers:
        mapped_errors.update({line: [x for x in error_list if x.line_number == line]})

    return mapped_errors


def group_errors_inline(errors: List[Error]) -> dict:
    """
    Errors are grouped by line. If the sequences of the errors overlap, they are included in the same group.
    :param List[Error] errors: List of errors
    :return: A dictionary that contains all groups. It has the start index and the end index of each group as a key and the values are then all associated errors in a list.
    """
    groups = {}

    # sorting errors
    errors.sort(key=lambda x: x.incorrect_sequence.start_index)

    current_intersection_test = []
    current_group = []

    for error in errors:

        start = error.incorrect_sequence.start_index
        if error.line_number > 0 and start == 0 and error.incorrect_sequence.char_sequence == "":
            groups.update({(-1, -1): errors})
            break

        end = start + len(error.incorrect_sequence.char_sequence)
        current_indexes = set([x for x in range(start, end + 1)])
        current_intersection_test.append(current_indexes)

        if len(current_intersection_test) == 0:
            current_group.append(error)


        elif set.intersection(*[x for x in current_intersection_test]):

            if len(current_intersection_test) > 1:
                current_intersection_test = [
                    set(list(current_intersection_test[0]) + list(current_intersection_test[1]))]

            current_group.append(error)
        else:

            tmp = current_intersection_test.pop()
            groups.update(
                {(min(set.union(*current_intersection_test)),
                  max(set.union(*current_intersection_test))): current_group})

            current_intersection_test = [tmp]
            current_group = [error]

    if len(current_group) > 0:
        groups.update(
            {(min(set.union(*current_intersection_test)), max(set.union(*current_intersection_test))): current_group})

    return groups

