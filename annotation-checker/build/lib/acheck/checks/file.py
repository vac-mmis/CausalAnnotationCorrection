import csv
import logging
import re
import string
from pathlib import Path
from typing import List
from acheck.config import config
from acheck.utils.annotationhelper import parse_annotation
from acheck.checking.check_interface import Check
from acheck.checking.error import ErrorType, Error, FixCode, Fix, Sequence

logger = logging.getLogger(__name__)


class CSVFormatCheck(Check):
    """Checks whether the given annotation file has a valid csv format

    :Options:
        - sniffer_size:
            Size parameter for reading the file and determine the csv dialect (e.g. "file_size=4096")
        - columns:
            Number of columns in the csv file
        - quotechar:
            Quotechar of the csv file
        - delimiter:
            Delimiter char of the csv file
    """
    sniffer_size = config.load("Annotation","csv_sniffer_size")
    columns = config.load("Annotation","csv_columns")
    quotechar = config.load("Annotation","csv_quotechar")
    delimiter = config.load("Annotation","csv_delimiter")

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()
        return self.check_csv_structure(annotation_file,
                                        sniffer_size=self.options.get("sniffer_size", self.sniffer_size),
                                        columns=self.options.get("columns", self.columns),
                                        delimiter=self.options.get("delimiter", self.quotechar),
                                        quotechar=self.options.get("quotechar", self.delimiter),
                                        check_id=self.id)

    @staticmethod
    def check_csv_structure(file_name: Path, sniffer_size: int, check_id: int, columns=2, delimiter=",", quotechar='|'):

        try:
            with open(file_name, 'r', newline='') as csvfile:
                data = csvfile.read(sniffer_size)

                if not all([c in string.printable or c.isprintable() for c in data]):
                    return [Error(
                        file_name=file_name,
                        error_type=ErrorType.IllegalCSVFile,
                        fixes=[Fix(f"Found not printable elements", fix_code=FixCode.Alert)],
                        check_id=check_id,
                    )]
                csvfile.seek(0)
                reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
                errors = []
                for index, row in enumerate(reader):

                    if len(row) != columns and len(row) > 0 or len(row) == 0:
                        errors.append(Error(
                            file_name=file_name,
                            error_type=ErrorType.IllegalCSVFile,
                            line_number=index + 1,
                            fixes=[Fix(f"Illegal number of columns", fix_code=FixCode.Alert)],
                            check_id=check_id,
                        ))

                return errors
        except (IOError, OSError, UnicodeError, csv.Error) as e:
            logger.exception(e)
            return [
                Error(
                    file_name=file_name,
                    error_type=ErrorType.IllegalCSVFile,
                    fixes=[Fix(str(e), fix_code=FixCode.Alert)],
                    check_id=check_id,
                )
            ]


class ReadFileCheck(Check):
    """Checks if there are any issues during reading the file by opening it"""

    @staticmethod
    def check_open_file(*infile, check_id):

        for file in infile:

            file_error = Error(file, ErrorType.IllegalFile, check_id, fixes=[Fix("Can't open the file")])
            try:
                with open(file, "r") as f:
                    f.close()
                    return []

            except (IOError, OSError) as e:
                file_error.advice = f"{repr(e)}: {infile}"
                logger.error(e)
                return [file_error]

    def run(self, annotation_file, domain_file, problem_file, line_limit=-1) -> List[Error]:
        self.logs.clear()
        return self.check_open_file(domain_file, problem_file, annotation_file, check_id=self.id)


class CharacterCheck(Check):
    """Checks if there are any characters that are not allowed

    :Options:
        - regex_characters:
            The regular expression that matches all allowed characters for the whole annotation
        - regex_time:
            The regular expression that matches all allowed characters plus the punctuation mark period
    """
    regex_characters = config.load("Annotation","regex_characters")
    regex_time = config.load("Annotation","regex_time")

    def run(self, annotation_file, domain_file, problem_file, line_limit: int = -1) -> List[Error]:
        self.logs.clear()
        return self.check_characters(annotation_file=annotation_file,
                                  check_id=self.id,
                                  regex_characters=self.options.get("regex_characters", self.regex_characters),
                                  regex_time=self.options.get("regex_time", self.regex_time),
                                  line_limit=line_limit
                                  )

    @staticmethod
    def check_characters(annotation_file, check_id, regex_characters, regex_time, line_limit) -> List[Error]:
        error_list = []
        times, divs, expressions = parse_annotation(annotation_file, line_limit)

        p_symbols = re.compile(regex_characters)
        p_time_symbols = re.compile(regex_time)
        for index, (time, div, exp) in enumerate(zip(times, divs, expressions), start=1):

            if (time + div + exp).strip() == "":
                continue
            for m in p_time_symbols.finditer(time):
                error_list.append(
                    Error(
                        annotation_file,
                        incorrect_sequence=Sequence(m.start(), m.group()),
                        fixes=[Fix(fix_code=FixCode.RemoveSequence)],
                        error_type=ErrorType.IllegalCharacter,
                        line_number=index,
                        check_id=check_id,
                    )
                )
            for n in p_symbols.finditer(div + exp):
                error_list.append(
                    Error(
                        annotation_file,
                        incorrect_sequence=Sequence(len(time) + n.start(), n.group()),
                        fixes=[Fix(fix_code=FixCode.RemoveSequence)],
                        error_type=ErrorType.IllegalCharacter,
                        line_number=index,
                        check_id=check_id
                    )
                )
        return error_list
