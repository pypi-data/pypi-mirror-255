import warnings


warnings.warn(
    "The module `arasea.tensor.math_opt` is deprecated; use `arasea.tensor.rewriting.math` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.tensor.rewriting.math import *  # noqa: F401 E402 F403
