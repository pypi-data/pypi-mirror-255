"""
# Function overloading

Owners: piotrm

This file contains an implementation of function overloading that has some
features that the standard `overload` module does not.

# Caveats

The overloading scheme relies on type annotations and on those annotations to
support isinstance/issubclass. Because of this, you cannot use most of the type
aliases in `typing.*` as they are not actual types. Some of the more useful type
constructors like `Union` implemented as types are in `types.py` but you should
use them only if you need the type checking functionality like overload does.
"""

from copy import copy
from dataclasses import dataclass
import functools
from inspect import BoundArguments
from inspect import Parameter as IParameter
from inspect import Signature
from inspect import signature
import logging
from types import MethodType
from typing import Callable, Iterable, Mapping, Optional, Sequence, TypeVar

from truera.client.util.annotations import annotation_isinstance
from truera.client.util.debug import Capture
from truera.client.util.debug import code_location_string
from truera.client.util.debug import render_exception
from truera.client.util.func import Args
from truera.client.util.func import KWArgs
from truera.client.util.func import parameter_typechecks
from truera.client.util.func import PArgs
from truera.client.util.func import render_args_kwargs
from truera.client.util.func import retab
from truera.client.util.func import sig_eval_annotations
from truera.client.util.func import sig_fill_defaults
from truera.client.util.func import sig_render
from truera.client.util.python_utils import caller_globals
from truera.client.util.type_utils import Monoid
from truera.client.util.types import Function
from truera.client.util.types import Parameter

logger = logging.getLogger(name=__name__)


@dataclass
class OverloadOption:
    sig: Signature
    sig_annotated: Signature
    func: Function


# Accumulator passed through bindings hook.
A = TypeVar("A")

BindingsHook = Callable[[A, Callable, Signature, BoundArguments],
                        BoundArguments]
ArgsHook = Callable[[PArgs, KWArgs], Args]


def sig_bind(
    func: Function,
    sig: Signature,
    args: tuple,
    kwargs: dict,
    post_bind_hooks: Iterable[BindingsHook] = None,
    globals: dict = {}
) -> Optional[BoundArguments]:
    """
    Given a signature `sig`, check whether it matches the given arguments in
    `args` and `kwargs` as if the user called a method with that signature with
    those args.

    `globals` is required to retrieve types from their names in case that
    __future__.annotations is enabled.

    If `post_bind_hooks` are provided, those functions can transform bindings
    AFTER signature is matched. 

    Returns the bound arguments object if successful or None otherwise.
    """

    post_bind_hooks = post_bind_hooks or []

    _typechecks = functools.partial(parameter_typechecks, globals=globals)

    sig = sig.replace()  # copy

    # Accumulate required positional args here.
    positional = []
    # Accumulate keyword bindings here.
    keyword = dict()

    # Will be emptying these out so make a copy first.
    args = list(args)  # list for popping
    kwargs = copy(kwargs)  # will be popping, don't want to affect the given one

    # Track whether signature has *args or **kwargs. This will determine whether
    # it is ok to have args or kwargs left over.
    had_varargs = False
    had_varkwargs = False

    for i, (name, param) in enumerate(sig.parameters.items()):
        typ = param.annotation

        default = param.default
        kind = param.kind

        if name in kwargs:
            # TODO: Should we check that parameter can be keyword?

            if _typechecks(kwargs[name], typ):
                keyword[name] = kwargs[name]
                del kwargs[name]

            # This is needed if we don't use our own Optional type:
            # elif default is not Parameter.empty and kwargs[name] is None:
            # Ok to provide None for an optional parameter, in which case
            # the dispatcher will just delete that argument before
            # dispatching.

            else:
                # A keyword argument's type did not match. This means signature
                # does not match so we return None to indicate that.
                return None

        elif (
            kind is IParameter.POSITIONAL_ONLY or
            kind is IParameter.POSITIONAL_OR_KEYWORD
        ) and len(args) > 0 and _typechecks(args[0], typ):
            # If no type is given or type matches, put it onto list of required positional args
            positional.append(args.pop(0))

            # Otherwise the type of a required positional arge does not
            # match but might match some keyword parameter's type. This will
            # be handled in the further case below.

        elif kind is IParameter.VAR_POSITIONAL:
            had_varargs = True

        elif kind is IParameter.VAR_KEYWORD:
            had_varkwargs = True

        else:
            # In this case a parameter's name was not in kwargs but there might
            # be a value of the right type in the remining positional values. So
            # we try to find it.

            vals_of_type = [
                (i, v)
                for i, v in enumerate(args)
                if annotation_isinstance(v, typ, globals=globals)
            ]

            if len(vals_of_type) == 1:
                i, v = vals_of_type[0]
                args.pop(i)

                if kind is IParameter.POSITIONAL_ONLY:
                    positional.append(v)

                elif kind is IParameter.KEYWORD_ONLY or kind is IParameter.POSITIONAL_OR_KEYWORD:
                    keyword[name] = v

                else:
                    raise RuntimeError(f"Unhandled annotation kind {kind}.")

            elif len(vals_of_type) > 1:
                raise ValueError(
                    f"Found more than 1 matching positional argument for {name}: {typ}"
                )

            elif default is not IParameter.empty:
                keyword[name] = default

            else:
                # did not match this parameter
                return None

    # Return failure if there were positional args left over but signature did not have a *args.
    if len(args) > 0 and not had_varargs:
        return None

    if len(kwargs) > 0:
        # Similarly for keyword args.
        if not had_varkwargs:
            return None

    bindings = sig.bind(*positional, *args, **keyword, **kwargs)
    bindings.apply_defaults()

    acc = None
    for hook in post_bind_hooks:
        acc, bindings = hook(acc=acc, func=func, sig=sig, bindings=bindings)

    return bindings


