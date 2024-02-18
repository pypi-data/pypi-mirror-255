import warnings


warnings.warn(
    "The module `arasea.graph.kanren` is deprecated; use `arasea.graph.rewriting.kanren` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.graph.rewriting.kanren import *  # noqa: F401 E402 F403
