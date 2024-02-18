import warnings


warnings.warn(
    "The module `arasea.graph.toolbox` is deprecated "
    "and has been renamed to `arasea.graph.features`",
    DeprecationWarning,
    stacklevel=2,
)

from arasea.graph.toolbox import *
