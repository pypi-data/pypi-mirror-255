"""
# Utilities for dealing with functions and methods

Owners: piotrm
"""

from __future__ import annotations

from abc import ABCMeta
import functools
from inspect import BoundArguments
from inspect import Parameter as IParameter
from inspect import Signature
from inspect import signature
from typing import (
    Any, Callable, Dict, List, Mapping, OrderedDict, Sequence, Tuple, TypeVar
)
import warnings

from truera.client.util.annotations import annotation_isinstance
from truera.client.util.annotations import eval_type
from truera.client.util.annotations import parts_of_annotation
from truera.client.util.annotations import render_annotation
from truera.client.util.debug import retab
from truera.client.util.doc import doc_prepend
from truera.client.util.doc import doc_render
from truera.client.util.python_utils import caller_frame
from truera.client.util.type_utils import AutoNone
from truera.client.util.types import Function
from truera.client.util.types import LogicalType

T = TypeVar("T")
C = TypeVar("C")
U = TypeVar("U")
V = TypeVar("V")

# positional args
PArgs = Tuple[Any]
# keyword args
KWArgs = Mapping[str, Any]
# both
Args = Tuple[PArgs, KWArgs]

# logger = logging.getLogger(name=__name__)


class Const():
    """
    Utility for lru_cache or other caching mechanism. Wrap a value in Const for
    cache to ignore it as a parameter for determining whether input differs or
    not as compared to already-computed inputs.
    """

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return True


def compose(fs: Sequence[Callable]) -> Callable:
    """
    Compose the sequence of single arg methods, applied in same order as sequence.
    """

    def composed(arg):
        for f in fs:
            arg = f(arg)
        return arg

    return composed


class Deprecate:
    # TODO: if this piece grows more, move it out into separate file.

    @staticmethod
    def module(name, message, dep_version, remove_version):
        """
        Immediately issue a warning that the module with the given `name` is
        deprecated.
        """

        warnings.warn(
            message=
            f"Module {name} is deprecated since version {dep_version} and will be removed in {remove_version}. {message}",
            category=DeprecationWarning
        )

    @staticmethod
    def method(message, dep_version, remove_version):
        """
        Mark the given method as being deprecated since `dep_version` and that it
        will be removed in version `remove_version`.
        """

        def wrapper(thing):
            if isinstance(thing, classmethod):
                func = thing.__func__
                extra_decorator = classmethod
            elif isinstance(thing, Callable):
                func = thing
                extra_decorator = lambda x: x
            else:
                raise RuntimeError(
                    f"Do not know how to wrap object of type {type(thing)}."
                )

            dep_message = f"Method {func.__name__} is deprecated since version {dep_version} and will be removed in {remove_version}. {message}"

            @functools.wraps(func)
            @extra_decorator
            def f(*args, **kwargs):
                warnings.warn(message=dep_message, category=DeprecationWarning)
                return func(*args, **kwargs)

            # Also add depreciation message to the doc string.
            doc_prepend(f, f"DEPRECATED: {dep_message}")
            return f

        return wrapper


