"""
The layout algorithm here was inspired by the following
papers and libraries:

- Wadler, P. (1998). A prettier printer
    https://homepages.inf.ed.ac.uk/wadler/papers/prettier/prettier.pdf
- Lindig, C. (2000) Strictly Pretty
    http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.34.2200
- Extensions to the Wadler pretty printer by Daniel Leijen in the
    Haskell package 'wl-pprint'
    https://hackage.haskell.org/package/wl-pprint-1.2/docs/Text-PrettyPrint-Leijen.html
- The Haskell 'prettyprinter' package, which builds on top of the
    'ansi-wl-pprint' package.
    https://hackage.haskell.org/package/prettyprinter
- The JavaScript Prettier library
    https://github.com/prettier/prettier
"""

from copy import copy

from .doctypes import (
    NIL,
    HARDLINE,
    AlwaysBreak,
    Annotated,
    Concat,
    Contextual,
    FlatChoice,
    Fill,
    Group,
    Nest,
    normalize_doc,
)
from .sdoctypes import (
    SLine,
    SAnnotationPop,
    SAnnotationPush,
)


BREAK_MODE = 0
FLAT_MODE = 1


def fast_fitting_predicate(
    page_width,  # Ignored.
    ribbon_frac,  # Ignored.
    min_nesting_level,  # Ignored.
    max_width,
    triplestack
):
    """
    One element lookahead. Fast, but not the prettiest.
    """

    chars_left = max_width

    while chars_left >= 0:
        if not triplestack:
            return True

        indent, mode, doc = triplestack.pop()
        if doc is NIL:
            continue
        elif isinstance(doc, str):
            chars_left -= len(doc)
        elif isinstance(doc, Concat):
            # Recursive call in Strictly Pretty: docs within Concat
            # are processed in order, with keeping the current
            # indentation and mode.
            # We want the leftmost element at the top of the stack,
            # so we append the concatenated documents in reverse order.
            triplestack.extend(
                (indent, mode, doc)
                for doc in reversed(doc.docs)
            )
        elif isinstance(doc, Annotated):
            triplestack.append((indent, mode, doc.doc))
        elif isinstance(doc, Fill):
            triplestack.extend(
                (indent, mode, doc)
                for doc in reversed(doc.docs)
            )
        elif isinstance(doc, Nest):
            # Nest is a combination of an indent and a doc.
            # Increase indentation, then add the doc for processing.
            triplestack.append((indent + doc.indent, mode, doc.doc))
        elif isinstance(doc, AlwaysBreak):
            return False
            triplestack.append((indent, BREAK_MODE, doc.doc))
        elif doc is HARDLINE:
            return True
        elif isinstance(doc, FlatChoice):
            if mode is FLAT_MODE:
                triplestack.append((indent, mode, doc.when_flat))
            elif mode is BREAK_MODE:
                triplestack.append((indent, mode, doc.when_broken))
            else:
                raise ValueError
        elif isinstance(doc, Group):
            # Group just changes the mode.
            triplestack.append((indent, FLAT_MODE, doc.doc))
        elif isinstance(doc, Contextual):
            ribbon_width = max(0, min(page_width, round(ribbon_frac * page_width)))

            evaluated_doc = doc.fn(
                indent=indent,
                column=max_width - chars_left,
                page_width=page_width,
                ribbon_width=ribbon_width,
            )
            normalized = normalize_doc(evaluated_doc)
            triplestack.append((indent, mode, normalized))
        elif isinstance(doc, SAnnotationPush):
            continue
        elif isinstance(doc, SAnnotationPop):
            continue
        else:
            raise ValueError((indent, mode, doc))

    return False


