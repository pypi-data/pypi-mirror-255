""" shil.util
"""

import functools

from fleks.util import lme

LOGGER = lme.get_logger(__name__)


def invoke(*args, **kwargs):
    """ """
    from shil.models import Invocation

    if args:
        if len(args) == 1 and "command" not in kwargs:
            command = args[0]
            assert isinstance(command, (str,)), f"expected string, got {type(command)}"
            kwargs.update(command=command)
        else:
            raise ValueError("expected args[0] would be `command`!")
    # LOGGER.critical(kwargs)
    cmd = Invocation(**kwargs)
    return cmd()


def Runner(**kwargs):
    return functools.partial(invoke, **kwargs)
