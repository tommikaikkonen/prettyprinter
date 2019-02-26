import numpy as np

from prettyprinter import install_extras, pformat


def test_numpy():
    for tp in np.sctypes["uint"] + np.sctypes["int"] + np.sctypes["float"]:
        np_scalar = tp(1)
        py_scalar = np.array(1, tp).item()  # builtin int/float.
        assert pformat(np_scalar) == pformat(py_scalar)
    assert pformat(np.bool_(True)) == pformat(True)
    install_extras(["numpy"])
    for tp in (np.sctypes["uint"] + np.sctypes["int"] + np.sctypes["float"]
               + [np.bool_]):
        assert "(" in pformat(tp(1))
