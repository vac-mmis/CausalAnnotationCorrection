import re
import time
import requests
import subprocess
from pathlib import Path
from typing import List, Tuple
from acheck.config import config
from acheck.checking.check_interface import Check, ToolObjectsMeta
from acheck.checking.error import Error, ErrorType, Sequence, Fix, FixCode, ErrorLevel
from acheck.utils import filehelper as fh
from acheck.utils.annotationhelper import get_plan, time_to_line_number, read_annotation

import logging

logger = logging.getLogger(__name__)


def _parse_stdout(stdout):
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


def _parse_stderr(stderr):
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


def _use_validator(domain, problem, plan, validator_path, timeout, logs):
    process_stdout = ""
    process_stderr = f"Validator timeout after {timeout} seconds"
    try:
        completed_process = subprocess.run(
            [validator_path, "-v", domain, problem, plan],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        process_stdout = completed_process.stdout
        process_stderr = completed_process.stderr
    except subprocess.TimeoutExpired:
        logs.append(
            f"Full output from plan validator:\nValidator timeout after {timeout} seconds"
        )
        raise
    except Exception:
        logs.append(
            f"An error occurred during plan validation.\nMake sure that the path to the validator executable is set correctly.\nPath: '{validator_path}'"
        )
        raise

    return process_stdout, process_stderr


def _plan_validation(
    annotation: Path,
    domain: Path,
    problem: Path,
    tool_meta: ToolObjectsMeta,
    add_finished_as_last_line: bool,
    check_id,
    line_limit,
    logs: List[str],
    timeout: int = 5,
):
    plan = [x["plan"] for x in tool_meta.annotations if x["file"] == annotation][0]
    plan_lines = get_plan(annotation, line_limit, add_finished_as_last_line)

    fh.write_lines(plan, plan_lines)
    validator = tool_meta.validator

    annotation_lines = read_annotation(annotation, line_limit)

    stdout, stderr = _use_validator(domain, problem, plan, validator, timeout, logs)

    error_list = []

    messages = _parse_stdout(stdout)

    logs.append(stdout.decode("utf-8"))
    logs.append(stderr.decode("utf-8"))

    critical_messages = _parse_stderr(stderr)

    for critical_msg in critical_messages:
        if "domain" in critical_msg:
            error_list.append(
                Error(
                    file_name=domain,
                    fixes=[
                        Fix(
                            fix_code=FixCode.Alert,
                            correct_string="Domain description is invalid.",
                        )
                    ],
                    error_type=ErrorType.IllegalDomainDescription,
                    check_id=check_id,
                )
            )
        if "failed to read file" in critical_msg:
            error_list.append(
                Error(
                    file_name=domain,
                    fixes=[
                        Fix(
                            fix_code=FixCode.Alert,
                            correct_string="Problem description is invalid.",
                        )
                    ],
                    error_type=ErrorType.IllegalProblemDescription,
                    check_id=check_id,
                )
            )
        if "Error:" in critical_msg:
            error_list.append(
                Error(
                    file_name=domain,
                    fixes=[
                        Fix(
                            fix_code=FixCode.Alert,
                            correct_string="There was an error during plan validation. "
                            "Make sure that 'ActionCheck' and 'WorldObjectCheck' are enabled. "
                            "For more information, check the log.",
                        )
                    ],
                    error_type=ErrorType.PlanValidationError,
                    check_id=check_id,
                )
            )

    warn_messages = []
    error_messages = []

    for msg_block in messages:
        warnings = [msg_block for line in msg_block if "WARNING" in line]
        errors = [
            msg_block
            for line in msg_block
            if ("failed" in line) or ("Bad plan description!" in line)
        ]
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
                    fixes=[
                        Fix(
                            fix_code=FixCode.Alert, correct_string=" ".join(error_block)
                        )
                    ],
                )
            )
        else:
            error_list.append(
                Error(
                    file_name=annotation,
                    error_type=ErrorType.PlanValidationError,
                    line_number=time_to_line_number(
                        annotation, _get_time_from_block(error_block), line_limit
                    ),
                    incorrect_sequence=Sequence(
                        0,
                        annotation_lines[
                            time_to_line_number(
                                annotation,
                                _get_time_from_block(error_block),
                                line_limit,
                            )
                            - 1
                        ],
                    ),
                    check_id=check_id,
                    fixes=[
                        Fix(
                            fix_code=FixCode.Alert, correct_string=" ".join(error_block)
                        )
                    ],
                )
            )

    return error_list


