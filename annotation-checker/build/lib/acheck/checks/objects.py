import difflib
import io
import sys
from typing import List
from pddlpy import DomainProblem
from acheck.checking.check_interface import Check
from acheck.checking.error import Error, ErrorType, Sequence, Fix, FixCode
from acheck.utils.annotationhelper import parse_annotation
from acheck.config import config
import contextlib
import logging

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def suppress_stdout():
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class WorldObjectsCheck(Check):
    """Check for objects that are not part of the model description

    e.g. the objects in "hold-manual-both" are manual and both
    """

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()
        errors = self.check_world_objects(annotation=annotation_file,
                                          domain=domain_file,
                                          problem=problem_file,
                                          check_id=self.id,
                                          line_limit=line_limit,
                                          logs=self.logs)
        return errors

    @staticmethod
    def check_world_objects(annotation, domain, problem, check_id, line_limit, logs):
        logs = []
        errors = []

        with suppress_stdout() as (stdout, stderr):
            domain_problem = DomainProblem(domain, problem)
        logs.append(f"Full output of pddlpy:\n{stdout.getvalue()}{stderr.getvalue()}")

        world_objects = domain_problem.worldobjects()

        divider = config.load("Annotation","term_divider")
        times, divs, expressions = parse_annotation(annotation, line_limit)
        for line, expression in enumerate(expressions, start=1):
            if expression == "" or expression == "\n":
                continue
            literals = expression.split(divider)[1:]
            index = len(expression.split(divider)[0]) + 1
            for literal in literals:
                if literal in world_objects or literal.isdigit():
                    index += len(literal) + 1
                    continue

                closest = difflib.get_close_matches(literal, world_objects, 3)

                fixes = [Fix(correct_string=x, fix_code=FixCode.ReplaceSequence) for x in closest] + [
                    Fix(correct_string=literal, fix_code=FixCode.AdaptModel)] + [
                            Fix(fix_code=FixCode.ReplaceSequence, correct_string="{{custom}}")]

                errors.append(
                    Error(
                        file_name=annotation,
                        error_type=ErrorType.UnknownObject,
                        line_number=line,
                        incorrect_sequence=Sequence(len(times[line - 1]) + len(divs[line - 1]) + index, literal),
                        fixes=fixes,
                        check_id=check_id
                    )
                )
                index += len(literal) + 1
        return errors


class ActionCheck(Check):
    """Check for actions that are not part of the model description

    e.g. the action in "hold-manual-both" is hold
    """

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:

        self.logs.clear()
        errors = self.check_actions(annotation=annotation_file,
                                    domain=domain_file,
                                    problem=problem_file,
                                    check_id=self.id,
                                    line_limit=line_limit,
                                    logs=self.logs)
        return errors

    @staticmethod
    def check_actions(annotation, domain, problem, check_id, line_limit, logs):
        errors = []

        with suppress_stdout() as (stdout, stderr):
            domain_problem = DomainProblem(domain, problem)
        logs.append(f"Full output of pddlpy:\n{stdout.getvalue()}{stderr.getvalue()}")

        actions = domain_problem.operators()




        divider = config.load("Annotation","term_divider")
        times, divs, expressions = parse_annotation(annotation, line_limit)
        for line, expression in enumerate(expressions, start=1):
            if expression == "" or expression == "\n":
                continue
            first = expression.split(divider)[0]

            if first in actions:
                continue

            closest = difflib.get_close_matches(first, actions, 3)

            parameter_string = f":parameters ("

            for i, x in enumerate(expression.split(divider)[1:]):
                parameter_string += f"?p{i} - type{i} "
            parameter_string += f")"

            action_pddl_template = (f"(:action {first}\n"
                                    f"\t{parameter_string}\n"
                                    f"\t:precondition ()\n"
                                    f"\t:effect ()\n"
                                    f")")
            fixes = [Fix(correct_string=x, fix_code=FixCode.ReplaceSequence) for x in closest] + [
                Fix(correct_string=action_pddl_template, fix_code=FixCode.AdaptModel)] + [
                        Fix(fix_code=FixCode.ReplaceSequence, correct_string="{{custom}}")]

            errors.append(
                Error(
                    file_name=annotation,
                    error_type=ErrorType.UnknownAction,
                    line_number=line,
                    incorrect_sequence=Sequence(len(times[line - 1]) + len(divs[line - 1]), first),
                    fixes=fixes,
                    check_id=check_id
                )
            )
        return errors
