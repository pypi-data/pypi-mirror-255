import warnings


warnings.warn(
    "The module `arasea.link.jax.jax_dispatch` is deprecated "
    "and has been renamed to `arasea.link.jax.dispatch`",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.link.jax.dispatch import *
