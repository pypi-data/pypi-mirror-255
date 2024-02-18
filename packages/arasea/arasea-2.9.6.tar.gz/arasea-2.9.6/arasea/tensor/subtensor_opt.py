import warnings


warnings.warn(
    "The module `arasea.tensor.subtensor_opt` is deprecated; use `arasea.tensor.rewriting.subtensor` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.tensor.rewriting.subtensor import *  # noqa: F401 E402 F403
