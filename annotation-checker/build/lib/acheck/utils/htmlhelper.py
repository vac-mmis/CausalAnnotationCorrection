from typing import List

from acheck.checking.error import Error


def linec(inner_html: str):
    """
    htmlwith class line
    :param inner_html:
    :return:
    """
    return f"<div class=\"line\"><span class=\"line-number\"></span>{inner_html}</div>"


def marked(inner_text: str, error_id: str):

    return f"<span data-id=\"{error_id}\" class=\"marked\">{inner_text}</span>"


def build_line(line: str, error_groups: dict, error_list: List[Error]):
    inner_html = ""
    current_index = 0
    for indexes, errors in error_groups.items():
        inner_html += line[current_index:indexes[0]]
        inner_html += marked(line[indexes[0]:indexes[1]], ";".join([str(error_list.index(x)) for x in errors]))
        current_index = indexes[1]
    inner_html += line[current_index:]
    return linec(inner_html)
