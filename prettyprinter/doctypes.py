def normalize_doc(doc):
    if isinstance(doc, str):
        if doc == '':
            return NIL
        return doc
    return doc.normalize()


class Doc:
    """The base class for all Docs, except for plain ``str`` s which
    are unboxed.

    A Doc is a tree structure that represents the set of all possible
    layouts of the contents. The layout algorithm processes the tree,
    narrowing down the set of layouts based on input parameters like
    total and ribbon width to produce a stream of SDocs (simple Docs)
    that represent a single layout.
    """
    __slots__ = ()

    def normalize(self):
        return self


class Annotated(Doc):
    __slots__ = ('doc', 'annotation')

    def __init__(self, doc, annotation):
        self.doc = doc
        self.annotation = annotation

    def __repr__(self):
        return 'Annotated({})'.format(repr(self.doc))

    def normalize(self):
        return Annotated(normalize_doc(self.doc), self.annotation)


class Nil(Doc):
    def __repr__(self):
        return 'NIL'


NIL = Nil()


class Concat(Doc):
    __slots__ = ('docs', )

    def __init__(self, docs):
        self.docs = list(docs)

    def normalize(self):
        normalized_docs = []
        propagate_broken = False
        for doc in self.docs:
            doc = normalize_doc(doc)
            if isinstance(doc, Concat):
                normalized_docs.extend(doc.docs)
            elif isinstance(doc, AlwaysBreak):
                propagate_broken = True
                normalized_docs.append(doc.doc)
            elif doc is NIL:
                continue
            else:
                normalized_docs.append(doc)

        if not normalized_docs:
            return NIL

        if len(normalized_docs) == 1:
            res = normalized_docs[0]
        else:
            res = Concat(normalized_docs)

        if propagate_broken:
            res = AlwaysBreak(res)
        return res

    def __repr__(self):
        return "Concat([{}])".format(
            ', '.join(repr(doc) for doc in self.docs)
        )


class Nest(Doc):
    __slots__ = ('indent', 'doc')

    def __init__(self, indent, doc):
        assert isinstance(indent, int)
        assert isinstance(doc, Doc)

        self.indent = indent
        self.doc = doc

    def normalize(self):
        inner_normalized = normalize_doc(self.doc)
        if isinstance(inner_normalized, AlwaysBreak):
            return AlwaysBreak(
                Nest(self.indent, inner_normalized.doc)
            )
        return Nest(self.indent, inner_normalized)

    def __repr__(self):
        return 'Nest({}, {})'.format(
            repr(self.indent),
            repr(self.doc)
        )


class FlatChoice(Doc):
    __slots__ = (
        '_when_broken',
        '_when_flat',
        'normalize_on_access',
        '_broken_normalized',
        '_flat_normalized',
    )

    def __init__(self, when_broken, when_flat, normalize_on_access=False):
        self._when_broken = when_broken
        self._when_flat = when_flat

        # If we were to strictly normalize this Doc, we'd have
        # to normalize both subtrees, which can be costly if they're
        # large. The layout algorithm only accesses one of the
        # properties based on the current mode (break/flat).
        # Hence we delay the normalization to when that access
        # happens.
        self.normalize_on_access = normalize_on_access
        self._broken_normalized = False
        self._flat_normalized = False

    def normalize(self):
        if self.normalize_on_access:
            return self

        return FlatChoice(
            self._when_broken,
            self._when_flat,
            normalize_on_access=True
        )

    @property
    def when_broken(self):
        if self.normalize_on_access and not self._broken_normalized:
            self._when_broken = normalize_doc(self._when_broken)
            self._broken_normalized = True
        return self._when_broken

    @property
    def when_flat(self):
        if self._broken_normalized and not self._flat_normalized:
            self._when_flat = normalize_doc(self._when_flat)
            self._flat_normalized = True
        return self._when_flat

    def __repr__(self):
        return 'FlatChoice(when_broken={}, when_flat={})'.format(
            repr(self.when_broken),
            repr(self.when_flat)
        )


class Contextual(Doc):
    __slots__ = ('fn', )

    def __init__(self, fn):
        self.fn = fn

    def __repr__(self):
        return 'Contextual({})'.format(repr(self.fn))


class HardLine(Doc):
    def __repr__(self):
        return 'HardLine()'


HARDLINE = HardLine()
LINE = FlatChoice(HARDLINE, ' ')
SOFTLINE = FlatChoice(HARDLINE, NIL)


class Group(Doc):
    __slots__ = ('doc', )

    def __init__(self, doc):
        assert isinstance(doc, Doc)
        self.doc = doc

    def normalize(self):
        doc_normalized = normalize_doc(self.doc)
        if isinstance(doc_normalized, AlwaysBreak):
            # Group is the possibility of either flat
            # or break; since we're always breaking,
            # we don't need Group.
            return doc_normalized
        elif doc_normalized is NIL:
            return NIL
        return Group(doc_normalized)

    def __repr__(self):
        return 'Group({})'.format(repr(self.doc))


class AlwaysBreak(Doc):
    __slots__ = ('doc', )

    def __init__(self, doc):
        assert isinstance(doc, Doc)
        self.doc = doc

    def normalize(self):
        doc_normalized = normalize_doc(self.doc)
        if isinstance(doc_normalized, AlwaysBreak):
            return doc_normalized
        return AlwaysBreak(doc_normalized)

    def __repr__(self):
        return 'AlwaysBreak({})'.format(repr(self.doc))


class Fill(Doc):
    __slots__ = ('docs', )

    def __init__(self, docs):
        self.docs = list(docs)

    def normalize(self):
        normalized_docs = []
        propagate_broken = False
        for doc in self.docs:
            if isinstance(doc, AlwaysBreak):
                propagate_broken = True
                doc = doc.doc

            if doc is NIL:
                continue
            else:
                normalized_docs.append(doc)

        if normalized_docs:
            res = Fill(normalized_docs)
            if propagate_broken:
                res = AlwaysBreak(res)
            return res

        return NIL

    def __repr__(self):
        return "Fill([{}])".format(
            ', '.join(repr(doc) for doc in self.docs)
        )