def smart_fitting_predicate(
    page_width,
    ribbon_frac,
    min_nesting_level,
    max_width,
    triplestack
):
    """
    Lookahead until the last doc at the current indentation level.
    Pretty, but not as fast.
    """
    chars_left = max_width

    while chars_left >= 0:
        if not triplestack:
            return True

        indent, mode, doc = triplestack.pop()

        if doc is NIL:
            continue
        elif isinstance(doc, str):
            chars_left -= len(doc)
        elif isinstance(doc, Concat):
            # Recursive call in Strictly Pretty: docs within Concat
            # are processed in order, with keeping the current
            # indentation and mode.
            # We want the leftmost element at the top of the stack,
            # so we append the concatenated documents in reverse order.
            triplestack.extend(
                (indent, mode, doc)
                for doc in reversed(doc.docs)
            )
        elif isinstance(doc, Annotated):
            triplestack.append((indent, mode, doc.doc))
        elif isinstance(doc, Fill):
            # Same as the Concat case.
            triplestack.extend(
                (indent, mode, doc)
                for doc in reversed(doc.docs)
            )
        elif isinstance(doc, Nest):
            # Nest is a combination of an indent and a doc.
            # Increase indentation, then add the doc for processing.
            triplestack.append((indent + doc.indent, mode, doc.doc))
        elif isinstance(doc, AlwaysBreak):
            return False
        elif doc is HARDLINE:
            # In the fast algorithm, when we see a line,
            # we return True. Here, as long as the minimum indentation
            # level is satisfied, we continue processing the next line.
            # This causes the longer runtime.
            if indent > min_nesting_level:
                chars_left = page_width - indent
            else:
                return True
        elif isinstance(doc, FlatChoice):
            if mode is FLAT_MODE:
                triplestack.append((indent, mode, doc.when_flat))
            elif mode is BREAK_MODE:
                triplestack.append((indent, mode, doc.when_broken))
            else:
                raise ValueError
        elif isinstance(doc, Group):
            # Group just changes the mode.
            triplestack.append((indent, FLAT_MODE, doc.doc))
        elif isinstance(doc, Contextual):
            ribbon_width = max(0, min(page_width, round(ribbon_frac * page_width)))

            evaluated_doc = doc.fn(
                indent=indent,
                column=max_width - chars_left,
                page_width=page_width,
                ribbon_width=ribbon_width,
            )
            normalized = normalize_doc(evaluated_doc)
            triplestack.append((indent, mode, normalized))
        elif isinstance(doc, SAnnotationPush):
            continue
        elif isinstance(doc, SAnnotationPop):
            continue
        else:
            raise ValueError((indent, mode, doc))

    return False


