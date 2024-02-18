import warnings


warnings.warn(
    "The module `arasea.tensor.opt_uncanonicalize` is deprecated; use `arasea.tensor.rewriting.uncanonicalize` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.tensor.rewriting.uncanonicalize import *  # noqa: F401 E402 F403
