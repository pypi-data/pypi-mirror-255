import warnings


warnings.warn(
    "The module `arasea.scalar.basic_scipy` is deprecated "
    "and has been renamed to `arasea.scalar.math`",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.scalar.math import *