def best_layout(
    doc,
    width,
    ribbon_frac,
    fitting_predicate,
    outcol=0,
    mode=BREAK_MODE
):
    normalized = normalize_doc(doc)

    ribbon_width = max(0, min(width, round(ribbon_frac * width)))

    # The Strictly Pretty paper shows a recursive algorithm.
    # This is the stack-and-loop version of it.
    triplestack = [(outcol, mode, normalized)]

    while triplestack:
        indent, mode, doc = triplestack.pop()

        if doc is NIL:
            # Nothing to do here.
            continue

        if doc is HARDLINE:
            yield SLine(indent)
            outcol = indent
        elif isinstance(doc, str):
            yield doc
            outcol += len(doc)
        elif isinstance(doc, Concat):
            # Add the docs to the stack and process them.
            # The first doc in the concatenation must
            # end up at the top of the stack, hence the reversing.
            triplestack.extend(
                (indent, mode, child)
                for child in reversed(doc.docs)
            )
        elif isinstance(doc, Contextual):
            evaluated_doc = doc.fn(
                indent=indent,
                column=outcol,
                page_width=width,
                ribbon_width=ribbon_width,
            )
            normalized = normalize_doc(evaluated_doc)
            triplestack.append((indent, mode, normalized))
        elif isinstance(doc, Annotated):
            yield SAnnotationPush(doc.annotation)
            # Usually, the triplestack is solely a stack of docs.
            # SAnnotationPop is a special case: when we find an annotated doc,
            # we output the SAnnotationPush SDoc directly. The equivalent
            # SAnnotationPop must be output after all the nested docs have been
            # processed. An easy way to do this is to add the SAnnotationPop
            # directly to the stack and output it when we see it.
            triplestack.append((indent, mode, SAnnotationPop(doc.annotation)))
            triplestack.append((indent, mode, doc.doc))
        elif isinstance(doc, FlatChoice):
            if mode is BREAK_MODE:
                triplestack.append((indent, mode, doc.when_broken))
            elif mode is FLAT_MODE:
                triplestack.append((indent, mode, doc.when_flat))
            else:
                raise ValueError
        elif isinstance(doc, Nest):
            # Increase indentation and process the nested doc.
            triplestack.append((indent + doc.indent, mode, doc.doc))
        elif isinstance(doc, Group):
            new_triplestack = copy(triplestack)
            # The line will consist of the Grouped doc, as well as the rest
            # of the docs in the stack.
            new_triplestack.append((indent, FLAT_MODE, doc.doc))

            min_nesting_level = min(outcol, indent)

            columns_left_in_line = width - outcol
            columns_left_in_ribbon = indent + ribbon_width - outcol
            available_width = min(columns_left_in_line, columns_left_in_ribbon)

            if fitting_predicate(
                page_width=width,
                ribbon_frac=ribbon_frac,
                min_nesting_level=min_nesting_level,
                max_width=available_width,
                triplestack=new_triplestack
            ):
                # This group will fit on a single line. Continue processing
                # the grouped doc in flat mode.
                triplestack.append((indent, FLAT_MODE, doc.doc))
            else:
                triplestack.append((indent, BREAK_MODE, doc.doc))
        elif isinstance(doc, Fill):
            # docs must be alternating whitespace
            docs = doc.docs

            if not docs:
                continue

            first_doc = docs[0]
            flat_content_triple = (indent, FLAT_MODE, first_doc)
            broken_content_triple = (indent, BREAK_MODE, first_doc)

            # this is just copy pasted from the group case...
            min_nesting_level = min(outcol, indent)

            columns_left_in_line = width - outcol
            columns_left_in_ribbon = indent + ribbon_width - outcol
            available_width = min(columns_left_in_line, columns_left_in_ribbon)

            does_fit = fast_fitting_predicate(
                page_width=width,
                ribbon_frac=ribbon_frac,
                min_nesting_level=min_nesting_level,
                max_width=available_width,
                triplestack=[flat_content_triple]
            )

            if len(docs) == 1:
                if does_fit:
                    triplestack.append(flat_content_triple)
                else:
                    triplestack.append(broken_content_triple)
                continue

            whitespace = docs[1]
            flat_whitespace_triple = (indent, FLAT_MODE, whitespace)
            broken_whitespace_triple = (indent, BREAK_MODE, whitespace)

            if len(docs) == 2:
                if does_fit:
                    triplestack.append(flat_whitespace_triple)
                    triplestack.append(flat_content_triple)
                else:
                    triplestack.append(broken_whitespace_triple)
                    triplestack.append(broken_content_triple)

                continue

            remaining = docs[2:]
            remaining_triple = (indent, mode, Fill(remaining))

            fst_and_snd_content_flat_triple = (indent, FLAT_MODE, Concat(docs[:2]))

            fst_and_snd_content_does_fit = fast_fitting_predicate(
                page_width=width,
                ribbon_frac=ribbon_frac,
                min_nesting_level=min_nesting_level,
                max_width=available_width,
                triplestack=[fst_and_snd_content_flat_triple]
            )

            if fst_and_snd_content_does_fit:
                triplestack.append(remaining_triple)
                triplestack.append(flat_whitespace_triple)
                triplestack.append(flat_content_triple)
            elif does_fit:
                triplestack.append(remaining_triple)
                triplestack.append(broken_whitespace_triple)
                triplestack.append(flat_content_triple)
            else:
                triplestack.append(remaining_triple)
                triplestack.append(broken_whitespace_triple)
                triplestack.append(broken_content_triple)
        elif isinstance(doc, AlwaysBreak):
            triplestack.append((indent, BREAK_MODE, doc.doc))
        elif isinstance(doc, SAnnotationPop):
            yield doc
        else:
            raise ValueError((indent, mode, doc))


def layout_smart(doc, width=79, ribbon_frac=0.9):
    return best_layout(
        doc,
        width,
        ribbon_frac,
        fitting_predicate=smart_fitting_predicate,
    )


def layout_fast(doc, width=79, ribbon_frac=0.9):
    return best_layout(
        doc,
        width,
        ribbon_frac,
        fitting_predicate=fast_fitting_predicate,
    )