class WrapperMeta(ABCMeta):
    """
    ABC to help enforce some rules regarding wrappers. 
    
    - Attribute protection: classes that mark attributes with "__protected__"
      cannot have those attributes overridden by child classes.
    
    - Initialization requirements: methods marked with "__require__" need to be
      executed during an objects initialization. Mark parent initializers to
      require children to call the parent initializer.

    - Abstract method deprecation. Allows for wrappers to accept old methods in
      place of new renamed ones while issuing deprecation warnings.
    """

    @staticmethod
    def deprecates(oldfunc_name: str, dep_version: str, remove_version: str):
        """
        Mark an abstract method as deprecating the given method (name). During
        class construction, the marked field will be filled in using the oldfunc
        method if it exists, issuing a deprecation warning.
        """

        def wrapper(absfunc):
            # TODO: figure out a working way to detect whether absfunc is an
            # abstractmethod.

            #  assert isinstance(absfunc, abstractmethod), "This deprecation wrapper is meant for abstract methods only."

            absfunc.__deprecates__ = (oldfunc_name, dep_version, remove_version)

            return absfunc

        return wrapper

    # TODO: try to reuse typing.final
    @staticmethod
    def protect(obj) -> Any:
        """Decorator to mark the given object as protected."""

        if isinstance(obj, Callable) or isinstance(obj, classmethod):
            obj.__protected__ = True

        elif isinstance(obj, property):
            if obj.fset is not None:
                obj.fset.__protected__ = True
            if obj.fget is not None:
                obj.fget.__protected__ = True
            if obj.fdel is not None:
                obj.fdel.__protected__ = True

        else:
            raise ValueError(f"Unhandled object type to protect: {type(obj)}")

        return obj

    def __check_protect(obj, attr, base_name, class_name):
        """
        Check if the given object is marked protected and if so, throw an error
        with the other args as debugging info.
        """

        if hasattr(obj, "__protected__") and getattr(obj, "__protected__"):
            raise AttributeError(
                f"Attribute {attr} of {base_name} should not be overriden in child class {class_name}."
            )

    def __check_deprecates(base_val, attr, attrs):
        """
        Check if an abstractmethod in `base_val` named `attr` is defined in
        `attrs` by its old name.
        """

        if hasattr(base_val.__func__, "__deprecates__"):

            oldmethod_name, dep_version, remove_version = getattr(
                base_val.__func__, "__deprecates__"
            )

            if oldmethod_name in attrs:
                # Issue warning.
                warnings.warn(
                    f"Method {oldmethod_name} is deprecated since {dep_version} and will be removed in {remove_version}. "
                    f"The method was renamed to {base_val.__func__.__name__}.",
                    DeprecationWarning
                )

                # Replace the abstract method with concrete implementation from `oldmethod_name`.
                attrs[attr] = attrs[oldmethod_name]
            else:
                # Leave abstract, will cause abstractmethod undefined in parent __new__ .
                pass
        else:
            # This should cause abstracmethod needs to be defined in the parent __new__ .
            pass

    @staticmethod
    def require(func) -> Any:
        """
        Decorator to mark the given method as required during initialization and
        must be overriden.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.__require__ = False
            return func(*args, **kwargs)

        wrapper.__require__ = True

        return wrapper

    @staticmethod
    def require_if_extended(func) -> Any:
        """
        Decorator to mark the given method as required during initialization but
        does not need to be overriden.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.__require__ = False
            return func(*args, **kwargs)

        wrapper.__require__ = True
        wrapper.__extend_optional__ = True

        return wrapper

    def __init__(cls, name, bases, attrs):
        """
        When instantiating an object, do some checks and wraps some methods
        depending on what the object is.
        """

        if len(bases) == 0:
            # If instantiating metaclass itself, do nothing.
            super().__init__(name, bases, attrs)
            return

        # Otherwise the instantiated object has some parent class base.
        # TODO: What if they have more than one?

        if not "__init__" in attrs:
            # If the child class has no initializer of its own, check if we wanted it to.

            if hasattr(bases[0], "__init__") and hasattr(
                bases[0], "__require__"
            ) and not hasattr(bases[0].__init__, "__extend_optional__"):
                # If your parent has an init with is required, you need to have an init (and call the parent).
                raise AttributeError(
                    f"Wrapper class {name} needs to define __init__."
                )
            else:
                # If we did not want child class to have __init__ of its own, nothing else to do.

                super().__init__(name, bases, attrs)
                return

        init = attrs['__init__']

        if hasattr(init, "__require__"):
            # If the child we are looking at is one annotated with require, we
            # are in one of the base wrapper classes. No more enforcements for
            # those.

            super().__init__(name, bases, attrs)
            return

        # Otherwise we have a child class that has an init and extended one of the wrapper classes.
        # We wraper the init method as follows:

        @functools.wraps(init)
        def wrapper(self, *args, **kwargs):
            nonlocal init

            # Set the __require__ mark for all base classes that have the mark to True.
            for base in bases:
                if hasattr(base, "__init__"):
                    baseinit = getattr(base, "__init__")
                    if hasattr(baseinit, "__require__"):
                        baseinit.__require__ = True

            # Call the child initializer.
            init(self, *args, **kwargs)

            # Check that __required__ marks have now been changed to False. Note that this is done
            # by the wrapper in the @require decorator.
            for base in bases:
                if hasattr(base, "__init__"):
                    baseinit = getattr(base, "__init__")
                    if hasattr(baseinit, "__require__"):
                        if baseinit.__require__:
                            raise RuntimeError(
                                f"Class {base.__name__} initializer must be called by child class {name}."
                            )

        # Update the created class' initializer with the wrapper.
        cls.__init__ = wrapper
        attrs['__init__'] = wrapper  # not sure if this is needed too

        super().__init__(name, bases, attrs)

    def __new__(meta, name, bases, attrs):
        """
        When creating a new instance, check if any attributes are defined in the
        parent class and are labeled as protected. If so, throw an error. Also
        check for deprecated abstractmethods to point them to new names while
        issuing warnings.
        """

        for base in bases:
            # Check all the bases.

            for attr, base_val in base.__dict__.items():
                if hasattr(base_val, "__func__"):
                    # if abstract, check if for deprecated methods that can be renamed

                    meta.__check_deprecates(base_val, attr, attrs)

            for attr in attrs:
                # For each attribute in the created class.

                if hasattr(base, attr):
                    # Check if the base class also has that attribute.

                    base_val = getattr(base, attr)

                    # Checks need to be done differently for some objects than others.
                    # property in particular does not like creating new attributes to mark
                    # protection, hence this condition here.

                    if isinstance(base_val, Callable
                                 ) or isinstance(base_val, classmethod):

                        # And if so, whether it is marked as protected.
                        meta.__check_protect(
                            base_val, attr, base.__name__, name
                        )

                    elif isinstance(base_val, property):
                        # If attribute in base class was a property, check whether any of its
                        # constituent methods were marked protected.
                        if base_val.fget is not None:
                            meta.__check_protect(
                                base_val.fget, attr, base.__name__, name
                            )
                        if base_val.fset is not None:
                            meta.__check_protect(
                                base_val.fset, attr, base.__name__, name
                            )
                        if base_val.fdel is not None:
                            meta.__check_protect(
                                base_val.fdel, attr, base.__name__, name
                            )
                    else:
                        pass

        return super().__new__(meta, name, bases, attrs)


