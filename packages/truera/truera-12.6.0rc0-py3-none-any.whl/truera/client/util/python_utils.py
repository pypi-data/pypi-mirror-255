"""
# Python utilities

- Owners: piotrm

Core utilities for various low-level python features. Avoid circular imports by
not importing any other truera sources.
"""

from copy import copy
import functools
import importlib
import inspect
from inspect import BoundArguments
from pathlib import Path
import sys
import types
from typing import Any, Callable, Dict, Optional, Tuple, Union

# NOTE(piotrm): Some functions here would make better sense to put in func_utils
# but since we use them in type_utils and other core utils, we have to include
# them here to avoid circular imports.

# These are here to avoid circular imports.
Annotation = Union[type, str]
ObjLike = Union[object, str]  # str may be object so unsure about this

# logger = logging.getLogger(name=__name__)


class CodeMapper():
    """
    Utility for recording locations of lines of code to be used in tests that
    check for code locations. An example of this is the parameter inference
    system in quicker quickstart NLP that records and presents various code
    locations to the user when something goes wrong. This CodeMapper class is
    used to test that the code tracking functionality is working as intended.
    """

    default_mapper = None

    def __init__(self):
        # Names mapping to a path and a line number (a code location).

        self.sites: Dict[str, Tuple[Path, int]] = dict()

    def next_line(self, name):
        """
        Give a name to the code location that comes right after the line where
        `next_line` is called.
        """

        frame = caller_frame()
        file = frame.f_code.co_filename
        lineno = frame.f_lineno
        self.sites[name] = (Path(file), lineno + 1)

    # Note: @classmethod @property not working in earlier Pythons.
    @classmethod
    def default(cls) -> 'CodeMapper':
        """
        Return an existing default code mapper (and create one if it doesn't yet exist).
        """
        if cls.default_mapper is None:
            cls.default_mapper = CodeMapper()

        return cls.default_mapper


def get_frameinfo(depth=0):
    """
    Get the frame at the given depth in the call stack.
    """
    return inspect.stack()[depth]


def caller_frame():
    """
    Get the frame of the caller of the method that calls this method, i.e. two
    frames deep in the stack. 
    """
    frameinfo = get_frameinfo(3)  # 2 + 1 more for caller_frame itself.
    return frameinfo.frame


def caller_frameinfo():
    """
    Get the frameinfo of the caller of the method that calls this method, i.e. two
    frames deep in the stack. 
    """
    frameinfo = get_frameinfo(3)  # 2 + 1 more for caller_frame itself.
    return frameinfo


def get_code_location(locinfo) -> Tuple[Path, int]:
    """
    Return the code location pointing to a frame callsite, exception raise site,
    or definition of a callable. Supported are `inspect.FrameInfo` that
    represent a callsite, `tracepoint` which represent the site of an exception
    throw, and function which points to its definition.
    """

    if isinstance(locinfo, inspect.FrameInfo):
        # FrameInfo are generated using get_frameinfo and represent the
        # execution information at the call site `inspect.stack()` inside
        # get_frameinfo relative to some stack depth. Depth is a bit fragile as
        # inserting helper functions between get_frameinfo and the intended
        # tracked callsite requires increasing the depth for each helper.
        file = Path(locinfo.filename)
        line = locinfo.lineno

    elif isinstance(locinfo, types.TracebackType):
        # These are generated during exception handling but the actual site of
        # the raise is at the end of the tb_next-connected chain.
        while locinfo.tb_next is not None:
            locinfo = locinfo.tb_next

        file = Path(locinfo.tb_frame.f_code.co_filename)
        line = locinfo.tb_lineno

    elif isinstance(locinfo, Callable):
        file, line = get_def_site(locinfo)

    else:
        raise ValueError(f"Unknown frame-like object type: {type(locinfo)}.")

    return file, line


def get_def_site(f: Callable) -> Tuple[Path, int]:
    """
    The the location where the given function is defined in terms of a file and
    line number.
    """

    file = inspect.getfile(f)
    line = inspect.findsource(f)[1] + 1

    return Path(file), line


def get_args_callsite(*args, **kwargs) -> inspect.FrameInfo:
    """
    Put a target function's calls as arguments to this function and it will
    produce the frame at which the calls are made. You can use this to debug
    features that track function callsites.
    """
    return caller_frameinfo()


def get_exception_site(thunk) -> inspect.FrameInfo:
    """
    Executes the given thunk and returns the frame at the site where the given
    thunk constructs its exception. This function fails if thunk does not raise
    an exception.
    """

    class UniqueException(Exception):
        pass

    try:
        thunk()
        raise UniqueException()

    except:
        exn_type, _, tb = sys.exc_info()

        if exn_type is UniqueException:
            raise RuntimeError("Thunk did not raise an exception as expected.")

        while tb.tb_next is not None:
            tb = tb.tb_next

        return tb.tb_frame


def copy_bindings(bindings: BoundArguments) -> BoundArguments:
    """
    Duplicate the given bindings into a new BoundArguments object.
    """

    return BoundArguments(
        bindings.signature.replace(), copy(bindings.arguments)
    )


def cache_on_first_arg(func):
    """
    Create a memoized version of `method` that does caching only on the first
    argument, ignoring the rest for cache-lookup purposes.
    """

    cache = dict()

    @functools.wraps(func)
    def wrapper(k, *args, **kwargs):
        kh = hash(k)
        if kh in cache:
            return cache[kh]
        else:
            v = func(k, *args, **kwargs)
            cache[kh] = v
            return v

    return wrapper


def caller_globals():
    frame = inspect.currentframe()
    return frame.f_back.f_back.f_globals


@functools.lru_cache(maxsize=128)
def import_optional_module(module_name: str) -> Optional[types.ModuleType]:
    """
    Split the module importing part of the next method into a cached function
    here as searching for missing modules may be expensive. This returns None if
    module is not imported.
    """

    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


# Might as well cache this as well.
@functools.lru_cache(maxsize=1024)
def import_optional(
    module_name: str, purpose: Optional[str] = None
) -> types.ModuleType:
    """
    Import the module with the given name. If this fails, return an object which
    will raise an exception if it is used for anything indicating that the given
    module was required.

    This can be used to import modules at the top of a python file even if they
    do not exist for a particular SDK deployment. If the methods that rely on
    those imports never get called, things will be fine. Otherwise if someone
    tries to use the optional module without having it installed, an exception
    will be raised with the given `purpose` message. For example, trulens is
    required for SDK for use with neural networks but not for use with
    tabular/diagnostic models; When using tabular, trulens does not need to be
    installed.
    """

    module = import_optional_module(module_name)

    if module is not None:
        return module

    if purpose is not None:
        fail_msg = (
            f"Module {module_name} is required for {purpose}. "
            "You may need to install it."
        )
    else:
        fail_msg = (
            f"Module {module_name} is required. "
            "You may need to install it."
        )

    class FailWhenUsed:

        def __getattribute__(self, _: str) -> Any:
            raise ImportError(fail_msg)

    return FailWhenUsed()
