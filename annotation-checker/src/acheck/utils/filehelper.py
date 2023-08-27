from os.path import exists
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def create_file(file_name, content: str = None):
    try:
        with open(file_name, "w+", encoding="utf-8") as file:
            if content:
                file.write(content)
            file.close()
    except (IOError, OSError) as e:
        logger.error(e)
        raise


def create_file_if_not_exist(file_name: Path, content: str = None):
    try:
        if not exists(file_name):
            with open(file_name, "w+", encoding="utf-8") as file:
                if content:
                    file.write(content)
                file.close()
    except (IOError, OSError) as e:
        logger.error(e)
        raise


def delete_words_from_file(filename, word):
    try:
        with open(filename, 'r+') as file:
            lines = file.readlines()
            file.seek(0)  # Gehe zum Anfang der Datei

            for line in lines:
                if line.strip() != word:
                    file.write(line)

            file.truncate()  # Kürze die Datei auf die neue Größe

    except (IOError, OSError) as e:
        logger.exception(e)


def write_unique_words_to_file(filename, word):
    try:

        with open(filename, 'a+') as file:
            file.seek(0)  # Gehe zum Anfang der Datei
            existing_words = set(file.read().splitlines())
            file.seek(0, 2)  # Gehe ans Ende der Datei (a+ Modus)
            if word not in existing_words:
                file.write(word + '\n')

    except (IOError, OSError) as e:
        logger.exception(e)


def read_file(file_name: Path):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
    except (IOError, OSError) as e:
        logger.error(e)
        raise


def write_file(file_name: Path, data: str):
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data)
    except (IOError, OSError) as e:
        logger.error(e)
        raise


def write_lines(file_name: Path, data: List[str]):
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.writelines(u"\n".join(data))
    except (IOError, OSError) as e:
        logger.error(e)
        raise


def read_bytes(file_name: Path):
    try:
        with open(file_name, "rb") as file:
            return file.read()
    except (IOError, OSError) as e:
        logger.error(e)
        raise
