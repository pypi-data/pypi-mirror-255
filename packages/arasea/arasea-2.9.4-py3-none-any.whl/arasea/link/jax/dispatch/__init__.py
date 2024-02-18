# isort: off
from arasea.link.jax.dispatch.basic import jax_funcify, jax_typify

# Load dispatch specializations
import arasea.link.jax.dispatch.scalar
import arasea.link.jax.dispatch.tensor_basic
import arasea.link.jax.dispatch.subtensor
import arasea.link.jax.dispatch.shape
import arasea.link.jax.dispatch.extra_ops
import arasea.link.jax.dispatch.nlinalg
import arasea.link.jax.dispatch.slinalg
import arasea.link.jax.dispatch.random
import arasea.link.jax.dispatch.elemwise
import arasea.link.jax.dispatch.scan

# isort: on
