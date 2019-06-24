import ast
from distutils.version import LooseVersion
from math import ceil

from ..doctypes import Concat, HARDLINE
from ..prettyprinter import (
    register_pretty,
    pretty_call_alt,
    pretty_bool,
    pretty_int,
    pretty_float
)


class _ArrayWrapper:
    def __init__(self, array):
        self.array = array


def pretty_ndarray(value, ctx):
    import numpy as np
    # numpy 1.14 added dtype_is_implied.
    if LooseVersion(np.__version__) < "1.14":
        return repr(value)
    if type(value) != np.ndarray:
        # Masked arrays, in particular, require their own logic.
        return repr(value)
    from numpy.core import arrayprint
    args = (_ArrayWrapper(value),)
    kwargs = []
    dtype = value.dtype
    # This logic is extracted from arrayprint._array_repr_implementation.
    skip_dtype = arrayprint.dtype_is_implied(dtype) and value.size > 0
    if not skip_dtype:
        dtype_repr = repr(dtype)
        assert dtype_repr.startswith("dtype(") and dtype_repr.endswith(")")
        kwargs.append(("dtype", ast.literal_eval(dtype_repr[6:-1])))
    ctx_new = ctx.nested_call()
    # Handle truncation of subsequences for multidimensional arrays
    if value.ndim >= 2 and value.size > ctx.max_seq_len:
        left, right = 1, ctx.max_seq_len
        while left != right:
            middle = ceil((left + right) / 2)
            if np.prod(np.minimum(middle, value.shape)) > ctx.max_seq_len:
                right = middle - 1
            else:
                left = middle
        ctx_new.max_seq_len = left
    return pretty_call_alt(ctx_new, type(value), args, kwargs)


def pretty_arraywrapper(value, ctx):
    import numpy as np
    # array2string correctly aligns the items of the array, without adding
    # "array(" in the front or the dtype info (which we handle ourselves) in
    # the back.
    s = np.array2string(value.array, separator=", ")
    lines = s.split("\n")
    if len(lines) == 1:
        return s
    else:
        interspersed = [HARDLINE] * 2 * len(lines)
        interspersed[1::2] = lines
        return Concat(interspersed)


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
    register_pretty("prettyprinter.extras.numpy._ArrayWrapper")(
        pretty_arraywrapper)
