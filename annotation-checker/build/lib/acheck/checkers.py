import itertools

from acheck.checking.check_interface import CheckGroup
from acheck.checks.file import ReadFileCheck, CSVFormatCheck, CharacterCheck
from acheck.checks.objects import ActionCheck, WorldObjectsCheck
from acheck.checks.signature import SignatureCheck
from acheck.checks.spelling import SpellCheck
from acheck.checks.structure import TimeIsNumberCheck, TimeAscendingCheck, ExpressionStructureCheck
from acheck.checks.validating import PlanValidationCheck, PDDLSyntaxCheck


def register_checks(tool_meta):
    """
    In this list all checks must be registered which run continuously, i.e. which belong to the check group async.
    Feel free to edit and mess around with your own checks.
    """
    async_checks = [

        # Add, remove or edit checks inside here
        SpellCheck(
            group=CheckGroup.Async,
            tool_meta=tool_meta,
        ),
        PDDLSyntaxCheck(
            group=CheckGroup.Async,
            tool_meta=tool_meta,
        ),
    ]

    """
    In this list all checks must be registered which run sequentially, i.e. which belong to the check group default.
    Feel free to edit and mess around with your own checks.
    """
    default_checks = [

        # Add, remove or edit checks inside here
        ReadFileCheck(
            group=CheckGroup.PreStart,
            tool_meta=tool_meta,
        ),
        CSVFormatCheck(
            group=CheckGroup.PreStart,
            tool_meta=tool_meta,
            options={"sniffer_size": 32768},
        ),
        CharacterCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),
        TimeIsNumberCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),
        TimeAscendingCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
            options={"strict": True}
        ),
        ExpressionStructureCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),

        ActionCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),
        WorldObjectsCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),
        SignatureCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),
        PlanValidationCheck(
            group=CheckGroup.Default,
            tool_meta=tool_meta,
        ),
    ]

    """Each check gets its id assigned automatically.
    DO NOT TOUCH ANYTHING DOWN HERE.
    """
    checks = async_checks + default_checks
    # Registering incrementing id's for each check, so errors can be identified better
    id_iter = itertools.count()
    for check in checks:
        check.id = next(id_iter)

    return checks
