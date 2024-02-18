import warnings


warnings.warn(
    "The module `arasea.graph.unify` is deprecated; use `arasea.graph.rewriting.unify` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.graph.rewriting.unify import *  # noqa: F401 E402 F403
