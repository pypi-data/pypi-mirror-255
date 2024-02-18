# isort: off
from arasea.link.numba.dispatch.basic import (
    numba_funcify,
    numba_const_convert,
    numba_njit,
)

# Load dispatch specializations
import arasea.link.numba.dispatch.scalar
import arasea.link.numba.dispatch.tensor_basic
import arasea.link.numba.dispatch.extra_ops
import arasea.link.numba.dispatch.nlinalg
import arasea.link.numba.dispatch.random
import arasea.link.numba.dispatch.elemwise
import arasea.link.numba.dispatch.scan
import arasea.link.numba.dispatch.sparse

# isort: on
