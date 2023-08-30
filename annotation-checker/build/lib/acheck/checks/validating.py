import re
import requests
import subprocess
from pathlib import Path
from typing import List
from acheck.config import config
from acheck.checking.check_interface import Check, ToolObjectsMeta
from acheck.checking.error import Error, ErrorType, Sequence, Fix, FixCode, ErrorLevel
from acheck.utils import filehelper as fh
from acheck.utils.annotationhelper import get_plan, time_to_line_number, read_annotation

import logging

logger = logging.getLogger(__name__)


def parse_stdout(stdout):
    messages = []
    msg_buffer = []
    is_msg = False
    for line in stdout.decode("utf-8").splitlines():
        if "Checking next happening" in line:
            is_msg = True
        elif "Bad plan description!" in line:
            is_msg = True
        if line == "" or line == "\n":
            is_msg = False
        if is_msg:
            msg_buffer.append(line)
        else:
            if len(msg_buffer) > 0:
                messages.append(msg_buffer)
            msg_buffer = []
    if len(msg_buffer) > 0:
        messages.append(msg_buffer)
    return messages


def parse_stderr(stderr):
    messages = []
    error_buffer = ""
    for line in stderr.decode("utf-8").splitlines():
        if "Problem in domain definition" in line:
            messages.append(line)
        elif "Parser failed to read file" in line:
            messages.append(line)

        else:
            error_buffer += line
    messages.append(error_buffer)

    return messages


def use_validator(domain, problem, plan, validator_path, timeout, logs):
    process_stdout = ""
    process_stderr = f"Validator timeout after {timeout} seconds"
    try:
        completed_process = subprocess.run([validator_path, "-v", domain, problem, plan], stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, timeout=timeout)
        process_stdout = completed_process.stdout
        process_stderr = completed_process.stderr
    except subprocess.TimeoutExpired:
        logs.append(f"Full output from plan validator:\nValidator timeout after {timeout} seconds")
        raise
    except Exception:
        logs.append(
            f"An error occurred during plan validation.\nMake sure that the path to the validator executable is set correctly.\nPath: '{validator_path}'")
        raise

    return process_stdout, process_stderr


def plan_validation(annotation: Path, domain: Path, problem: Path, tool_meta: ToolObjectsMeta,
                    add_finished_as_last_line: bool,
                    check_id,
                    line_limit, logs: List[str],
                    timeout: int = 5):
    plan = [x["plan"] for x in tool_meta.annotations if x["file"] == annotation][0]
    plan_lines = get_plan(annotation, line_limit, add_finished_as_last_line)

    fh.write_lines(plan, plan_lines)
    validator = tool_meta.validator

    annotation_lines = read_annotation(annotation, line_limit)

    stdout, stderr = use_validator(domain, problem, plan, validator, timeout, logs)



    error_list = []

    messages = parse_stdout(stdout)

    logs.append(stdout.decode('utf-8'))
    logs.append(stderr.decode('utf-8'))

    critical_messages = parse_stderr(stderr)

    for critical_msg in critical_messages:
        if "domain" in critical_msg:
            error_list.append(
                Error(
                    file_name=domain,
                    fixes=[Fix(fix_code=FixCode.Alert, correct_string="Domain description is invalid.")],
                    error_type=ErrorType.IllegalDomainDescription,
                    check_id=check_id,

                )
            )
        if "failed to read file" in critical_msg:
            error_list.append(
                Error(
                    file_name=annotation,

                    fixes=[Fix(fix_code=FixCode.Alert, correct_string="Problem description is invalid.")],
                    error_type=ErrorType.IllegalProblemDescription,
                    check_id=check_id
                )
            )
        if "Error:" in critical_msg:
            error_list.append(
                Error(
                    file_name=annotation,

                    fixes=[Fix(fix_code=FixCode.Alert, correct_string="There was an error during plan validation. "
                                                                      "Make sure that 'ActionCheck' and 'WorldObjectCheck' are enabled. "
                                                                      "For more information, check the log.")],
                    error_type=ErrorType.PlanValidationError,
                    check_id=check_id
                )
            )

    warn_messages = []
    error_messages = []

    for msg_block in messages:

        warnings = [msg_block for line in msg_block if "WARNING" in line]
        errors = [msg_block for line in msg_block if ("failed" in line) or ("Bad plan description!" in line)]
        if errors:
            error_messages.append(errors[0])
        if warnings:
            warn_messages.append(warnings[0])

    for error_block in error_messages:

        if "Bad plan description!" in error_block:
            error_list.append(
                Error(
                    file_name=domain,
                    error_type=ErrorType.PlanValidationError,
                    check_id=check_id,
                    fixes=[Fix(fix_code=FixCode.Alert, correct_string=" ".join(error_block))]
                )
            )
        else:

            error_list.append(
                Error(
                    file_name=domain,
                    error_type=ErrorType.PlanValidationError,
                    line_number=time_to_line_number(annotation, get_time_from_block(error_block), line_limit),
                    incorrect_sequence=Sequence(0, annotation_lines[
                        time_to_line_number(annotation, get_time_from_block(error_block), line_limit) - 1]),
                    check_id=check_id,
                    fixes=[Fix(fix_code=FixCode.Alert, correct_string=" ".join(error_block))]
                )
            )

    return error_list


