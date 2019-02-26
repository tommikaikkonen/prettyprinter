from .. import prettyprinter
from ..prettyprinter import (
    register_pretty, pretty_singletons, pretty_int, pretty_float)


def install():
    prettyprinter._NUMPY_EXTRA_INSTALLED = True
    register_pretty("numpy.bool_")(pretty_singletons)
    for name in [
            "uint8", "uint16", "uint32", "uint64",
            "int8", "int16", "int32", "int64",
    ]:
        register_pretty("numpy." + name)(pretty_int)
    for name in [
            "float16", "float32", "float64", "float128",
    ]:
        register_pretty("numpy." + name)(pretty_float)
