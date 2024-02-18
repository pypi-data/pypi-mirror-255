""" shil
"""

from fleks.util import lme

from .models import Invocation, InvocationResult  # noqa
from .parser import fmt, shfmt  # noqa
from .util import Runner, invoke  # noqa

DEBUG = True  # False
LOGGER = lme.get_logger(__name__)
