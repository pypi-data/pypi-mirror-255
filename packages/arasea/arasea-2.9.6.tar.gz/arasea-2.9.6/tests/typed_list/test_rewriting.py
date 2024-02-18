import numpy as np

import arasea
import arasea.tensor as at
import arasea.typed_list
from arasea.compile.io import In
from arasea.tensor.type import TensorType, matrix, scalar
from arasea.typed_list.basic import Append, Extend, Insert, Remove, Reverse
from arasea.typed_list.type import TypedListType
from tests.tensor.utils import random_ranged


class TestInplace:
    def test_reverse_inplace(self):
        mySymbolicMatricesList = TypedListType(
            TensorType(arasea.config.floatX, shape=(None, None))
        )()

        z = Reverse()(mySymbolicMatricesList)
        m = arasea.compile.mode.get_default_mode().including(
            "typed_list_inplace_rewrite"
        )
        f = arasea.function(
            [In(mySymbolicMatricesList, borrow=True, mutable=True)],
            z,
            accept_inplace=True,
            mode=m,
        )
        assert f.maker.fgraph.toposort()[0].op.inplace

        x = random_ranged(-1000, 1000, [100, 101])

        y = random_ranged(-1000, 1000, [100, 101])

        assert np.array_equal(f([x, y]), [y, x])

    def test_append_inplace(self):
        mySymbolicMatricesList = TypedListType(
            TensorType(arasea.config.floatX, shape=(None, None))
        )()
        mySymbolicMatrix = matrix()
        z = Append()(mySymbolicMatricesList, mySymbolicMatrix)
        m = arasea.compile.mode.get_default_mode().including(
            "typed_list_inplace_rewrite"
        )
        f = arasea.function(
            [
                In(mySymbolicMatricesList, borrow=True, mutable=True),
                In(mySymbolicMatrix, borrow=True, mutable=True),
            ],
            z,
            accept_inplace=True,
            mode=m,
        )
        assert f.maker.fgraph.toposort()[0].op.inplace

        x = random_ranged(-1000, 1000, [100, 101])

        y = random_ranged(-1000, 1000, [100, 101])

        assert np.array_equal(f([x], y), [x, y])

    def test_extend_inplace(self):
        mySymbolicMatricesList1 = TypedListType(
            TensorType(arasea.config.floatX, shape=(None, None))
        )()

        mySymbolicMatricesList2 = TypedListType(
            TensorType(arasea.config.floatX, shape=(None, None))
        )()

        z = Extend()(mySymbolicMatricesList1, mySymbolicMatricesList2)
        m = arasea.compile.mode.get_default_mode().including(
            "typed_list_inplace_rewrite"
        )
        f = arasea.function(
            [
                In(mySymbolicMatricesList1, borrow=True, mutable=True),
                mySymbolicMatricesList2,
            ],
            z,
            mode=m,
        )
        assert f.maker.fgraph.toposort()[0].op.inplace

        x = random_ranged(-1000, 1000, [100, 101])

        y = random_ranged(-1000, 1000, [100, 101])

        assert np.array_equal(f([x], [y]), [x, y])

    def test_insert_inplace(self):
        mySymbolicMatricesList = TypedListType(
            TensorType(arasea.config.floatX, shape=(None, None))
        )()
        mySymbolicIndex = scalar(dtype="int64")
        mySymbolicMatrix = matrix()

        z = Insert()(mySymbolicMatricesList, mySymbolicIndex, mySymbolicMatrix)
        m = arasea.compile.mode.get_default_mode().including(
            "typed_list_inplace_rewrite"
        )

        f = arasea.function(
            [
                In(mySymbolicMatricesList, borrow=True, mutable=True),
                mySymbolicIndex,
                mySymbolicMatrix,
            ],
            z,
            accept_inplace=True,
            mode=m,
        )
        assert f.maker.fgraph.toposort()[0].op.inplace

        x = random_ranged(-1000, 1000, [100, 101])

        y = random_ranged(-1000, 1000, [100, 101])

        assert np.array_equal(f([x], np.asarray(1, dtype="int64"), y), [x, y])

    def test_remove_inplace(self):
        mySymbolicMatricesList = TypedListType(
            TensorType(arasea.config.floatX, shape=(None, None))
        )()
        mySymbolicMatrix = matrix()
        z = Remove()(mySymbolicMatricesList, mySymbolicMatrix)
        m = arasea.compile.mode.get_default_mode().including(
            "typed_list_inplace_rewrite"
        )
        f = arasea.function(
            [
                In(mySymbolicMatricesList, borrow=True, mutable=True),
                In(mySymbolicMatrix, borrow=True, mutable=True),
            ],
            z,
            accept_inplace=True,
            mode=m,
        )
        assert f.maker.fgraph.toposort()[0].op.inplace

        x = random_ranged(-1000, 1000, [100, 101])

        y = random_ranged(-1000, 1000, [100, 101])

        assert np.array_equal(f([x, y], y), [x])


def test_constant_folding():
    m = at.ones((1,), dtype="int8")
    l = arasea.typed_list.make_list([m, m])
    f = arasea.function([], l)
    topo = f.maker.fgraph.toposort()
    assert len(topo)
    assert isinstance(topo[0].op, arasea.compile.ops.DeepCopyOp)
    assert f() == [1, 1]
