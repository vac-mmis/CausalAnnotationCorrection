import json
import multiprocessing
import os
import time
import traceback
import socketserver
import threading

from enum import Enum
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from typing import Tuple, List
from urllib.parse import urlparse
from docutils.core import publish_parts

from acheck.checking import fixing, error

from acheck.utils import loghelper as log
from acheck.utils import filehelper as fh

from acheck.checking.check_interface import CheckGroup, Check, ToolObjectsMeta
from acheck.checking.error import ErrorLevel, write_list, write_groups, Error, read_list
import logging

logger = logging.getLogger(__name__)


class MyServer(ThreadingHTTPServer):

    def __init__(self,
                 server_address: Tuple[str, int],
                 lock: threading.Lock,
                 lock_timeout: int,
                 tool_meta: ToolObjectsMeta,
                 checks: List[Check],
                 verbose: bool,
                 ):
        handler = MyRequestHandlerFactory(lock, lock_timeout, tool_meta, checks, verbose)
        super().__init__(server_address, handler)


class ContentType(Enum):
    HTML = "text/html"
    JSON = "application/json"
    JS = "text/javascript"
    CSS = "text/css"
    TEXT = "text/plain"
    ICO = "image/x-icon"
    JPEG = "image/jpeg"
    JPG = "image/jpeg"
    PNG = "image/png"
    SVG = "image/svg+xml"


def get_newest_timestamp(directory: Path):
    latest_time = 0

    for path, _, files in os.walk(directory):
        for name in files:
            file = os.path.join(path, name)
            mtime = os.path.getmtime(file)
            if mtime > latest_time:
                latest_time = mtime

    return latest_time


