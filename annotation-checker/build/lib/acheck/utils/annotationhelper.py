import csv
from pathlib import Path
from typing import List
import logging
from acheck.config import config

logger = logging.getLogger(__name__)



def parse_annotation(infile, line_limit):
    csv_delimiter = config.load("Annotation","csv_delimiter")
    times = []
    delimiter = []
    expressions = []
    try:
        with open(infile, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            line_counter = 0

            for line in reader:
                if line_limit != -1 and line_counter == line_limit + 1:
                    break


                if len(line) == 1:
                    line = [line[0], ""]
                    delimiter.append("")
                if len(line) == 0:
                    line = ["", ""]
                    delimiter.append("")
                else:
                    delimiter.append(csv_delimiter)
                times.append(line[0])
                expressions.append(line[1])
                line_counter += 1

        return times, delimiter, expressions
    except IndexError as e:
        logger.error(e)
    except IOError as e:
        logger.error(e)
    except csv.Error as e:
        logger.error(e)


def read_annotation(infile, line_limit = -1) -> List[str]:
    a, b, c = parse_annotation(infile, line_limit)
    if line_limit == -1:
        return [q + w + e for q, w, e in zip(a, b, c)]
    return [q + w + e for q, w, e in zip(a, b, c)][0:line_limit + 1]


def write_annotation(annotation_list, outfile) -> None:
    try:
        with open(outfile, 'w') as f:
            for line_number,line in enumerate(annotation_list):
                if line_number == len(annotation_list)-1:
                    f.write(f'{line}')
                else:
                    f.write(f'{line}\n')
    except IOError as e:
        logger.error(e)
        raise


def collapse_subsequence(infile, outfile):
    new_list = []
    try:
        with open(infile, "r") as f:
            lines = f.readlines()
            line_old = ","
            for line in lines:
                if line.split(",")[1] != line_old.split(",")[1]:
                    new_list.append(line)
                line_old = line
            f.close()
    except IOError as e:
        logger.error(e)
        raise
    try:
        with open(outfile, "w+") as g:
            g.writelines(new_list)
            g.close()
    except IOError as r:
        logger.error(r)
        raise


def time_to_line_number(annotation: Path, time: float, line_limit) -> int:
    times, _, _ = parse_annotation(annotation, line_limit)

    if len([times.index(t) for t in times if float(t) == float(time)]) > 0:
        return [times.index(t) for t in times if float(t) == float(time)][0] + 1
    return -1


def get_plan(annotation: Path, line_limit, add_finished: bool = True, ) -> List[str]:
    parsed_annotation = list(zip(*parse_annotation(annotation, line_limit)))

    last_line_values = parsed_annotation[-1]
    last_time_value = last_line_values[0]

    plan = []
    for time, _, expression in parsed_annotation:
        expression = expression.replace("-", " ")
        plan.append(f"{time}: ({expression})")

    if add_finished:
        plan.append(f"{float(last_time_value) + 4000}: (get_done)")

    return plan


if __name__ == '__main__':
    pass
