"""
# Utilities for dealing with __future__.annotations

- Owners: piotrm

Some part of these utilities are for consistently dealing with method
annotations under __future__.annotation and without it. You will find `TypeLike`
to signify something which already is a type or a string which needs to be
evaluated to retrieve the named type.

The benefit of __future__.annotations, however, is that we can type more things
that might not otherwise be typable. Additionally, the same handling we need for
this feature are also useful for referring to types that come from optionally
installed packages without producing errors when they are not installed.
"""

import importlib
import logging
from typing import Any, Iterable, Tuple

from truera.client.util.python_utils import Annotation
from truera.client.util.python_utils import cache_on_first_arg
from truera.client.util.python_utils import ObjLike
from truera.client.util.type_utils import is_typelike
from truera.client.util.type_utils import Never

logger = logging.getLogger(name=__name__)


def render_annotation(annot: Annotation) -> str:
    mod, name = parts_of_annotation(annot)
    if mod is None or mod == "builtins" or mod.startswith("truera."):
        # Don't bother printing "builtins" as those are always available in
        # globals. Also don't print truera module names. Those should be
        # documented in ingestion examples.
        return name
    else:
        return f"{mod}.{name}"


def parts_of_annotation(annot: Annotation) -> Tuple[str, str]:
    """
    Given an annotation which is a type or string that may optionally be wrapped
    in quotes if __future__.annotations is used, produce its module of origin
    and name. If the annotation does not refer to a module, returns None for
    that portion.
    """

    if is_typelike(annot):
        module = None,
        if hasattr(annot, "__module__"):
            if hasattr(annot.__module__, "__name__"):
                module = annot.__module__.__name__
            else:
                module = str(annot.__module__)

        name = None
        if hasattr(annot, "__name__"):
            name = getattr(annot, "__name__")
        elif hasattr(annot, "_name"):
            # Python < 3.10
            name = getattr(annot, "_name")
        return module, name

    if annot[0] in ["'", '"'] and annot[0] == annot[-1]:
        annot = annot[1:-1]
        if "." in annot:
            parts = annot.split(".")
            return parts[0], annot
        else:
            return None, annot
    else:
        return None, annot


def eval_object(obj: ObjLike, globals={}) -> object:
    """
    Given an object or a string that names it, produce the object if possible.
    Might return None if the module containing that object cannot be loaded
    (i.e. not installed).
    """
    if isinstance(obj, str):
        return get_object_by_name(obj, globals=globals)
    else:
        return obj


@cache_on_first_arg
def eval_type(typ: Annotation, globals={}) -> type:
    """
    Given a type or a string that evaluates to it, produce the type if possible.
    Might return None if the module containing that type cannot be loaded (i.e.
    not installed).
    """

    if is_typelike(typ):
        return typ
    else:
        return get_type_by_name(typ, globals=globals)


@cache_on_first_arg
def get_type_by_name(typ: Annotation, globals={}) -> type:
    obj = get_object_by_name(typ, globals)

    if isinstance(obj, Iterable):
        obj = tuple(get_type_by_name(part, globals=globals) for part in obj)
        return obj

    if not is_typelike(obj):
        if obj is None:
            logger.warn(
                f"Annotation {typ} is not a type, use `NoneType` instead."
            )
        else:
            logger.warn(
                f"Annotation {typ} does not refer to a type. If this is a literal value use its literal type `Literal({typ})`."
            )
        return Never

    return obj


# @functools.lru_cache(maxsize=128, ) # cannot use this cache with globals
@cache_on_first_arg
def get_object_by_name(obj: ObjLike, globals={}) -> object:
    """
    When using "from __future__ import annotations", all annotations are
    strings. Those which were specified as strings get further quoted inside the
    string like:

        def func(arr: 'numpy.ndarray): ...

    The annotation for `arr` will be:

        "'numpy.ndarray'"

    That is, a string with an additional ' quotation. On the other hand, for:

        def func(arr: numpy.array): ...

    The annotation will be:

        "numpy.ndarray"
    """

    if not isinstance(obj, str):
        return obj

    if obj[0] in ['"', "'"] and obj[0] == obj[-1]:
        obj = obj[1:-1]

    try:
        # Module might already be loaded and available in globals. For
        # example in "import numpy as np". Then "np" will be numpy in that
        # context. Globals needs to be known for this to work though.

        typ = eval(obj, globals)

        if isinstance(typ, str):
            # Might have been a string that evaluates to a string, which
            # eventually evaluates to a type.
            return get_object_by_name(typ, globals)
        else:
            return typ

    except Exception as e:
        # Otherwise assume the type is written as "module...attribute" so we
        # first try to import top-level module. This allows us to refer to types
        # without importing them ahead of time.

        logger.debug(f"Could not evaluate '{obj}': {e}.")
        pass  # continue

    if "." not in obj:
        logger.warn(f"Could not evaluate object from string '{obj}'.")
        return Never

    else:
        addr = obj.split(".")
        mod_name = addr[0]
        addr = addr[1:]

    try:
        mod = importlib.import_module(mod_name)

    except BaseException as e:
        logger.warn(
            f"Could not import module {mod_name} because {e}. This may be ok unless you expect to use this module."
        )
        # This is expected if module is not installed.
        return Never

    try:
        # Get sub-modules or final attribute.
        for comp in addr:
            mod = getattr(mod, comp)

        return mod

    except Exception as e:
        # This is less expected but could still happen for example due to
        # differing tensorflow versions that all have the same top-level name
        # but different contents.
        logger.debug(
            f"Loaded module for {obj} but could not load type/class because {e}."
        )
        return Never


def annotation_isinstance(obj: Any, annot: Annotation, globals={}) -> bool:
    """
    `isinstance` equivalent that works for more things including types given by
    name as is the case when delayed type evaluation is enabled (annotations in
    __future__).
    """

    annot_type = eval_type(annot, globals=globals)

    return isinstance(obj, annot_type)


def annotation_issubclass(
    annot1: Annotation, annot2: Annotation, globals={}
) -> bool:
    """
    `issubclass` equivalent that works for more things including types given by
    name as is the case when delayed type evaluation is enabled (annotations in
    __future__).
    """

    annot1_type = eval_type(annot1, globals=globals)
    annot2_type = eval_type(annot2, globals=globals)

    return issubclass(annot1_type, annot2_type)
