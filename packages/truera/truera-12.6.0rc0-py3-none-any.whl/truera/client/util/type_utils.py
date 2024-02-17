"""
# Types, typing, type handling utilities.

- Owners: piotrm

## Typelike

A lot of utilities here are for dealing with objects which we want to treat like
types/classes but are not actually types/classes according to python. This
includes most of `typing` module contents. Note, however, that in order to
support isinstance/issublcass, we have alternate implementations of some of the
"types" in `typing`.*. You can find those in `types.py`.

## Tests

- Unit tests
    - `python/truera/test/unit_tests/client/test_type_utils.py`
    - `make test/unit_tests/client/test_type_utils`

"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
import inspect
from re import Pattern
import types
import typing
from typing import Any, Iterable, Optional, Set

from truera.client.util.python_utils import cache_on_first_arg

# logger = logging.getLogger(name=__name__)


# TODO(future python version): Can replace this with python's once a version
# that supports instancecheck is included.
class Never(type):
    """
    A type that is not inhabited by any instance. LogicalType.Unit has the
    same purpose but it also supports subclass checks unlike this core
    version.
    """

    def __instancecheck__(self, obj: Any) -> bool:
        return False


class AutoNone(type):
    """
    Controls which function arguments get their default value filled in the
    function signature by `sig_fill_defaults`.
    """
    # NOTE: this type needs to be here to avoid circular imports.

    # __new__ needed for type subtypes if they change expected __new__/__init__
    # arguments which AutoNone does not.

    pass


class Monoid(ABC):
    """
    Monoid. Abstraction of the concept of set of objects with a plus operation
    that can add two objects to produce a third. Models things like
    accumulators, or map-reduce like operations. Must also define a zero object
    for the starting points for monoid-based operations.
    """

    @staticmethod
    @abstractmethod
    def zero() -> Monoid:
        pass

    @staticmethod
    @abstractmethod
    def plus(a: Monoid, b: Monoid) -> Monoid:
        pass


# Methods for dealing with delayed annotation evaluation via future.__annotations__ .


def typelike_bases(obj) -> Iterable[type]:
    """
    Get the bases of the given type `obj` or if its a pretend-type, get some pretend bases.
    """

    if isinstance(obj, type):
        return obj.__bases__
    else:
        # For pretend types, return just object. This limits possible
        # instance/subclass checking possible for now.
        return [object]


@cache_on_first_arg
def is_typelike(obj) -> bool:
    """
    Check whether given `obj` is a type or something we'd like to treat as a
    type. This includes typing.* aliases.
    """

    if isinstance(obj, type):
        return True

    # The above does not always work. typing.Sequence is not a type for example.

    if hasattr(obj, "__subclasscheck__"):
        return True

    # This one is needed to view the typing.* collection "types" as types.
    if isinstance(obj, typing._GenericAlias):
        return True

    return False


def fullname(obj: Any) -> str:
    """
    Get the full module/package class name of the given object.
    """

    if isinstance(obj, types.ModuleType):
        return obj.__name__
    elif isinstance(obj, type):
        return obj.__module__ + "." + obj.__name__
    elif hasattr(obj, "__origin__"):
        # typing.* aliases have __origin__ .
        return fullname(obj.__origin__)
    elif hasattr(obj, "__class__"):
        return fullname(obj.__class__)
    else:
        raise ValueError(f"Cannot determine full name of {obj}.")


def shortname(obj: Any) -> str:
    """
    Get the short module/package class name of the given object.
    """

    if isinstance(obj, types.ModuleType):
        return obj.__name__
    elif isinstance(obj, type):
        return obj.__name__
    elif hasattr(obj, "__origin__"):
        # typing.* aliases have __origin__ .
        return shortname(obj.__origin__)
    elif hasattr(obj, "__class__"):
        return shortname(obj.__class__)
    else:
        raise ValueError(f"Cannot determine short name of {obj}.")


def _find_matches(
    mod: types.ModuleType,
    walked: Set[type],
    found: Set[type],
    typ: Optional[type] = None,
    pattern: Optional[Pattern] = None
) -> Iterable[type]:
    """
    Helper for `find_matches`. Initialized with empty `walked` set, the modules
    already walked, and empty `found` set, the classes already matched and
    yielded.
    """

    if mod in walked:
        return

    walked.add(mod)

    for name in dir(mod):
        try:
            submod = getattr(mod, name)
        except:
            continue

        fname = fullname(submod)

        matched_typ = typ is None
        matched_pattern = pattern is None

        if inspect.ismodule(submod):
            if fname.startswith(fullname(mod)):
                for m in _find_matches(
                    submod,
                    walked=walked,
                    found=found,
                    typ=typ,
                    pattern=pattern
                ):
                    yield m

        elif fname in found:
            continue

        elif inspect.isclass(submod):
            if typ is not None and issubclass(submod, typ):
                matched_typ = True
            if pattern is not None and pattern.fullmatch(fname) is not None:
                matched_pattern = True
        else:
            if typ is not None and isinstance(submod, typ):
                matched_typ = True
            if pattern is not None and pattern.fullmatch(fname) is not None:
                matched_pattern = True

        if matched_typ and matched_pattern:
            found.add(fname)
            yield submod


def find_matches(
    mod: types.ModuleType,
    typ: Optional[type] = None,
    pattern: Optional[Pattern] = None
) -> Iterable[type]:
    """
    Walk the module hierarchy starting with the given module `mod` producing all
    of the contents that are either subtypes of given type `typ` and whose name
    matches given re.Pattern `pattern`. One of the two conditions may be
    ommitted.
    """
    assert typ or pattern, "Need `typ` and/or `pattern` to be given."

    return _find_matches(mod, set(), set(), typ=typ, pattern=pattern)


def concretize(
    mod: typing.ModuleType,
    typ: Optional[type] = None,
    pattern: Optional[Pattern] = None
) -> str:
    """
    Render a piece of python source that represents the types found by walking
    over `mod` that are subtypes of `typ` or ones whose name matches re.Pattern
    `pattern`. One of these conditions may be ommitted.
    """

    assert typ or pattern, "Need `typ` and/or `pattern` to enumerate types."

    return "Union(" + (
        ",\n".join(
            fullname(t) for t in find_matches(mod, typ=typ, pattern=pattern)
        )
    ) + ")\n"
