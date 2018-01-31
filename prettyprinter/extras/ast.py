import ast
from collections import OrderedDict
from prettyprinter.prettyprinter import pretty_call_alt, register_pretty


def is_class_from_ast(value):
    return isinstance(value, ast.AST)


def pretty_nodes(value, ctx):
    cls = type(value)
    kwargs = [(k, v) for k, v in value.__dict__.items() if not k.startswith('_')]
    if cls.__module__ == '_ast':
        cls_name = 'ast.%s' % cls.__qualname__
    else:
        cls_name = cls
    return pretty_call_alt(ctx, cls_name, kwargs=kwargs)


def install():
    register_pretty(predicate=is_class_from_ast)(pretty_nodes)
