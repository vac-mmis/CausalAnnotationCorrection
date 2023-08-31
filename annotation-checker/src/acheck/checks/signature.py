import json
from pathlib import Path
from typing import List, Tuple
from acheck.checking.check_interface import Check
from acheck.checking.error import Error, ErrorType, Fix, FixCode, Sequence
from acheck.config import config
from acheck.utils.annotationhelper import parse_annotation
from acheck.utils import filehelper as fh


class SignatureCheck(Check):
    """Check for the occurring of multiple different signature descriptions for the same action

    As a fix you can select one signature as the right one and only all other descriptions will give you an error
    e.g.

    "hold-manual-both" -> hold takes two arguments -> signature of 2
    "hold-manual-both-right" -> hold takes three arguments -> signature of 3

    If you select a signature of 2 for hold, "hold-manual-both-right" and all different signatures
    will give you an error.
    """

    def run(self,annotation_file,domain_file,problem_file,line_limit = -1) -> List[Error]:
        self.logs.clear()
        signatures_file = self.tool_meta.signatures
        return self._check_signatures(annotation=annotation_file,
                                     signature_file=signatures_file,
                                     check_id=self.id,
                                     line_limit=line_limit)

    @staticmethod
    def _check_signatures(annotation: Path, signature_file: Path, check_id,line_limit):
        errors = []

        times, divs, expressions = parse_annotation(annotation,line_limit)

        active_signatures = json.loads(fh.read_file(signature_file))

        signatures_by_line = _get_signatures(annotation,line_limit)
        duplicate_signatures = _get_duplicates(signatures_by_line)

        for line, action, signature in signatures_by_line:
            if action not in duplicate_signatures.keys():
                continue
            active_signature = active_signatures.get(action)

            fixes = []

            if active_signature is not None:
                if int(signature) == int(active_signature):
                    continue
                fixes.append(Fix(fix_code=FixCode.Alert,
                                 correct_string=f"Change number of parameters for '{action}' to '{active_signature}' or "
                                                f"change the action description inside the model."))
            fixes.append(Fix(fix_code=FixCode.WhitelistSignature,
                             correct_string=f"{action}/{signature}"))

            errors.append(
                Error(
                    file_name=annotation,
                    error_type=ErrorType.IllegalSignature,
                    line_number=line,
                    incorrect_sequence=Sequence(start_index=len(times[line - 1]) + len(divs[line - 1]),
                                                char_sequence=expressions[line - 1]),
                    fixes=fixes,
                    check_id=check_id
                )
            )

        return errors


def _get_signatures(annotation: Path,line_limit) -> List[Tuple[int, str, int]]:
    signatures = []

    times, divs, expressions = parse_annotation(annotation,line_limit)
    term_divider = config.load("Annotation","term_divider")
    for index, exp in enumerate(expressions, start=1):
        if exp != "":
            literals = exp.split(term_divider)
            action = literals[0]
            signatures.append((index, action, len(literals[1:])))
        else:
            signatures.append((index, "", 0))

    return signatures


def _get_duplicates(signatures: List[Tuple[int, str, int]]):
    duplicates = {}
    for line, action, signature in signatures:
        duplicates.setdefault(action, set()).add(signature)
    return {x: y for x, y in duplicates.items() if len(y) > 1}
