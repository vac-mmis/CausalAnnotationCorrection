import logging
import re
from pathlib import Path
from typing import List
from acheck.utils.annotationhelper import parse_annotation
from acheck.checking.check_interface import Check
from acheck.checking.error import Error, Sequence, Fix, FixCode, ErrorType
from acheck.config import config
from acheck.utils.typecheck import is_int, is_float

logger = logging.getLogger(__name__)


class TimeIsNumberCheck(Check):
    """Check if the first column of the csv line is a number"""

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()
        return self._check_time_is_number(annotation_file=annotation_file,
                                         check_id=self.id,
                                         line_limit=line_limit)

    @staticmethod
    def _check_time_is_number(annotation_file: Path, check_id, line_limit) -> List[Error]:
        error_list = []
        times, commas, expressions = parse_annotation(annotation_file, line_limit)
        for index, (time, comma, expression) in enumerate(zip(times, commas, expressions), start=1):

            if (time + comma + expression).strip() == "":
                continue
            try:
                float(time)
            except ValueError as e:
                logger.error(e)
                error_list.append(
                    Error(
                        file_name=annotation_file,
                        incorrect_sequence=Sequence(0, time),
                        fixes=[Fix(correct_string="The time values must be either of type integer or of type float",
                                   fix_code=FixCode.Alert)],
                        error_type=ErrorType.IllegalTimestampNoNumber,
                        line_number=index,
                        check_id=check_id
                    )
                )
        return error_list


class TimeAscendingCheck(Check):
    """Checks whether the given annotation has incrementing timestamps

    :Options:
        - strict:
            Check for real ascending timestamps, otherwise following equal timestamps are allowed
    """
    strict = False

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()

        return self._check_time_ascending(annotation_file,
                                         check_id=self.id,
                                         strict=self.options.get("strict", self.strict),
                                         line_limit=line_limit)

    @staticmethod
    def _check_time_ascending(annotation_file: Path, check_id, line_limit, strict: bool = False, ) -> List[Error]:
        error_list = []
        times, commas, expressions = parse_annotation(annotation_file, line_limit)
        time_old = -1
        for index, (time, comma, expression) in enumerate(zip(times, commas, expressions), start=1):
            if (time + comma + expression).strip() == "" or not is_int(time) or not is_float(time):
                continue
            if len(times) > 0 and float(time) > time_old:
                time_old = float(time)
            elif len(times) >= 0 and float(time) >= time_old and not strict:
                time_old = float(time)
            else:
                error_list.append(
                    Error(
                        file_name=annotation_file,
                        incorrect_sequence=Sequence(0, time),
                        fixes=[Fix(correct_string="Timestamps need to be ascending", fix_code=FixCode.Alert)],
                        error_type=ErrorType.IllegalTimestampNotAscending,
                        line_number=index,
                        check_id=check_id
                    )
                )
        return error_list


class ExpressionStructureCheck(Check):
    """Checks if the structure of the annotation lines have a given pattern

    :Options:
        - regex_expressions_structure:
            The regular expression that matches every line of the annotation
    """

    regex_expressions_structure = config.load("Annotation","regex_expression_structure")

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()

        return self._check_expression_structure(annotation_file=annotation_file,
                                               regex=self.options.get("regex_expressions_structure",
                                                                      self.regex_expressions_structure),
                                               check_id=self.id,
                                               line_limit=line_limit)

    @staticmethod
    def _check_expression_structure(annotation_file, regex, check_id, line_limit) -> List[Error]:
        error_list = []
        times, commas, expressions = parse_annotation(annotation_file, line_limit)
        for index, (time, comma, expression) in enumerate(zip(times, commas, expressions), start=1):
            if (time + comma + expression).strip() == "":
                continue
            p = re.compile(regex)
            if not p.fullmatch(expression):
                error_list.append(
                    Error(
                        annotation_file,
                        incorrect_sequence=Sequence(char_sequence=expression, start_index=len(time) + len(comma)),
                        error_type=ErrorType.IllegalExpressionStructure,
                        line_number=index,
                        check_id=check_id
                    )
                )
                continue
        return error_list
