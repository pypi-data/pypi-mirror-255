import warnings


warnings.warn(
    "The module `arasea.sparse.opt` is deprecated; use `arasea.sparse.rewriting` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.sparse.rewriting import *  # noqa: F401 E402 F403
