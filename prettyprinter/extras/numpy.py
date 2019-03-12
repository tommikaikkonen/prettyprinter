import ast
from distutils.version import LooseVersion

from ..prettyprinter import (
    register_pretty,
    pretty_call_alt,
    pretty_bool,
    pretty_int,
    pretty_float
)


def pretty_ndarray(value, ctx):
    import numpy as np
    # numpy 1.14 added dtype_is_implied.
    if LooseVersion(np.__version__) < "1.14":
        return repr(value)
    if type(value) != np.ndarray:
        # Masked arrays, in particular, require their own logic.
        return repr(value)
    from numpy.core import arrayprint
    args = (value.tolist(),)
    kwargs = []
    dtype = value.dtype
    # This logic is extracted from arrayprint._array_repr_implementation.
    skip_dtype = arrayprint.dtype_is_implied(dtype) and value.size > 0
    if not skip_dtype:
        dtype_repr = repr(dtype)
        assert dtype_repr.startswith("dtype(") and dtype_repr.endswith(")")
        kwargs.append(("dtype", ast.literal_eval(dtype_repr[6:-1])))
    return pretty_call_alt(ctx, type(value), args, kwargs)


def install():
    register_pretty("numpy.bool_")(pretty_bool)

    for name in [
        "uint8", "uint16", "uint32", "uint64",
        "int8", "int16", "int32", "int64",
    ]:
        register_pretty("numpy." + name)(pretty_int)

    for name in [
        "float16", "float32", "float64", "float128",
    ]:
        register_pretty("numpy." + name)(pretty_float)

    register_pretty("numpy.ndarray")(pretty_ndarray)
