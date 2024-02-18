import warnings


warnings.warn(
    "The module `arasea.tensor.random.opt` is deprecated; use `arasea.tensor.random.rewriting` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.tensor.random.rewriting import *  # noqa: F401 E402 F403
