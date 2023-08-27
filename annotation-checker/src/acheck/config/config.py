import os.path
import typing
import toml
import logging
from os.path import exists
from acheck import constants

logger = logging.getLogger(__name__)


def init():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.CONFIG_NAME)
    if not exists(config_path):
        try:
            with open(config_path, "w+") as config_file:
                toml.dump(constants.DEFAULT_CONFIG, config_file)
        except IOError as e:
            logger.error(e)


def reset_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.CONFIG_NAME)

    try:
        with open(config_path, "w+") as config_file:
            toml.dump(constants.DEFAULT_CONFIG, config_file)
    except IOError as e:
        logger.error(e)


def load(*configs: str,
         file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       constants.CONFIG_NAME)) -> typing.MutableMapping:
    try:
        init()
        with open(file_path, "r") as f:
            current = toml.load(f)

            for key in configs:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    reset_config()
                    logger.warning("Access to an element that does not exist in config. Config was reset")
                    return load(*configs)
            return current

    except IOError as e:
        logger.error(e)


def change(*config, value, file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         constants.CONFIG_NAME)):
    try:
        with open(file_path, "r") as f:
            config_data = toml.load(f)
            current = config_data

            for key in config[:-1]:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return False

            last_key = config[-1]
            if isinstance(current, dict) and last_key in current:
                current[last_key] = value
                write(config_data)
                logger.info("The configuration was changed")
                return True
            else:
                return False

    except IOError as e:
        logger.error(e)


def write(config_data):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.CONFIG_NAME)
    try:
        init()

        with open(config_path, "w") as f:
            toml.dump(config_data, f)
    except IOError as e:
        logger.error(e)


def import_config(file_path):
    try:
        with open(file_path, "r") as f:

            config_data = toml.load(f)
            write(config_data)

    except IOError as e:
        logger.error(e)


def export_config(file_path):
    config_data = load()
    try:
        with open(file_path, "w+") as f:

            toml.dump(config_data, f)

    except IOError as e:
        logger.error(e)
