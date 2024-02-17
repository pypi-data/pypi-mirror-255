"""
# Utilities for dealing with and manipulating docstrings

- Owners: piotrm
"""

from typing import Any, Tuple

# logger = logging.getLogger(name=__name__)


def doc_untab(obj: Any) -> Tuple[str, str]:
    """
    Get the margin and a de-marginalized docstring of the given object.
    """

    if not hasattr(obj, "__doc__"):
        return ("", "")

    doc = obj.__doc__

    if doc is None:
        return ("", "")

    while doc[0] == "\n":
        doc = doc[1:]

    tab = ""

    while doc[0] in [" ", "\t"]:
        tab += doc[0]
        doc = doc[1:]

    lines = []
    for line in doc.split("\n"):
        if line.startswith(tab):
            line = line[len(tab):]

        lines.append(line)

    return (tab, "\n".join(lines))


def doc_render(obj) -> str:
    """
    Draws the given object's docstring removing its margin.
    """

    _, doc = doc_untab(obj)
    return doc.strip()


def doc_prepend(obj: Any, text: str) -> None:
    """
    Prepend the given text to the docstring for the given object. Prepends
    using the same margins that exist already.
    """

    if not obj.__doc__:
        doc = ""
    else:
        doc = obj.__doc__

    tabwidth = 0

    # Check if there is a margin made of spaces in the existing docstring.
    if len(doc) > 2:

        if doc[0] == "\n":
            # Check for docstrings delimited with """ that start on the next
            # line after delimeter. The first line in such docstrings does not
            # have a margin, so we throw away the first line.

            lines = doc.split("\n")
            l1 = lines[1]
        else:
            l1 = doc

        for i, c in enumerate(l1):
            if c != " ":
                break

        tabwidth = i

    textlines = text.split("\n")
    tabedtext = "\n".join(
        [(" " * tabwidth) + textline for textline in textlines]
    )

    doc = tabedtext + "\n" + doc

    obj.__doc__ = doc