class Undispatch(Exception):
    """
    Throw this in an overloaded method to pretend like that method
    should not have been called, and continue looking for other matching methods.
    """
    pass


def overload(
    accumulate: Optional[Monoid] = None,
    pre_bind_hooks: Optional[Sequence[ArgsHook]] = None,
    post_bind_hooks: Optional[Sequence[BindingsHook]] = None,
    fill_defaults: bool = True
):
    """
    Decorator to specify a method to overload. Attaches several things to the
    returned method which are then used to define additional implementations, as
    well as replacing the method with a dispatching mechanism which selects from
    among the overloaded methods based on their signatures as compared to given
    arguments when called.

    If optional `accumulate` monoid is provided, all matching methods are called
    and their result is combined using the given monoid. Without the monoid,
    only the first matching method is called unless that call throws
    `Undispatch` in which case the next matching method is called.

    Functions specified in `post_bind_hooks` are called on the bound
    variables of matching overloaded functions before they are called and can
    change those bindings if needed (i.e. replace default values).

    Functions specified in `pre_bind_hooks` are called on args, kwargs before
    any matching is attempted.

    If `fill_defaults` is true, annotations subclassing `AutoNone`
    will get their defaults set to `None` if not already set.

    Overloaded methods may call each other but you have to be careful to not go
    into an infinite call loop.

    Returns callable class with attributions/methods:

    - register: the method used to add additional method definitions to
      overload.
    - options: the collection of methods overloaded.
    - render_options: method to render the collection of methods overloaded.
    """

    # Need to get caller's globals in case they provide type annotations via
    # module aliases like np for numpy. This only applies to delayed annotations
    # enabled with __future__.annotations .
    globals = caller_globals()

    class Dispatch(Callable):

        def __init__(self, firstf: Callable, user_visible: bool = True):
            assert isinstance(
                firstf, Callable
            ), f"Callable expected, got {type(firstf)} instead."

            # The list of overloaded signatures/methods including the first one.
            self.options: list[OverloadOption] = []

            # Keep track of the first method. Will be adjusting subsequence overloads with
            # this one's name and adding to this method's docstring.
            self.firstf = firstf

            if hasattr(firstf, "__doc__"):
                self.doc = firstf.__doc__
            else:
                self.doc = None

            # First method's name which will be replicated into all other registered
            # methods.
            self.firstname = firstf.__name__

            self.__name__ = self.firstname
            # Make all of the options show up under the same name, does not impact
            # being able to call them by their original name if needed

            # Adjust the dispatch's doc string to include, presently, just the first
            # method.

            self.is_method = False
            self.callable_type = "function"

            self.pre_bind_hooks = pre_bind_hooks or []
            self.post_bind_hooks = post_bind_hooks or []
            self.fill_defaults = fill_defaults

            if isinstance(firstf, MethodType):
                # Methods have a pre-bound first argument refering to instance
                # or class. TODO(piotrm): This does not work: whether this is a
                # method or function is not known at the time the containing
                # class is defined. Our own wrapper gets wrapped as a method
                # with bound self by the getattribute method of the class in
                # which we use overload.
                self.is_method = True
                self.callable_type = "method"

            # We must return from the decorator a function, not a method. At the
            # same time, we need to refer to self in said function. So we create
            # a function here that captures self from its scope instead of an
            # argument.

            def dispatch(*args, **kwargs):
                return self(*args, **kwargs)  # __call__

            dispatch.register = self.register
            dispatch.get_options_for = self.get_options_for
            dispatch.__name__ = self.firstname
            dispatch.dispatch = self

            self.dispatch = dispatch

            self.register(user_visible=user_visible)(firstf)

            self.redoc()

        def __call__(self, *args, _db: bool = False, **kwargs):
            # The main functionality, the dispatch method replacing the firstf
            # decorated method determines which of the registered options to use
            # given the provided arguments.

            for hook in self.pre_bind_hooks:
                args, kwargs = hook(args=args, kwargs=kwargs)

            # Keep track of matching calls to print out an error message if they all fail.
            failed_calls = []

            # If monoid given, start with a zero.
            if accumulate is not None:
                ret = accumulate.zero()

            # Keep track if any signature matched the given args.
            matched = False

            # For each signature/method in order they were registered.
            for option in self.options:
                cap_bind = Capture.for_term()

                try:
                    # Forward only the relevant args, ie. check if it matches
                    # the given args. TODO(piotrm): check if this is still
                    # needed after independent inferences of psys.py are used.
                    forward_kwargs = {
                        k: kwargs[k]
                        for k in kwargs
                        if k in option.sig.parameters.keys()
                    }
                    with cap_bind:
                        bindings = sig_bind(
                            func=option.func,
                            sig=option.sig,
                            post_bind_hooks=self.post_bind_hooks,
                            globals=globals,
                            args=args,
                            kwargs=forward_kwargs
                        )
                except Exception as e:
                    if _db:
                        print(
                            f"{code_location_string(locinfo=option.func)} option failed"
                        )
                        cap_bind.display()
                    else:
                        failed_calls.append((option, e, cap_bind))
                    continue

                # Not None means it matched.
                if bindings is not None:
                    logger.debug(f"matched {option.sig}")

                    if _db:
                        print(
                            f"{code_location_string(locinfo=option.func)} trying option"
                        )

                    # TODO: need some infinite recursion check here. The below doesn't quite work.
                    # Make sure we are not going in circles.
                    # st = inspect.stack()
                    # if st[2].function == "dispatch":
                    #    if st[1].frame == st[3].frame:
                    #        raise RuntimeError(
                    #            "Dispatched methods are calling themselves in circles."
                    #        )

                    # Call the matched method, catching Undispatch
                    cap_call = Capture.for_term()
                    try:
                        with cap_call:
                            next_ret = option.func(
                                *bindings.args, **bindings.kwargs
                            )
                    except Undispatch as e:
                        # If caught Undispatch, continue loop until another
                        # method matches.
                        failed_calls.append((option, e, cap_call))
                        continue
                    except Exception as e:
                        failed_calls.append((option, e, cap_call))
                        continue
                    else:
                        # Otherwise after a successful call,

                        if _db:
                            cap_bind.display()
                            cap_call.display()

                        if accumulate is not None:
                            # Accumulate its result if monoid was provided.
                            ret = accumulate.plus(ret, next_ret)
                        else:
                            # Or return it if no monoid was provided.
                            return next_ret

                    # Only happens in accumulator mode, make note that some
                    # method matched.
                    matched = True

                else:
                    # Signature did not match.
                    pass

            # Return the accumulated results in accumulation mode.
            if matched:
                return ret

            # Otherwise construct an error message that includes all of the
            # registered options.
            message = f"Failed all `{self.firstname}` definitions. Given arguments:\n\n"
            message += retab(render_args_kwargs(args, kwargs), tab="\t") + "\n"

            if len(failed_calls) > 0:
                message += "Failed calls:\n\n"
                for option, exc, cap in failed_calls:
                    # If overloaded method raises NotImplementedError, avoid showing to users.
                    if not isinstance(exc, NotImplementedError):
                        message += retab(
                            sig_render(
                                option.func,
                                sig=option.sig_annotated,
                                withdoc=True,
                                override_name=self.firstname
                            ), "\t"
                        ) + "\n\n"
                        message += retab(
                            "FAILURE: " +
                            retab(render_exception(exc), "\t", tab_first=False),
                            "\t"
                        ) + "\n\n"
                        message += str(cap.summary())

                message += "\n\n"

            message += "Options are:\n\n"
            message += retab(self.render_options(), "\t")

            raise TypeError(message)

        def get_options_for(self, *args, **kwargs):
            for option in self.options:
                # TODO(piotrm): Figure out if we need to keep the dispatch
                # method's kwargs filtering step and if we therefore need it
                # here too.

                # Check if it matches the given args.
                try:
                    bindings = sig_bind(
                        sig=option.sig,
                        func=option.func,
                        globals=globals,
                        args=(self,) + args,
                        kwargs=kwargs
                    )

                    if bindings is not None:
                        yield option.func

                except:
                    pass

        def render_options(
            self, withdoc: bool = False, globals: Mapping = None
        ) -> str:
            """
            Create a string listing all the registered signatures.
            """

            message = ""
            for option in self.options:
                if option.func.__user_visible__:
                    # Override the name of the method in the signature so that all
                    # listed methods appear to have the same name as the first
                    # overloaded method.
                    message += sig_render(
                        option.func,
                        sig=option.sig_annotated,
                        override_name=self.firstname,
                        withdoc=withdoc,
                        globals=globals
                    )
                    message += "\n\n"

            return message

        def register(self, *args, **kwargs):
            """
            Decorator to add a new method to the list of overloaded options for
            the originally decorated method. Returns the registered method as
            is. You can use this to name overloaded methods different things and
            call them explicitly outside of the dispatch mechanism, while still
            using the mechanism for calls to the first registered method.
            """

            # Keep track of the original signature which might have strings
            # instead of types in annotations.

            user_visible = kwargs.pop("user_visible", True)

            def _register(f: Callable) -> Callable:
                annotation_sig = signature(f)
                sig = annotation_sig

                # Fill in default values if configured to do so.
                if self.fill_defaults:
                    sig = sig_fill_defaults(sig, globals=globals)

                # Evaluate annotations to their types in case delayed annotations
                # are enabled.
                sig = sig_eval_annotations(sig, globals=globals)
                missing_help_doc_params = []
                for param in sig.parameters.values():
                    if param.name != "self":
                        # Annotations might be wrapped in Optional or Given. Get the base parameter:
                        base_annot = Parameter.base_param(param.annotation)
                        assert base_annot is not None, f"User-facing method {f.__name__} (overloading {self.firstname}) argument {param.name} was not annotated with param but with {param.annotation} instead."

                        # Check that it has help_doc .
                        # TODO: Renable this test at some point once help_docs are ready.
                        if base_annot.help_info is None:
                            missing_help_doc_params.append(base_annot)

                assert len(
                    missing_help_doc_params
                ) == 0, f"User-facing method {f.__name__} (overloading {self.firstname}) arguments {missing_help_doc_params} have no help_info."

                f.__signature__ = sig
                f.__overload_name__ = self.firstname
                f.__user_visible__ = user_visible

                self.options.append(
                    OverloadOption(
                        sig=sig, sig_annotated=annotation_sig, func=f
                    )
                )
                self.redoc()

                # Note that we are not returning the dispatch here but instead the
                # function being registered in the dispatch. This lets us to refer
                # to it specifically by whatever name it was defined with when
                # decorated without going through the dispatch if we need to.
                return f

            if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
                # If no kwargs were given, we are being called without parentheses
                # and therefore need to return the decorator itself.
                assert user_visible == True
                return _register(args[0])
            else:
                # Otherwise we are being called with parentheses and need to return
                # the result of the decorator.
                return _register

        def redoc(self, doc: str = None):
            if doc is not None:
                self.doc = doc

            # Update the docstring of the wrapper of the first function
            # decorated with overload (the one the user gets a handle on).
            self.dispatch.__doc__ = (
                self.doc + "\n\n" if self.doc is not None else ""
            ) + (
                f"This method is an overloaded {self.callable_type} with multiple valid signatures. Options are:\n\n"
                + retab(
                    self.render_options(withdoc=True, globals=globals),
                    tab="\t"
                )
            )

    def wrapper(*args, **kwargs):
        user_visible = kwargs.pop("user_visible", True)

        def _wrapper(firstf):
            d = Dispatch(firstf, user_visible=user_visible)

            # We return a function, not a method, not an instance. The function comes with
            # various "sub-functions" like register to add more options to the overload.
            return d.dispatch

        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # If no kwargs were given, we are being called without parentheses
            # and therefore need to return the decorator itself.
            return _wrapper(args[0])
        else:
            # Otherwise we are being called with parentheses and need to return
            # the result of the decorator.
            return _wrapper

    return wrapper

    # End of def overload(...)