def MyRequestHandlerFactory(lock: threading.Lock, lock_timeout: int, tool_meta: ToolObjectsMeta,
                            checks: List[Check],
                            verbose: bool):
    class MyRequestHandler(SimpleHTTPRequestHandler):
        """
        Server Stuff
        Post/Get Requests
        """

        def log_message(self, format, *args):
            with log.console_lock:
                formatted_args = ""
                if len(args) == 3:
                    formatted_args = f"{args[0]} {args[1]} {args[2]}"
                logger.debug(f"REQUEST: {formatted_args}")

        def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
            self.tool_meta = tool_meta
            self.checks = checks
            self.verbose = verbose
            self.lock = lock
            self.lock_timeout = lock_timeout

            os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../resources"))
            super().__init__(request, client_address, server)

        def handle_file_request(self):

            url_parts = urlparse(self.path)
            request_file_path = Path(url_parts.path.strip("/"))

            if not request_file_path.is_file():
                return

            content = fh.read_bytes(request_file_path)
            suffix = request_file_path.suffix.strip(".").upper()
            self.send_response(200)
            self.send_header("Content-type", ContentType[suffix].value)
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if self.path == "/":
                content = fh.read_file(Path("editor.html"))

                encoded_content = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(encoded_content)
                return

            if "getdata" in self.path:

                client_timestamp = 0

                if len(self.path.split("=")) > 1:
                    try:

                        if self.path.split("=")[1] != "undefined":
                            client_timestamp = float(self.path.split("=")[1])

                    except (TypeError, ValueError):
                        self.send_response(500)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"message": "getdata= value needs to be numeric"}).encode("utf-8"))
                        raise

                while True:
                    output_path = self.tool_meta.output
                    server_timestamp = get_newest_timestamp(output_path)
                    if server_timestamp > client_timestamp:
                        break
                    time.sleep(0.5)

                data = dict()
                try:
                    data.update(_data_to_dict(self.tool_meta, server_timestamp, self.checks))
                    json_data = json.dumps(data)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json_data.encode("utf-8"))
                except ConnectionAbortedError:
                    logger.warning(f"ConnectionAbortedError: Eine bestehende Verbindung wurde softwaregesteuert"
                                   f"durch den Hostcomputer abgebrochen")
                except json.decoder.JSONDecodeError:
                    logger.exception(f"JSONDecodeError")
                except Exception:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"message": f"Server can't send new data.\n{traceback.format_exc()}"}).encode(
                            "utf-8"))
                    raise

            elif self.path.lower().endswith((".png", ".svg", ".json", ".js", ".css", ".ico", ".jpeg", ".jpg")):
                self.handle_file_request()
                return

            else:
                self.send_response(301)
                self.send_header("Location", "/")
                self.end_headers()
                return

        def do_POST(self):
            if "/restart" in self.path:
                logger.debug("not implemented yet")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "server reload"}).encode("utf-8"))

            if "/save" in self.path:
                if self.lock.acquire(blocking=True, timeout=self.lock_timeout):
                    try:

                        length = int(self.headers['content-length'])
                        with self.rfile as f:
                            data = json.loads(f.read(length))

                        annotation_content = data["annotation"]
                        annotation_id = int(data["annotationID"])

                        model_content = data["model"]
                        model_id = int(data["modelID"])

                        options_from_client = data["options"]

                        line_limit = data["line_limit"]  # save line limit woanders

                        pel = fh.read_file(self.tool_meta.pel).splitlines()

                        word_list = data["word_list"]
                        word_list.append("")
                        for word in word_list:
                            if word in pel:
                                fh.delete_words_from_file(self.tool_meta.pel, word)
                        fh.write_lines(self.tool_meta.pwl, word_list)

                        options = dict()

                        for opts in options_from_client:
                            options.setdefault(int(opts[1]), {}).update({opts[0]: opts[2]})

                        active_statuses = data["active_statuses"]

                        for index, check in enumerate(self.checks):
                            check.active = active_statuses[index]

                            if check.id not in options:
                                continue
                            for check_options in check.options:
                                value = options[check.id][check_options]
                                value_type = check.get_option_types()[check_options]

                                if value_type == "bool":
                                    check.options.update({check_options: bool(value)})
                                if value_type == "str":
                                    check.options.update({check_options: str(value)})
                                if value_type == "int":
                                    check.options.update({check_options: int(value)})
                                if value_type == "float":
                                    check.options.update({check_options: float(value)})

                        self.tool_meta.annotations[annotation_id]["line_limit"] = line_limit
                        fh.write_file(self.tool_meta.annotations[annotation_id]["file"], annotation_content)
                        fh.write_file(self.tool_meta.models[model_id]["file"], model_content)

                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"message": "saved"}).encode("utf-8"))
                    except Exception:
                        self.send_response(500)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"message": f"An error occurred onn the server during saving the file.\n"
                                                   f"{traceback.format_exc()}"}).encode("utf-8"))
                        raise
                    finally:
                        lock.release()
                else:
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"message": f"Timeout. Couldn't save the files. Try again later"}).encode("utf-8"))
                    raise Exception("HIER läuft was schief")

            if "/fix" in self.path:
                if self.lock.acquire(blocking=True, timeout=self.lock_timeout):
                    try:
                        length = int(self.headers['content-length'])
                        with self.rfile as f:
                            data = f.read(length)
                        fix_info = (json.loads(data))
                        annotation_index = int(fix_info["annotation_index"])
                        annotation = self.tool_meta.annotations[annotation_index]["file"]
                        errors_path = self.tool_meta.annotations[annotation_index]["errors"]
                        errors = error.read_list(errors_path)

                        fixing.compute_fix_request(
                            error_id=int(fix_info["error_id"]),
                            fix_id=int(fix_info["fix_id"]),
                            fix_same=fix_info["fix_all"],
                            errors=errors,
                            annotation_file=annotation,
                            tool_meta=self.tool_meta,
                            custom_replace=fix_info["custom"])

                        self.send_response(200)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"message": "fixed"}).encode("utf-8"))
                    except Exception:
                        self.send_response(500)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"message": f"An error occurred on the server during applying fixes.\n"
                                                   f"{traceback.format_exc()}"}).encode("utf-8"))
                        raise
                    finally:
                        lock.release()
                else:
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"message": f"Timeout. Couldn't apply fixes. Try again later"}).encode("utf-8"))

            if "/check" in self.path:
                if self.lock.acquire(blocking=True, timeout=self.lock_timeout):
                    try:

                        start_checking(self.tool_meta, self.checks, self.verbose,
                                       )

                        self.send_response(200)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"message": "checked"}).encode("utf-8"))
                    except Exception:
                        self.send_response(500)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"message": f"An error occurred on the server during checking.\n"
                                                   f"{traceback.format_exc()}"}).encode("utf-8"))
                        raise
                    finally:
                        lock.release()
                else:
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"message": f"Timeout. Couldn't check the files. Try again later"}).encode("utf-8"))

    return MyRequestHandler


