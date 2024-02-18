import arasea
from arasea.tensor.type import vector


def test_stack_trace():
    with arasea.config.change_flags(traceback__limit=1):
        v = vector()
        assert len(v.tag.trace) == 1
        assert len(v.tag.trace[0]) == 1

    with arasea.config.change_flags(traceback__limit=2):
        v = vector()
        assert len(v.tag.trace) == 1
        assert len(v.tag.trace[0]) == 2
