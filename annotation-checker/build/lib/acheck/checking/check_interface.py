import logging
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Union
from acheck.checking.error import Error

logger = logging.getLogger(__name__)
"""Register logging"""


class CheckGroup(Enum):
    """Separating checks into different groups with different behavior."""

    PreStart = 0,
    """
    PreStart checks are evaluated before the program starts. Such as file reading. 
    Checks in this group will be running one by one. PreStart Checks will also be added to the Default group.
    """
    Default = 2,
    """
    Checks in this group are executed one after another. If a check throws an error, the loop will stop. 
    It will move on if all error thrown by the actual checker are fixed.
    """
    Async = 3
    """
    Checks in this group will always run next to every check in the Default group. Such as spell checking.
    """


@dataclass
class ToolObjectsMeta:
    """
    Holds all information about all needed file paths and names

    :param Path output: The output path for the folder structure of the working copy, defaults to None
    :param List[Dict] annotations: A list of all annotation objects
    :param List[Dict] models: A list of all model objects
    :param Path pwl: The path for the personal words list of the spelling corrector
    :param Path pel: The path for the excluded words list of the spelling corrector
    :param Path signatures: The path of the signature file that stores the signature marked as correct for each action.
    :param Path validator: The path of the plan validator executable.
    """
    output: Path = None
    annotations: List[Dict] = field(default_factory=list)
    models: List[Dict] = field(default_factory=list)
    pwl: Path = None
    pel: Path = None
    signatures: Path = None
    validator: Path = None


class Check(ABC, metaclass=ABCMeta):
    """
    This is an interface for creating checks

    :ivar int id: This id is necessary to identify the checks in the tool, it is assigned automatically when creating the check. Defaults to "-1".
    :ivar List[str] logs: A list to pass additional outputs to the tool. Defaults to "[]".

    :param ToolObjectsMeta tool_meta: (Instance Attribute) A current instance of a ToolObjectsMeta object, which was initiated in the main script.
    :param check_interface.CheckGroup group: A group to differentiate between the checks' behavior.
    :param str displayed_name: (Instance Attribute) A custom name that will be displayed in the tool.
    :param bool active: Activates the check in the tool directly, the check can be deactivated in the tool. Defaults to "true".
    :param bool disabled: If this attribute is True, the check is disabled in the tool and cannot be used. This usually happens when certain requirements are not met to run the check correctly, e.g. third party software. If the run method raises an exception this also will be set to True.
    :param Dict[str, Union[str,bool,int,float]] options: All additional arguments that the check requires specifically for itself are stored here.

    :Options:
        Each option can be either of type str, bool, int or float. Generally all additional attributes defined in the check class are automatically converted into an option. However, all options with value can also be set by default when initializing the check.
    """

    def __init__(self, tool_meta: ToolObjectsMeta,
                 group: CheckGroup,
                 displayed_name: str = None,
                 active: bool = True,
                 disabled: bool = False,
                 options: Dict[str, Union[str, bool, int, float]] = None):
        if options is None:
            options = dict()
        if displayed_name is None:
            displayed_name = self.__class__.__name__

        self.active = active
        self.disabled = disabled
        self.displayed_name = displayed_name
        self.id = -1
        self.group = group
        self.logs = []
        self.options = options
        self.tool_meta = tool_meta

        check_options = [attr for attr in dir(self) if
                         not callable(getattr(self, attr)) and not attr.startswith("__")]

        self.options.update({x: getattr(self, x) for x in check_options if
                             x not in ['_abc_impl', 'active', 'disabled', 'options',
                                       'tool_meta', 'displayed_name', 'logs', 'group', 'id']})

        self.options.update(options)

    @abstractmethod
    def run(self, annotation: Path, domain: Path, problem: Path, line_limit: int = -1) -> List[Error]:
        """
        Start the check. All checks must inherit from this abstract class and need to implement their own run() method.

        :param Path annotation: Path of the annotation file
        :param Path problem: Path of the domain file
        :param Path domain: Path of the problem file
        :param int line_limit: Limits the check of the annotation up to a certain line. Defaults to "-1".

        :return: A list containing all the errors that were found during the check.
        :rtype: List[Error]
        """
        raise NotImplementedError

    def get_option_types(self):
        """
        A function that checks if all arguments have an appropriate type. Otherwise, it raises an error.
        Allowed typed are: `int`, `str`, `bool`, `float`.

        :return: A dictionary containing all extra arguments.
        :rtype: Dict[str, Union[str,bool,int,float]]
        :raises TypeError: If arguments are not of type int, str, float or bool.
        """
        options = dict()
        for opt, value in self.options.items():
            if isinstance(value, bool):
                options.update({opt: "bool"})
                continue
            if isinstance(value, int):
                options.update({opt: "int"})
                continue
            if isinstance(value, float):
                options.update({opt: "float"})
                continue
            if isinstance(value, str):
                options.update({opt: "str"})
                continue

            logger.exception(
                TypeError(f"{self.__class__.__name__} Arguments must be of type int,str,float or bool. {opt} is of "
                          f"type: {type(opt)}"))
        return options

    def get_option_as_config(self,option:str,value:str):
        """
        A function that checks if all arguments have an appropriate type. Otherwise, it raises an error.
        Allowed typed are: `int`, `str`, `bool`, `float`.

        :return: A dictionary containing all extra arguments.
        :rtype: Dict[str, Union[str,bool,int,float]]
        :raises TypeError: If arguments are not of type int, str, float or bool.
        """
        options = dict()
        for opt, value in self.options.items():
            if isinstance(value, bool):
                options.update({opt: "bool"})
                continue
            if isinstance(value, int):
                options.update({opt: "int"})
                continue
            if isinstance(value, float):
                options.update({opt: "float"})
                continue
            if isinstance(value, str):
                options.update({opt: "str"})
                continue

            logger.exception(
                TypeError(f"{self.__class__.__name__} Arguments must be of type int,str,float or bool. {opt} is of "
                          f"type: {type(opt)}"))
        return options