# method decorator
def derive(**derivations: Dict[str, 'decorator']):
    """
    A decorator that creates multiple methods based on the given `func`, each as
    named and wrapped by the given set of `derivations`. Each derivation must be
    a method decorator. Methods derived in this way will need pylint exceptions
    for E1101 at call sites. For example, using:

    # pylint: disable=E1101
    """

    # TODO: modify docstring

    frame = caller_frame()

    try:
        # get the caller's locals so we can give them the derived methods
        locals = frame.f_locals

        def wrapper(func):
            for name, decorator in derivations.items():
                locals[name] = decorator()(func)

            # Returned function is added to caller's locals as per decorator
            # semantics assuming `derive` is used as a decorator.
            return func

        return wrapper
    finally:
        del frame


# method decorator
def singlefun_of_manyfun():
    """
    Convert a method that accepts and returns a list of items to instead
    accept and return a single item. Any args other than the first are preserved.
    """

    def wrapper(func: Callable[[List[U]], List[V]]) -> Callable[[U], V]:

        @functools.wraps(func)
        def ret_fun(item: U, *args, **kwargs) -> V:
            results: List[V] = func([item], *args, **kwargs)
            return results[0]

        return ret_fun

    return wrapper


# method decorator
def self_singlefun_of_self_manyfun():
    """
    Convert a member method that accepts and returns a list of items to instead
    accept and return a single item. Self and args other than the first non-self
    arg are preserved.
    """

    def wrapper(func: Callable[[C, List[U]], List[V]]) -> Callable[[C, U], V]:

        @functools.wraps(func)
        def ret_fun(self: C, item: U, *args, **kwargs) -> V:
            results: List[V] = func(self, [item], *args, **kwargs)
            return results[0]

        return ret_fun

    return wrapper


def render_args_kwargs(args, kwargs):
    """
    Create a representation of args/kwargs lists but shorten large values so
    your screen does not get swamped.
    """

    message = f"args={str(args)[0:128]}\n"
    message += f"kwargs=\n"
    for k, v in kwargs.items():
        message += retab(f"{k}: {str(v)[0:32]}", "\t") + "\n"
    return message


def parameter_typechecks(obj, typ: IParameter, globals):
    """
    Check whether a inspect.Parameter annotation is matched by the given object.
    A such an annotation can be empty in which case we return affirmative.
    """

    if typ is IParameter.empty:
        return True
    return annotation_isinstance(obj, typ, globals=globals)


def bind_relevant(m: Callable, kwargs) -> BoundArguments:
    """
    Create a binding for the given method `m` from the subset of args that are
    parameters to m. This means that other elements of kwargs that do not match
    the signature are ignored.
    """
    sig = signature(m)
    return sig.bind_partial(
        **{
            k: v for k, v in kwargs.items() if k in sig.parameters.keys()
        }
    )


