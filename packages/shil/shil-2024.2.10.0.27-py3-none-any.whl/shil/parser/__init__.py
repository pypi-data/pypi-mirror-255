""" shil.parser 
"""

import tatsu
from fleks.util import lme

from .grammar import bashParser
from .semantics import Semantics

LOGGER = lme.get_logger(__name__)


def fmt(text, filename="?"):
    """ """
    semantics = Semantics()
    parser = bashParser()
    try:
        parsed = parser.parse(
            text,
            parseinfo=True,
            filename=filename,
            semantics=semantics,
        )
    except (tatsu.exceptions.FailedParse,) as exc:
        LOGGER.critical(exc)
        return text
    else:
        out = []
        for item in parsed:
            if isinstance(item, (list, tuple)):
                item = " ".join([str(x) for x in item])
            out.append(item)
        head = out.pop(0)
        # tail=out.copy()
        tail = "\n  ".join(out)
        return f"{head} {tail}"


shfmt = fmt