def _data_to_dict(tool_meta: ToolObjectsMeta, server_timestamp, checks: List[Check]):
    data = dict()

    for model in tool_meta.models:
        model_text = fh.read_file(model["file"])

        data.setdefault("models", []).append({
            "text": model_text,
            "file": model["file"],
            "locked": model["locked"]
        }
        )

    for annotation_index, annotation_dict in enumerate(tool_meta.annotations):
        errors_path = annotation_dict["errors"]
        groups_path = annotation_dict["groups"]
        groups_models_paths = annotation_dict["groups_models_paths"]

        failed_check_id = annotation_dict.get("failed_check_id", -1)

        annotation_text = fh.read_file(annotation_dict["file"])

        errors = fh.read_file(errors_path)
        groups = fh.read_file(groups_path)

        group_lists_model = [fh.read_file(path) for path in groups_models_paths]

        json_errors = list()
        json_groups = dict()
        json_group_lists_model = list()
        try:
            json_errors = json.loads(errors)
            json_groups = json.loads(groups)
            json_group_lists_model = [json.loads(group) for group in group_lists_model]
        except json.JSONDecodeError as e:
            logger.debug("Errors or groups list is empty")
            pass
        data.setdefault("annotations", []).append(
            {
                "file": annotation_dict["file"],
                "text": annotation_text,
                "errors": json_errors,
                "groups": json_groups,
                "group_lists_model": json_group_lists_model,
                "failed_check_id": failed_check_id,
                "line_limit": annotation_dict["line_limit"],
                "locked": annotation_dict["locked"]

            }
        )

    checks_list = checks
    checks_with_info = []
    for check in checks_list:
        checks_with_info.append({
            "name": check.displayed_name,
            "group": check.group.name,
            "active": check.active,
            "options": check.options,
            "doc": check.__doc__,
            "doc_html": publish_parts(check.__doc__ if check.__doc__ is not None else "", writer_name="html")[
                "html_body"],
            "id": check.id,
            "option_types": check.get_option_types(),
            "logs": check.logs,
            "disabled": check.disabled
        })

    data.update({"checks": checks_with_info})

    data.update({"last_update": server_timestamp})

    word_list = fh.read_file(tool_meta.pwl).splitlines()
    data.update({"word_list": word_list})

    return data


