import warnings


warnings.warn(
    "The module `arasea.scan.opt` is deprecated; use `arasea.scan.rewriting` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.scan.rewriting import *  # noqa: F401 E402 F403
