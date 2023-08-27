import pytest
from os.path import join, dirname, abspath
from acheck.config import config


@pytest.fixture()
def test_dir():
    return join(dirname(abspath(__file__)), "test_files")


@pytest.fixture()
def symbol_regex():
    return config.load()["Annotation"]["regex_characters"]


@pytest.fixture()
def time_regex():
    return config.load()["Annotation"]["regex_time"]


@pytest.fixture()
def expression_structure_regex():
    return config.load()["Annotation"]["regex_expression_structure"]