def sync_checking(annotation_dict: dict, domain_dict, problem_dict, checks: List[Check]) -> (
        List[Tuple[str, str]], List[Error]):
    logging_output = []

    error_path = annotation_dict["errors"]

    annotation_file = annotation_dict["file"]
    domain_file = domain_dict["file"]
    problem_file = problem_dict["file"]
    line_limit = annotation_dict["line_limit"]

    group_path = annotation_dict["groups"]
    group_domain_path = annotation_dict["groups_models_paths"][0]
    group_problem_path = annotation_dict["groups_models_paths"][1]
    logging_output.append(("info", ""))
    logging_output.append(("info", f"CHECKING: {os.path.basename(annotation_file)}".center(80, "-")))
    logging_output.append(("info", f"Annotation file: {annotation_file}"))
    logging_output.append(("info", f"Error file: {error_path}"))

    default_checks = [x for x in checks if x.group is not CheckGroup.Async and x.active]
    default_errors, current_check_id, output = compute_default_checks(annotation_file, domain_file,
                                                                      problem_file, default_checks,
                                                                      line_limit)

    logging_output.extend(output)
    annotation_dict.update({"failed_check_id": current_check_id})

    if current_check_id != -1:
        warning_string, error_string = format_warn_err(default_errors)
        warnings_count, error_count = count_warn_err_(default_errors)
        failed_check = list(filter(lambda x: x.id == current_check_id, default_checks))[0]

        logging_output.append(("warning",
                               f"Failed: {failed_check.__class__.__name__} ({error_count} {error_string}"
                               f" / {warnings_count} {warning_string})"))
        logging_output.append(("info", ""))

    write_list(error_path, default_errors)
    write_groups(group_path, [e for e in default_errors if
                              os.path.normpath(e.file_name) == os.path.normpath(annotation_dict["file"])])
    # domain errors
    write_groups(group_domain_path, [e for e in default_errors if os.path.normpath(e.file_name) == os.path.normpath(
        domain_dict["file"])])
    # problem errors
    write_groups(group_problem_path, [e for e in default_errors if
                                      os.path.normpath(e.file_name) == os.path.normpath(
                                          problem_dict["file"])])

    return logging_output, default_errors


def async_checking(annotation_dict: dict, domain_dict, problem_dict, checks: List[Check], queue, default_errors):
    annotation_file = annotation_dict["file"]
    domain_file = domain_dict["file"]
    problem_file = problem_dict["file"]
    line_limit = annotation_dict["line_limit"]

    error_path = annotation_dict["errors"]
    group_path = annotation_dict["groups"]
    group_domain_path = annotation_dict["groups_models_paths"][0]
    group_problem_path = annotation_dict["groups_models_paths"][1]

    global_checks = [x for x in checks if x.group is CheckGroup.Async and x.active]
    global_errors, output = compute_global_checks(annotation_file, domain_file,
                                                  problem_file, global_checks, line_limit)

    error_list = default_errors + global_errors

    write_list(error_path, error_list)
    write_groups(group_path, [e for e in error_list if
                              os.path.normpath(e.file_name) == os.path.normpath(annotation_dict["file"])])
    # domain errors
    write_groups(group_domain_path,
                 [e for e in error_list if os.path.normpath(e.file_name) == os.path.normpath(
                     domain_dict["file"])])
    # problem errors
    write_groups(group_problem_path, [e for e in error_list if
                                      os.path.normpath(e.file_name) == os.path.normpath(
                                          problem_dict["file"])])

    queue.put(global_checks)
    queue.put(output)
    # queue.put(global_errors)


def count_warn_err_(error_list: List[Error]):
    errors_count = len([e for e in error_list if e.error_level == ErrorLevel.Error])
    warnings_count = len([e for e in error_list if e.error_level == ErrorLevel.Warning])

    return warnings_count, errors_count


def format_warn_err(error_list: List[Error]):
    errors_count, warnings_count = count_warn_err_(error_list)

    error_number_string = "Error" if errors_count == 1 else "Errors"
    warning_number_string = "Warning" if warnings_count == 1 else "Warnings"

    return warning_number_string, error_number_string