def bind_relevant_and_call(m: Callable[..., T], kwargs) -> T:
    """
    Binding relevant arguments of `m` from `kwargs` and call it with them.
    Return whatever `m` returns.
    """

    bindings = bind_relevant(m, kwargs)

    return m(*bindings.args, **bindings.kwargs)


# Methods related to function signatures


def sig_render(
    func: Function,
    sig: Signature = None,
    withdoc: bool = False,
    override_name: str = None,
    newline_limit: int = 4,
    globals: Mapping = None,
):
    """
    Given a function, produce a string describing its signature in a manner that
    is independent of whether __future__.annotations have been imported or not.

    - `sig` - Use the given signature instead of the one derived from func.
    - `withdoc` - Also include the docstring.
    - `override_name` - Use the given string as the function's name, useful for
      overloaded functions.
    """

    func_name = func.__name__
    if override_name is not None:
        func_name = override_name

    sig = sig or signature(func)
    if globals:
        sig = sig_eval_annotations(sig, globals=globals)

    if withdoc and func.__doc__ is not None:
        ret = doc_render(func) + "\n"
    else:
        ret = ""

    ret += f"{func_name}("

    mods = []

    arg_parts = []

    for name, param in sig.parameters.items():
        arg_ret = ""

        if name == "self" or name.startswith("_Explainer"):
            continue

        if param.kind is IParameter.VAR_KEYWORD:
            arg_ret += "**"
        elif param.kind is IParameter.VAR_POSITIONAL:
            arg_ret += "*"

        arg_ret += f"{name}"

        annot = param.annotation
        while isinstance(annot, LogicalType) and hasattr(annot, "typ"):
            annot = annot.typ

        if annot is not IParameter.empty:
            if isinstance(annot, LogicalType) and hasattr(annot, "types"):
                annot_str = f": {annot.__class__.__name__}["
                for typ in annot.types:
                    _mod, annot = parts_of_annotation(typ)
                    if _mod is not None:
                        mods.append(_mod)
                    annot_str += render_annotation(typ)
                annot_str += "]"
            else:
                _mod, annot = parts_of_annotation(annot)
                if _mod is not None:
                    mods.append(_mod)
                arg_ret += f": {render_annotation(annot)}"

        if param.default is not IParameter.empty:
            arg_ret += f"={param.default}"

        arg_parts.append(arg_ret)

    if len(sig.parameters) >= newline_limit:
        space = "\n  "
        ret += space + f",{space}".join(arg_parts) + '\n'
    else:
        ret += ", ".join(arg_parts)

    _mod, annot = parts_of_annotation(sig.return_annotation)
    if _mod is not None:
        mods.append(_mod)
    ret += f") -> {render_annotation(sig.return_annotation)}"

    if withdoc:
        if len(mods) > 0:
            # Add a list of required modules to the doc string. Disabled for now because it includes
            # pre-installed ones as well. Need to filter them out.
            # ret += f"({', '.join(mods)} required)\n"
            pass
        else:
            pass
            # ret += "\n"
    ret += "\n"
    return ret


def sig_eval_annotations(sig: Signature, globals) -> Signature:
    """
    Replaces annotations that are still strings due to delayed annotation
    evaluation, and evaluates them to types they represent.
    """

    new_params = OrderedDict(sig.replace().parameters)

    for name, param in sig.parameters.items():
        annot = param.annotation

        if annot is not IParameter.empty:
            annot_type = eval_type(annot, globals)
            new_param = param.replace(annotation=annot_type)
            new_params[name] = new_param

    ret_annot = sig.return_annotation
    if ret_annot is not IParameter.empty:
        ret_annot = eval_type(ret_annot, globals)

    return sig.replace(
        parameters=new_params.values(), return_annotation=ret_annot
    )


def sig_fill_defaults(sig: Signature, globals) -> Signature:
    """
    Replaces parameters that have annotation marked AutoNone but have no default
    value, to instead have a default None.
    """

    new_params = OrderedDict(sig.replace().parameters)

    for name, param in sig.parameters.items():
        annot = param.annotation

        default = param.default

        if default is not IParameter.empty:
            continue

        if annot is not IParameter.empty:
            annot_type = eval_type(annot, globals)

            if annotation_isinstance(annot_type, AutoNone, globals):
                new_param = param.replace(default=None)
                new_params[name] = new_param

    return sig.replace(parameters=new_params.values())
