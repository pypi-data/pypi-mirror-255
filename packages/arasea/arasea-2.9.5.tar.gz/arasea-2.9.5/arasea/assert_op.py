import warnings


warnings.warn(
    "The module `arasea.assert_op` is deprecated "
    "and its `Op`s have been moved to `arasea.raise_op`",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.raise_op import Assert, assert_op  # noqa: F401 E402
