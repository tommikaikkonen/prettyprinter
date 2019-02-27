import numpy as np
import pytest

from prettyprinter import install_extras, pformat

install_extras(["numpy"])


@pytest.mark.parametrize('nptype', (
    np.sctypes["uint"] +
    np.sctypes["int"] +
    np.sctypes["float"]
))
def test_numpy_numeric_types(nptype):
    val = nptype(1)
    py_val = val.item()

    if type(py_val) in (int, float):
        inner_printed = pformat(py_val)
    else:
        # numpy renders types such as float128,
        # that are not representable in native Python
        # types, with Python syntax
        inner_printed = repr(py_val)

    expected = "numpy.{}({})".format(nptype.__name__, inner_printed)
    assert pformat(val) == expected


def test_numpy_bool_type():
    assert pformat(np.bool_(False)) == "numpy.bool_(False)"
    assert pformat(np.bool_(True)) == "numpy.bool_(True)"
