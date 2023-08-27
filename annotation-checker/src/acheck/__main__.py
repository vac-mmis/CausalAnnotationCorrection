import logging
import os
import shutil
import threading
import time
from pathlib import Path
from os.path import join
from typing import List
import acheck.server
from acheck import constants
from acheck.checking.check_interface import CheckGroup, ToolObjectsMeta, Check
from acheck.checking.error import Error
from acheck.checkers import register_checks
from acheck.config import config
import argparse
import sys

from acheck.utils import filehelper as fh
from acheck.server import MyServer

logger = logging.getLogger(__name__)
"""Register logging"""


def main():
    """Init tool meta object"""
    tool_meta = ToolObjectsMeta()

    configure_logging(logging.INFO)

    """Parsing command line arguments"""
    parser = argparse.ArgumentParser(
        prog="acheck",
        description="checking for errors in annotations files based on a given domain",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=""
    )
    subparsers = parser.add_subparsers(title="Commands", metavar="", dest="command")

    """Setting up the config parser"""
    parser_config = subparsers.add_parser("config", help="Customize the tool settings")
    parser_config.add_argument("-i",metavar="--import", help="Load a locally modified config file into the tool",type=file_path)
    parser_config.add_argument("-e", metavar="--export", help="Copy the config file of the tool", type=file_path)
    parser_config.add_argument("-v", metavar="--validator", help="Enter the path to the validator executable",
                               type=file_path)
    parser_config.add_argument("-l", metavar="--language", help="enter the langauge like f.e. en_US",
                               type=str)

    """Setting the standard check parser"""
    parser_check = subparsers.add_parser("check", help="Starts the application")

    parser_check.add_argument("domain", metavar="<domain>", help="Enter the domain file", type=file_path)
    parser_check.add_argument("problem", metavar="<problem>", help="Enter the problem file", type=file_path)
    parser_check.add_argument("annotation", metavar="<annotation>", help="Enter one or multiple annotation files",
                              nargs="*",
                              type=file_path)
    parser_check.add_argument("-o", "--output", metavar="<directory>", help="Specify the port a custom output folder",
                              type=dir_path)
    parser_check.add_argument("-l", "--lock", metavar="<file>",
                              help="lock files in the editor to make them uneditable",
                              nargs="*",
                              type=file_path)
    parser_check.add_argument("-m", "--multi", metavar="<directory>",
                              help="Enter a directory of annotations to load all files at once ",
                              type=dir_path)
    parser_check.add_argument("-p", "--port", metavar="<port>", help="Specify the port", type=int,
                              default=constants.STANDARD_PORT)
    parser_check.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
    parser_check.add_argument("-d", "--debug", help="See debug logging", action="store_true", default=False)

    noguiGroup = parser_check.add_mutually_exclusive_group()
    noguiGroup.add_argument("-n", "--nogui", help="For command line use with backup", action="store_true",
                            default=False)
    noguiGroup.add_argument("-i", "--inplace", help="Work on the original files without backup", action="store_true",
                            default=False)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit()

    """Configure config from config arguments"""
    if args.command == "config":
        if args.i:
            config.import_config(args.i)
            logger.info(f"Loaded the config from: {os.path.abspath(args.i)}")
        elif args.e:
            config.export_config(args.e)
            logger.info(f"Copied the config to: {os.path.abspath(args.e)}")
        elif args.v:
            config.change("Validator","path",value=os.path.abspath(args.v))
        elif args.l:
            config.change("Annotation","lang",value=args.l)

        """Exit on config command"""
        sys.exit()

    """Provide at least 1 annotation file"""
    if not args.annotation and args.multi is None:
        parser.error("The annotation file is missing")

    annotation_files = []
    locked_files = []

    """Configure logging level"""

    if args.debug:

        configure_logging(logging.DEBUG)

    """Register `multi` argument"""
    if args.multi:
        for file in os.listdir(args.multi):
            if file.endswith(".csv"):
                annotation_files.append(os.path.abspath(os.path.join(args.multi, file)))
    else:
        annotation_files = args.annotation
        locked_files = args.lock

    if args.output:

        output_directory = os.path.abspath(args.output)
    else:
        output_directory = os.path.abspath(constants.OUTPUT)

    """creating output directory"""
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    """create port specific server files"""
    if args.inplace:
        output_directory_with_port = os.path.join(output_directory, "inplace")
    else:
        output_directory_with_port = os.path.join(output_directory, str(args.port))
    if not os.path.exists(output_directory_with_port):
        os.mkdir(output_directory_with_port)

    output_directory = output_directory_with_port

    tool_meta.output = output_directory

    """create config if not exist already"""
    logger.debug("initializing config file")
    config.init()

    logger.info(f"Output: {output_directory}")

    """checking domain problem and annotation files"""
    for a_file in annotation_files:
        pre_checks_list = [x for x in register_checks(None) if
                           x.group is CheckGroup.PreStart]
        pre_start_checking(annotation_file=a_file, domain_file=os.path.abspath(args.domain),
                           problem_file=os.path.abspath(args.problem), checks_list=pre_checks_list)

    """backup for all annotation files"""
    for index, a_file in enumerate(annotation_files):
        annotation_dict = {}

        a_dir = os.path.join(output_directory, os.path.abspath(a_file).replace("/", "-").replace("\\", "-"))

        if not os.path.exists(a_dir):
            os.mkdir(a_dir)

        if args.inplace:
            annotation = a_file
        else:
            if not os.path.exists(os.path.join(a_dir, os.path.split(a_file)[-1])):
                shutil.copy(a_file, os.path.join(a_dir, os.path.split(a_file)[-1]))
            annotation = os.path.join(a_dir, os.path.split(a_file)[-1])

        fh.create_file_if_not_exist(Path(join(a_dir, constants.ERROR_FILE_NAME)), content="[]")
        fh.create_file_if_not_exist(Path(join(a_dir, constants.GROUP_FILE_NAME)), content="[]")
        fh.create_file_if_not_exist(Path(join(a_dir, constants.GROUP_DOMAIN_FILE_NAME)), content="[]")
        fh.create_file_if_not_exist(Path(join(a_dir, constants.GROUP_PROBLEM_FILE_NAME)), content="[]")
        fh.create_file_if_not_exist(Path(join(a_dir, constants.PLAN_FILE_NAME)))

        annotation_dict.update({"locked": False})
        if locked_files:
            if a_file in locked_files:
                annotation_dict.update({"locked": True})

        annotation_dict.update({"file": annotation})
        annotation_dict.update({"errors": join(a_dir, constants.ERROR_FILE_NAME)})
        annotation_dict.update({"groups": join(a_dir, constants.GROUP_FILE_NAME)})
        annotation_dict.update({"groups_models_paths": [join(a_dir, constants.GROUP_DOMAIN_FILE_NAME),
                                                        join(a_dir, constants.GROUP_PROBLEM_FILE_NAME)]})

        annotation_dict.update({"plan": join(a_dir, constants.PLAN_FILE_NAME)})
        annotation_dict.update({"current_check": ""})
        annotation_dict.update({"line_limit": -1})

        tool_meta.annotations.append(annotation_dict)

    """backup for domain and problem files"""
    old_domain = os.path.abspath(args.domain)
    old_problem = os.path.abspath(args.problem)

    if not args.inplace:
        if not os.path.exists(os.path.join(output_directory, os.path.split(old_domain)[-1])):
            shutil.copy(old_domain, os.path.join(output_directory, os.path.split(old_domain)[-1]))

        if not os.path.exists(os.path.join(output_directory, os.path.split(old_problem)[-1])):
            shutil.copy(old_problem, os.path.join(output_directory, os.path.split(old_problem)[-1]))

        domain = os.path.join(output_directory, os.path.split(old_domain)[-1])
        problem = os.path.join(output_directory, os.path.split(old_problem)[-1])
    else:
        domain = old_domain
        problem = old_problem

    domain_dict = {
        "file": domain,
        "locked": False
    }
    if locked_files:
        if args.domain in locked_files:
            domain_dict.update({"locked": True})

    tool_meta.models.append(domain_dict)

    problem_dict = {
        "file": problem,
        "locked": False
    }
    if locked_files:
        if args.problem in locked_files:
            problem_dict.update({"locked": True})
    tool_meta.models.append(problem_dict)

    """creating paths for spellcheck files and signatures"""
    pwl = join(output_directory, constants.PERSONAL_WORD_LIST)
    pel = join(output_directory, constants.PERSONAL_EXCLUDE_LIST)
    signatures = join(output_directory, constants.SIGNATURE_FILE)

    fh.create_file_if_not_exist(Path(pwl))
    fh.create_file_if_not_exist(Path(pel))
    fh.create_file_if_not_exist(Path(signatures), content="{}")

    tool_meta.pel = pel
    tool_meta.pwl = pwl
    tool_meta.signatures = signatures

    tool_meta.validator = config.load("Validator","path")

    """registering all checks"""
    checks = register_checks(tool_meta=tool_meta)

    if args.nogui or args.inplace:

        last_checked = acheck.server.get_newest_timestamp(os.path.dirname(os.path.dirname(output_directory)))
        acheck.server.start_checking(tool_meta, checks, args.verbose)
        while True:
            if last_checked < acheck.server.get_newest_timestamp(os.path.dirname(os.path.dirname(output_directory))):
                acheck.server.start_checking(tool_meta, checks, args.verbose)
                last_checked = acheck.server.get_newest_timestamp(os.path.dirname(os.path.dirname(output_directory)))
            time.sleep(0.5)

    """starting the server"""
    lock = threading.Lock()

    lock_timeout = constants.THREADING_LOCK_TIMEOUT
    with MyServer(("127.0.0.1", args.port), lock, lock_timeout, tool_meta, checks, args.verbose) as s:
        try:
            logger.info(f"Server is serving on port {s.server_address}")  # Output
            s.serve_forever()
        except KeyboardInterrupt:
            s.shutdown()
            sys.exit()


def pre_start_checking(annotation_file: Path, domain_file: Path, problem_file: Path, checks_list: List[Check]):
    checks_list_pre = [x for x in checks_list if x.group is CheckGroup.PreStart]

    for check in checks_list_pre:
        _return_on_error(check.run(annotation_file, domain_file, problem_file))


def _return_on_error(error_list: List[Error]):
    if len(error_list) > 0:
        for error in error_list:
            logger.warning(error.advice)
        sys.exit()


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"\'{path}\' is not a valid directory")


def file_path(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"\'{path}\' is not a valid file")


def configure_logging(level):
    logging.basicConfig(
        format="[%(threadName)s] %(name)s %(levelname)-8s %(message)s",
        level=level
    )


if __name__ == '__main__':
    main()