def start_checking(tool_meta: ToolObjectsMeta, checks: List[Check], verbose: bool):
    processes = []
    queues = []
    outputs = []
    for i, annotation_dict in enumerate(tool_meta.annotations):
        logging_output, default_errors = sync_checking(annotation_dict, tool_meta.models[0],
                                                       tool_meta.models[1], checks)
        outputs.append(logging_output)
        queues.append(multiprocessing.Queue())
        processes.append(multiprocessing.Process(target=async_checking,
                                                 args=(
                                                     annotation_dict, tool_meta.models[0],
                                                     tool_meta.models[1], checks, queues[i], default_errors
                                                 )))

    for process in processes:
        process.start()

    for index, process in enumerate(processes):
        process.join()
        global_checks = queues[index].get()
        global_output = queues[index].get()

        outputs[index].extend(global_output)

        for global_check in global_checks:
            for i in range(len(checks)):
                if checks[i].id == global_check.id:
                    checks[i] = global_check

        errors = read_list(tool_meta.annotations[index]["errors"])

        if verbose:
            outputs[index].extend([("info", e.advice) for e in errors])

    for output in outputs:
        for logging_out in output:
            if logging_out[0] == "info":
                logger.info(logging_out[1])
            elif logging_out[0] == "warning":
                logger.warning(logging_out[1])
            elif logging_out[0] == "error":
                logger.error(logging_out[1])
            else:
                logger.info(logging_out[1])


def compute_global_checks(annotation_file: Path, domain_file: Path, problem_file: Path, global_checks: List[Check],
                          line_limit: int) -> (List[Error], List[Tuple[str, str]]):
    logging_output = []
    global_errors = []
    for check in global_checks:
        current_errors = []
        check.disabled = False
        try:
            current_errors = check.run(annotation_file, domain_file, problem_file, line_limit)
            if len([e for e in current_errors]) == 0:
                logging_output.append(("info", f"Passed: {check.__class__.__name__}"))
                check.logs.insert(0,f"Passed {check.__class__.__name__}\n")
            else:
                warning_string, error_string = format_warn_err(current_errors)
                warnings_count, error_count = count_warn_err_(current_errors)
                check.logs.insert(0, "")
                for er in current_errors[::-1]:
                    check.logs.insert(0, er.advice)
                check.logs.insert(0, f"The following errors were found:")
                check.logs.insert(0, f"Failed {check.__class__.__name__}")
                logging_output.append(
                    ("warning", f"Failed: {check.__class__.__name__} ({error_count} {error_string}"
                                f" / {warnings_count} {warning_string})"))

        except Exception:
            logger.warning(f"An error occurred during {check.__class__.__name__}", exc_info=True)
            check.logs.append(f"This check is disabled. Full output: \n{traceback.format_exc()}")
            check.disabled = True

        global_errors += current_errors
    logging_output.append(("info", ""))
    return global_errors, logging_output


def compute_default_checks(annotation_file: Path, domain_file: Path, problem_file: Path, default_checks,
                           line_limit: int):
    logging_output = []
    errors_default = []

    # create default error list from default checkers

    current_failed_check_id = -1

    for check in default_checks:
        check.disabled = False
        current_failed_check_id = check.id
        current_errors = []
        try:
            current_errors.extend(check.run(annotation_file, domain_file, problem_file, line_limit))
        except Exception:
            logger.warning(f"An error occurred during {check.__class__.__name__}", exc_info=True)
            check.logs.append(f"\nThis check is disabled. Full output:\n{traceback.format_exc()}")
            check.disabled = True
            continue

        if len([e for e in current_errors if e.error_level is not ErrorLevel.Warning]) == 0:
            logging_output.append(("info", f"Passed: {check.__class__.__name__}"))
            check.logs.insert(0,f"Passed {check.__class__.__name__}\n")
            errors_default += current_errors
            continue
        else:
            check.logs.insert(0, "")
            for er in current_errors[::-1]:
                check.logs.insert(0, er.advice)
            check.logs.insert(0, f"The following errors were found:")
            check.logs.insert(0, f"Failed {check.__class__.__name__}")

        errors_default += current_errors
        break

    if len([e for e in errors_default if e.error_level is not ErrorLevel.Warning]) == 0:
        current_failed_check_id = -1

    return errors_default, current_failed_check_id, logging_output