def _get_time_from_block(msg_block) -> float:
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

    timeout = config.load("Validator", "timeout")

    def run(
        self, annotation_file, domain_file, problem_file, line_limit=-1
    ) -> List[Error]:
        self.logs.clear()
        return _plan_validation(
            annotation=annotation_file,
            domain=domain_file,
            problem=problem_file,
            tool_meta=self.tool_meta,
            add_finished_as_last_line=False,
            check_id=self.id,
            line_limit=line_limit,
            logs=self.logs,
            timeout=self.options.get("timeout", self.timeout),
        )


@DeprecationWarning
class PDDLSyntaxCheckOld(Check):
    """Checks the model files for pddl syntax errors

    :Options:
        - timeout:
            Time after which the validator terminates if it does not receive a response
    """

    timeout = 10

    def run(
        self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1
    ) -> List[Error]:
        self.logs.clear()

        domain_data = fh.read_file(domain)
        problem_data = fh.read_file(problem)

        data = {"domain": domain_data, "problem": problem_data}

        solve_request_url = requests.post(
            "http://localhost:5001/package/lama-first/solve", json=data
        ).json()

        # Query the result in the job
        celery_result = requests.post(
            "http://localhost:5001" + solve_request_url["result"]
        )

        print("Computing...")
        while celery_result.json().get("status", "") == "PENDING":
            # Query the result every 0.5 seconds while the job is executing
            celery_result = requests.post(
                "http://localhost:5001" + solve_request_url["result"]
            )
            time.sleep(1)

        response = celery_result.json()

        if response.get("result") is None:
            raise Exception(
                "No result from 'http://localhost:5001/package/lama-first/solve'"
            )

        if isinstance(response.get("result"), str):
            raise Exception(response.get("result"))

        if not bool(response.get("result").get("output")):
            err_msg_verbose = response["result"]["stderr"]
            err_msg = response["result"]["stdout"]

            self.logs.append(response.get("result").get("stdout"))

            if "Error:" in err_msg:
                self.logs.append(
                    f"Full output from 'http://localhost:5001/package/lama-first/solve':\n{err_msg_verbose}"
                )

                # Determine if it's a domain or problem file error
                is_domain_error = "domain file" in err_msg
                is_problem_error = (
                    "task file" in err_msg or "problem" in err_msg.lower()
                )

                # Look for the reason in the output
                error_pattern = r"Reason: (.+)"
                hit = re.search(error_pattern, err_msg)
                if hit:
                    error_message = hit.group(1).strip()
                else:
                    error_message = "Unknown error"

                # Attempt to find line number if available
                line_pattern = r"line (\d+)"
                line_hit = re.search(line_pattern, err_msg)
                if line_hit:
                    line_number = int(line_hit.group(1))
                else:
                    line_number = -1

                if is_domain_error:
                    return [
                        Error(
                            file_name=domain,
                            error_type=ErrorType.IllegalDomainDescription,
                            check_id=self.id,
                            line_number=line_number,
                            fixes=[
                                Fix(
                                    correct_string=error_message, fix_code=FixCode.Alert
                                )
                            ],
                            error_level=ErrorLevel.Error,
                        )
                    ]
                elif is_problem_error:
                    return [
                        Error(
                            file_name=problem,
                            error_type=ErrorType.IllegalProblemDescription,
                            check_id=self.id,
                            line_number=line_number,
                            fixes=[
                                Fix(
                                    correct_string=error_message, fix_code=FixCode.Alert
                                )
                            ],
                            error_level=ErrorLevel.Error,
                        )
                    ]

            # Fallback to original error patterns if the above doesn't match

            # Original problem file error handling
            if "problem.pddl" in err_msg.split(" ")[0]:
                self.logs.append(
                    f"Full output from 'http://localhost:5001/package/lama-first/solve':\n{err_msg_verbose}"
                )

                pattern = r"syntax error in line (\d+)"
                hit = re.search(pattern, err_msg)
                if hit:
                    line_number = int(hit.group(1))
                else:
                    line_number = -1

                return [
                    Error(
                        file_name=problem,
                        error_type=ErrorType.IllegalProblemDescription,
                        check_id=self.id,
                        line_number=line_number,
                        fixes=[Fix(correct_string=err_msg, fix_code=FixCode.Alert)],
                        error_level=ErrorLevel.Error,
                    )
                ]

            # Original domain file error handling as a fallback
            if "domain.pddl" in err_msg.split(" ")[0]:
                self.logs.append(
                    f"Full output from 'http://localhost:5001/package/lama-first/solve':\n{err_msg_verbose}"
                )

                pattern = r"syntax error in line (\d+)"
                hit = re.search(pattern, err_msg)
                if hit:
                    line_number = int(hit.group(1))
                else:
                    line_number = -1

                return [
                    Error(
                        file_name=domain,
                        error_type=ErrorType.IllegalDomainDescription,
                        check_id=self.id,
                        line_number=line_number,
                        fixes=[Fix(correct_string=err_msg, fix_code=FixCode.Alert)],
                        error_level=ErrorLevel.Error,
                    )
                ]
        else:
            self.logs.append(
                f"Full output from 'http://localhost:5001/package/lama-first/solve':\n\n{response.get('result').get('output').get('sas_plan')}"
            )

        return []


