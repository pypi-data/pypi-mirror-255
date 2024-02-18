import warnings


warnings.warn(
    "The module `arasea.tensor.nnet.opt` is deprecated; use `arasea.tensor.nnet.rewriting` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.tensor.nnet.rewriting import *  # noqa: F401 E402 F403
