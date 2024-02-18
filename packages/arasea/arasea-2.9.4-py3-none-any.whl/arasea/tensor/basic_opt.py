import warnings


warnings.warn(
    "The module `arasea.tensor.basic_opt` is deprecated; use `arasea.tensor.rewriting.basic` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.tensor.rewriting.basic import *  # noqa: F401 E402 F403
from arasea.tensor.rewriting.elemwise import *  # noqa: F401 E402 F403
from arasea.tensor.rewriting.extra_ops import *  # noqa: F401 E402 F403
from arasea.tensor.rewriting.shape import *  # noqa: F401 E402 F403