class PDDLSyntaxCheck(Check):
    """Checks the model files for pddl syntax errors using the AI-Planning/pddl library.

    This implementation replaces the previous web service implementation with a direct
    library-based approach for more detailed error reporting.
    """

    def run(
        self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1
    ) -> List[Error]:
        self.logs.clear()
        errors = []

        # Check domain file syntax
        domain_errors = self._check_domain_file(domain)
        if domain_errors:
            errors.extend(domain_errors)
            # If domain has errors, we return early as problem parsing might depend on domain
            return errors

        # Check problem file syntax
        problem_errors = self._check_problem_file(problem, domain)
        if problem_errors:
            errors.extend(problem_errors)

        return errors

    def _check_domain_file(self, domain_path: Path) -> List[Error]:
        """Check PDDL domain file syntax using the pddl library."""
        from pddl import parse_domain

        try:
            # Parse the domain file
            parse_domain(str(domain_path))
            # If no exception, parsing was successful
            self.logs.append(f"Domain file {domain_path} parsed successfully")
            return []
        except Exception as e:
            # Extract error details
            error_message, line_number = self._extract_error_details(str(e))
            self.logs.append(f"Error parsing domain file: {str(e)}")

            return [
                Error(
                    file_name=domain_path,
                    error_type=ErrorType.IllegalDomainDescription,
                    check_id=self.id,
                    line_number=line_number,
                    fixes=[Fix(correct_string=error_message, fix_code=FixCode.Alert)],
                    error_level=ErrorLevel.Error,
                )
            ]

    def _check_problem_file(self, problem_path: Path, domain_path: Path) -> List[Error]:
        """Check PDDL problem file syntax using the pddl library."""
        from pddl import parse_problem

        try:
            # Parse the problem file
            parse_problem(str(problem_path))
            # If no exception, parsing was successful
            self.logs.append(f"Problem file {problem_path} parsed successfully")
            return []
        except Exception as e:
            # Extract error details
            error_message, line_number = self._extract_error_details(str(e))
            self.logs.append(f"Error parsing problem file: {str(e)}")

            return [
                Error(
                    file_name=problem_path,
                    error_type=ErrorType.IllegalProblemDescription,
                    check_id=self.id,
                    line_number=line_number,
                    fixes=[Fix(correct_string=error_message, fix_code=FixCode.Alert)],
                    error_level=ErrorLevel.Error,
                )
            ]

    def _extract_error_details(self, error_str: str) -> Tuple[str, int]:
        """Extract line number and clean error message from exception text."""
        import re

        # Try to extract line number
        line_match = re.search(r"at line (\d+)", error_str)
        line_number = int(line_match.group(1)) if line_match else -1

        # Clean up the error message to be more user-friendly
        # Remove technical details like "During handling of the above exception..."
        cleaned_message = error_str.split("During handling of the above exception")[
            0
        ].strip()

        # If there's detailed error location info, keep it
        if "Expected one of:" in error_str:
            # Find everything from the beginning to "Expected one of:" including the list of expected tokens
            expected_match = re.search(
                r"(Expected one of:.*?)(?=Previous tokens:|$)", error_str, re.DOTALL
            )
            if expected_match:
                expected_info = expected_match.group(1).strip()
                cleaned_message += f"\n{expected_info}"

        return cleaned_message, line_number
