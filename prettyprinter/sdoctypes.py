
class SDoc(object):
    pass


class SLine(SDoc):
    __slots__ = ('indent', )

    def __init__(self, indent):
        assert isinstance(indent, int)
        self.indent = indent

    def __repr__(self):
        return 'SLine({})'.format(repr(self.indent))


class SAnnotationPush(SDoc):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'SAnnotationPush({})'.format(repr(self.value))


class SAnnotationPop(SDoc):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'SAnnotationPush({})'.format(repr(self.value))
