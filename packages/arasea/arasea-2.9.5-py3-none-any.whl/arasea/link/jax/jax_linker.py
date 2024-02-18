import warnings


warnings.warn(
    "The module `arasea.link.jax.jax_linker` is deprecated "
    "and has been renamed to `arasea.link.jax.linker`",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.link.jax.linker import *