def get_time_from_block(msg_block) -> float:
    m = re.search(r"(time [0-9]*)(.)?[0-9]*", msg_block[0])
    if m:
        time = m.group().split(" ")[1].strip(")")
        return float(time)


class PlanValidationCheck(Check):
    """Do a plan validation based on the given annotation

    :Options:
        - timeout:
            Time after which the validator terminates if it does not receive a response
    """

    timeout = config.load("Validator","timeout")

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()
        return plan_validation(annotation=annotation_file,
                               domain=domain_file,
                               problem=problem_file,
                               tool_meta=self.tool_meta,
                               add_finished_as_last_line=False,
                               check_id=self.id,
                               line_limit=line_limit,
                               logs=self.logs,
                               timeout=self.options.get("timeout", self.timeout))


class PDDLSyntaxCheck(Check):
    """Checks the model files for pddl syntax errors

       :Options:
           - timeout:
               Time after which the validator terminates if it does not receive a response
    """

    timeout = config.load("DomainProblemCheck","timeout")

    def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
        self.logs.clear()

        domain_data = fh.read_file(domain)
        problem_data = fh.read_file(problem)

        data = {'domain': domain_data,
                'problem': problem_data}
        response = requests.post('http://solver.planning.domains/solve', verify=False, json=data,
                                 timeout=self.options.get("timeout", self.timeout)).json()

        if response.get("status") == "ok" and response.get("result").get("parse_status") == "ok":
            output = response["result"]["output"]
            self.logs.append(f"Full output from 'http://solver.planning.domains/solve':\n{output}")

        if isinstance(response.get("result"), str):
            raise Exception(response.get("result"))
        if response.get("status") == "error" and response.get("result").get("parse_status") == "err":

            err_msg_verbose = response["result"]["error"]
            err_msg = response["result"]["output"]

            if "problem.pddl" in err_msg.split(" ")[0]:
                self.logs.append(f"Full output from 'http://solver.planning.domains/solve':\n{err_msg_verbose}")

                pattern = r"syntax error in line (\d+)"
                hit = re.search(pattern, err_msg)
                if hit:
                    line_number = int(hit.group(1))
                else:
                    line_number = -1

                return [Error(
                    file_name=problem,
                    error_type=ErrorType.IllegalProblemDescription,
                    check_id=self.id,
                    line_number=line_number,
                    fixes=[Fix(correct_string=err_msg, fix_code=FixCode.Alert)],
                    error_level=ErrorLevel.Error

                )]

            if "domain.pddl" in err_msg.split(" ")[0]:
                self.logs.append(f"Full output from 'http://solver.planning.domains/solve':\n{err_msg_verbose}")

                pattern = r"syntax error in line (\d+)"
                hit = re.search(pattern, err_msg)
                if hit:
                    line_number = int(hit.group(1))
                else:
                    line_number = -1
                return [Error(
                    file_name=domain,
                    error_type=ErrorType.IllegalDomainDescription,
                    check_id=self.id,
                    line_number=line_number,
                    fixes=[Fix(correct_string=err_msg, fix_code=FixCode.Alert)],
                    error_level=ErrorLevel.Error

                )]

        return []
