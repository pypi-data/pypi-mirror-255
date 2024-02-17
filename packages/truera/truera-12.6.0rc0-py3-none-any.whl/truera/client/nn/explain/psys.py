"""
# "Parameter System"

A scheme to "automatically" dispatch methods to derive values for requested
parameters. This scheme is similar to the overloading scheme of
`func_utils.overload` but distinct in some critical ways. While `overload`
resembles method overloading from object oriented programming, this rule system
resembles more a constraint satisfaction system as in prolog.

We demonstrate the parameter system via examples below. 

## The Basics

Parameters are subclasses of `type_utils.Parameter`. They can be treated as
types.

```python
    PArg1 = Parameter("first argument", desc="some documentation about it", typ=int)
    PArg2 = Parameter(...)
    PArg3 = Parameter(...)
```

Then lets say we want to define a function `fun` that accepts some parameters
which we want to be derived automatically:

```python
    def fun(arg1: PArg1, arg2: PArg2) -> int:
        return arg1 + arg2
```

The main interface to the parameter inference system is the `Rules` class,
instantiated and instrumented as follows:

```python
    rules = Rules()
    
    @rules.register_rules
    class Inferences:
        def name_does_not_matter() -> PArg1:
            return 42

        def infer_arg2(arg3: PArg3) -> PArg2:
            return arg3 + 100

        def infer_arg3(arg1: PArg1) -> PArg3:
            return arg1
```

This indicates that the class `Inferences` contains inference rules to be used
for deriving values for parameters. The names of the functions is not important.
Their type annotations are used for determining which rules are applicable to a
derivation. `infer_arg2`, for example, is a "rule" that can infer a value for
`PArg2` if it is provided a value for `PArg3`.

In order to call `fun` which needs both `PArg1` and `PArg2` we can use
`Rules.bind`:

```python
    binding = rules.bind(func=fun, ...)
    # Hidden parameters are for a case when you have some part of `fun`'s args. 
    # Ignore the fact that `bind` returns iterable, more on that later.
```

This gives you BoundArgumets which you can use to call `fun`:

```python
    result = fun(*binding.args, **binding.kwargs)
```

Under the hood, `Rules.bind` derives values for `fun`'s arguments using the
rules registered earlier. In the process it calls all of the registered methods.
Notice that it needs to use `infer_arg3` indirectly to be able to call
`infer_arg2`.

## Rule Arguments

The first notable difference between overloading and the rules system is that
the arguments to the rules are selected (and derived) only as needed for the
implementations of those rules. That is, even if we have derived a value for
something prior to deriving a parameter does not mean it will be included in all
subsequent calls. For example, `infer_arg3` above requires only `PArg1` so this
rule will be called only with a value for that argument, and not others like
`PArg2` which was a requirement of `fun` which initiated the derivation process
to begin with.

## Multiple Outputs and their Consistency

The second major difference between this scheme and overloading is that rules
support returning more than one parameter at once and enforcement of consistency
between returned parameters. By consistency here we mean that if a rule is used
that returns more than 1 parameter, those parameters should keep the values they
attained simultanously due to that one rule, and no other rule is allowed to
override one of those parameters. Thus the multiple parameters remain consistent
with each other, being produced together.

To use this feature, define rules with outputs annotated as tuples of
parameters:

```python
    def multiout_rule(...) -> (PArg1, PArg2):
        return (100, 42)
```

Note that even you need to derive just `PArg1` and do not care about `PArg2`, it
is still appropriate to use this rule.

## Multiple Derivations

The rule system is meant to better handle the possibility of multiple
different derivations producing potentially different assignments to the
parameters. In the above example, we actually need to use `bind` like this:

```python
    for binding in rules.bind(func=fun, ...):
        result = fun(*binding.args, **binding.kwargs)
```

That is, `rules.bind` returns an iterable of possible bindings, each derived
differently. While it does not check that the resulting `BoundArguments` are
actually different, this is an expected possibility.

## Names and Parameter Matching

The system derives values for parameters based on the annotations for registered
rules. The way in which an appropriate rules are determined has some subtleties.
First, to derive a value for `PArg1`, any rule that has `PArg1` specifically in
its tuple of outputs can be used. However, a value for this argument can also be
derived via rules for other parameters and if another parameter (matching as
described below) is already known, it can be used for `PArg1`.

A value for parameter `PArg2` can be used as a value for `PArg1` if these
parameters have the same name AND the type of PArg2 is a subtype of PArg1. Save
for the name requirement, this is identical to typical subtyping usage in object
oriented programming: a type B can be used where A is expected whenever B is a
subtype of A.

The subtyping is similar to how `overload` operates but the name requirement
introduces some flexibility and some rigidity. First, the names of the rule
arguments do not matter, only the parameter in their annotations. That is, in
the examples above, names `arg1`, `arg2`, `arg3` are irrelevant. This means it
is easy to get multiple values for parameters that have similar function. For
example, in NLP ingestion, one can define:

```python

    PTorchModel = Parameter("model", desc="a pytorch model", typ=torch.nn.Module)
    PHugsModel = Parameter("model", desc="a huggingface model", typ=...)

    def set_model1(model: PHugsModel): ...
        # use a hugs model

    def set_model2(
        name_does_not_matter: PTorchModel, name_irrelevant: PHugsModel
    ): ...
        # use both a torch model and a huggingface model derived from it, they 
        # may even be the same
```

On the other hand, there is some additional rigidity. In `set_model2`, a value
provided for `name_does_not_matter` is a pytorch model which could also be a
huggingface model (huggingface models are subclasses of torch models). A rule
that expects a huggingface model will not be able to take in the value we passed
in as `name_does_not_matter`, even if it is a huggingface model because the
annotation was a pytorch model. One can write rules, however, to do this
conversion:

```python
    def downcast_torch_model(model: PModelTorch) -> PModelHugsTextClassifier:
        if isinstance(model, PModelHugsTextClassifier):
            return model
```

TODO: Decide whether it is ok to use a huggingface model here even if its
annotated with pytorch model even though this goes against intuitions from
object oriented programming.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass
from enum import IntEnum
import inspect
from inspect import Parameter as IParameter
from inspect import signature
from inspect import Signature
from itertools import chain
import logging
import os
import sys
import traceback
from typing import Any, Callable, DefaultDict, Dict, Iterable, List
from typing import Optional as TOptional
from typing import Tuple, Union

from truera.client.util.debug import Capture
from truera.client.util.debug import code_location_string
from truera.client.util.debug import render_exception
from truera.client.util.debug import retab
from truera.client.util.func import sig_eval_annotations
from truera.client.util.python_utils import Annotation
from truera.client.util.python_utils import caller_globals
from truera.client.util.python_utils import get_frameinfo
from truera.client.util.type_utils import fullname
from truera.client.util.types import Function
from truera.client.util.types import Given
from truera.client.util.types import Optional
from truera.client.util.types import Parameter

logger = logging.getLogger(name=__name__)

StateDict = Dict[Parameter, Any]

# Follow up work to move this to a set of things that will be available to write from the tutorial
# JIRA#MLNN-463
INGESTION_CUSTOM_KEYS = set(
    [
        'model',
        'get_model',  # autowrap
        'eval_model',  # autowrap
        'vocab',  # autowrap
        'unk_token_id',  # autowrap
        'pad_token_id',  # autowrap
        'special_tokens',  # autowrap
        'text_to_inputs',  # autowrap
        'text_to_token_ids',  # autowrap
        'text_to_spans',  # autowrap
        'n_embeddings',  # autowrap
        'n_tokens',  # autowrap
        'ds_from_source',  # autowrap
        'standardize_databatch',  # autowrap
        'token_embeddings_layer',  # NLPAttributionConfiguration
        'token_embeddings_anchor',  # NLPAttributionConfiguration
        'output_layer',  # NLPAttributionConfiguration
        'output_anchor',  # NLPAttributionConfiguration
        'n_output_neurons',  # NLPAttributionConfiguration
        'n_metrics_records',  # NLPAttributionConfiguration
        'ref_token',  # NLPAttributionConfiguration
        'resolution',  # NLPAttributionConfiguration
        'rebatch_size',  # NLPAttributionConfiguration
    ]
)

# TODO(piotrm): tracing of rule derivation
#
# How traces should look like. After calling set_model(pytorch_model=something, pad_token=None):
#   Trace for pytorch_model:
#     via "Input"
#   Trace for parameter pad_token:
#     via "Rule tokens_of_huggingface_tokenizer"
#     via "Rule huggingface_tokenizer of huggingface_model"
#     via "Rule huggingface_model of pytorch_model"
#   Trace for parameter mask_token:
#     "Alongside pad_token" (if mask_token is not an arg to set_model)
#     ... rest is the same as pad_token


class TracepointVerbosity(IntEnum):
    NONE = 0
    FAILED_ONLY = 1
    ALL = 2


class Tracepoint(object):
    """
    Class for noting various points in the derivation of an inferrable parameter.
    """

    # Keep track of traces produces as part of some inference procedure. This is
    # useful if inference fails which usually does not store intermediate
    # results. This dict will contain intermediate results and information about
    # failures. Is List of Traces (Traces is itself a List of Tracepoint)
    # because the same parameter may have been attempted to be derived multiple
    # ways.
    logs: Dict[Parameter,
               List[List[Tracepoint]]] = collections.defaultdict(list)

    verbosity = TracepointVerbosity.FAILED_ONLY  # If set, anything logged will be printed out.
    log_traces = True  # If set, anything logged will be added to tracelogs.

    def __init__(self, *args, **kwargs):
        # Frameinfo of where a Tracepoint object is created. This may or may not
        # be the most useful location to show to the user. Some types of
        # tracepoints have more useful frames to show.
        self.constructor_frame = inspect.stack()[2]

    def location_string(self, frame=None):
        frame = frame or self.constructor_frame
        return code_location_string(frame)

    def __repr__(self):
        return str(self)

    @classmethod
    def last_need(cls, trace, param=None):
        """
        Get the last tracepoint in the trace that is the Inferring type. If
        `param` is provided, looks for the last Inferring point that includes
        `param`.
        """
        infers = [
            t for t in trace if isinstance(t, Inferring) and
            (param in t.params if param is not None else True)
        ]
        if len(infers) == 0:
            raise RuntimeError(
                "Cannot determine current inferrence goal in trace:\n" +
                cls.str_trace(trace)
            )

        last_point = infers[-1]

        return last_point

    @classmethod
    def last_need_param(cls, trace):
        """
        Get the last parameter being inferred in the given trace. Assumes it is
        specified by Inferring tracepoint with a single param.
        """

        last_point = cls.last_need(trace)

        if len(last_point.params) != 1:
            raise RuntimeError(
                "Cannot determine current inferrence goal in trace:\n" +
                cls.str_trace(trace)
            )

        return last_point.params[0]

    @classmethod
    def log(cls, trace):
        param = cls.last_need_param(trace)

        if Tracepoint.log_traces:
            Tracepoint.logs[param].append(trace)

        if Tracepoint.verbosity > TracepointVerbosity.NONE:
            if (
                Tracepoint.verbosity == TracepointVerbosity.FAILED_ONLY and
                isinstance(trace[-1], Failed)
            ) or Tracepoint.verbosity == TracepointVerbosity.ALL:
                print(Tracepoint.str_trace_concluded(trace))

    @classmethod
    def reset_logs(cls):
        Tracepoint.logs = collections.defaultdict(list)

    @classmethod
    def str_trace_concluded(cls, trace, split="\n\t"):
        """
        Produce a readable representation of a concluded trace. In addition to
        tracepoints, also includes the parameter that is the last inference goal
        before conclusion.
        """

        point = trace[-1]
        start_str = ""
        if isinstance(point, RuleBacktrack):
            param = cls.last_need_param(trace)
            start_str = f"⭕ {param}" + split

        elif isinstance(point, Failed):
            param = cls.last_need_param(trace)
            start_str = f"❌ {param}" + split

        elif isinstance(point, Inferred):
            param = point.param
            val = point.val
            start_str = f"✅ {param}={str(val)[0:16]} (via inference)" + split

        elif isinstance(point, ViaInput):
            param = point.param
            val = point.val
            start_str = f"✅ {param}={str(val)[0:16]} (via input)" + split

        elif isinstance(point, Defaulted):
            param = point.param
            val = point.val
            start_str = f"✅ {param}={str(val)[0:16]} (by default)" + split

        elif isinstance(point, ViaStronger):
            stronger = point.stronger
            param = point.param
            val = point.val
            start_str = f"✅ {param}={str(val)[0:16]} (via stronger {stronger})" + split
        else:
            raise RuntimeError(
                "Given trace is not concluded:\n" + cls.str_trace(trace)
            )

        return start_str + cls.str_trace(trace, split=split)

    @classmethod
    def str_trace(cls, trace, split="\n"):  #split="←"):
        return split.join(map(str, trace))


@dataclass
class Inferring(Tracepoint):
    param: Parameter

    def __init__(self, params, frame_callsite=None):
        if isinstance(params, Iterable):
            self.params = list(params)
        else:
            self.params = [params]
        self.frame_callsite = frame_callsite  # If inferring parameter for a user-facing method, specify the frame describing that call so it can be printed.
        super().__init__()

    def __str__(self):
        if self.frame_callsite is not None:
            return f"{self.location_string(frame=self.frame_callsite)}: need {','.join(map(str, self.params))}"
        else:
            return f"need {','.join(map(str, self.params))}"

    def __repr__(self):
        return str(self)


class Inferred(Tracepoint):
    param: Parameter
    val: Any

    def __init__(self, param, val, rule_frame=None):
        self.param = param
        self.val = val
        self.rule_frame = rule_frame
        super().__init__()

    def __str__(self):
        return f"{self.location_string(frame=self.rule_frame)}: {self.param} was inferred ✅"

    def __repr__(self):
        return str(self)


@dataclass
class Defaulted(Tracepoint):
    param: Parameter
    val: Any

    def __init__(self, param, val, frame_default=None):
        self.param = param
        self.val = val

        self.frame_default = None  # Location where the default is provided.
        super().__init__()

    def __str__(self):
        return f"{self.location_string()}: {self.param} = was defaulted ✅"

    def __repr__(self):
        return str(self)


@dataclass
class Failed(Tracepoint):

    def __init__(self, frame_error=None):
        self.frame_error = frame_error  # Location of the error(exception) that caused the failure.
        super().__init__()

    def __str__(self):
        return f"{self.location_string(self.frame_error)}: failed ❌"

    def __repr__(self):
        return str(self)


@dataclass
class ViaRule(Tracepoint):
    """
    The use of a rule.
    """

    rule: Rule

    def __init__(self, rule, frame_rule=None):
        self.rule = rule
        self.frame_rule = frame_rule  # Frame of the rule being called.

        super().__init__()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.location_string(frame=self.frame_rule)}: using function {self.rule} ..."


@dataclass
class RuleBacktrack(Tracepoint):
    """
    The use of a rule.
    """

    rule: Rule
    exception: Backtrack

    def __init__(self, rule, exception, frame_backtrack=None):
        self.rule = rule
        self.exception = exception
        self.frame_backtrack = frame_backtrack  # Location of where the backtrack exception is raised.
        super().__init__()

    def __repr__(self):
        return str(self)

    def __str__(self):
        msg = self.exception.msg.rstrip()
        return f"{self.location_string(frame=self.frame_backtrack)}: function {self.rule} backtracked because '{msg}' ⭕"


@dataclass
class ViaStronger(Tracepoint):
    """
    The use of a parameter that is stronger than the one asked for. For example,
    PModelTorch is "stronger" than PModel. If a rule or dispatch option calls
    for PModel, it is appropriate to give it PModelTorch instead as PModelTorch
    is a subclass of PModel.
    """

    stronger: Parameter

    def __init__(self, param, stronger, val, frame_definition=None):
        self.param = param
        self.stronger = stronger
        self.val = val
        self.frame_definition = frame_definition  # Location where the stronger is defined.
        super().__init__()

    def __str__(self):
        return f"{self.location_string()}: via value of subtype: {self.stronger}✅"

    def __repr__(self):
        return str(self)


@dataclass
class ViaInput(Tracepoint):
    """
    The use of an explicit method input, that is, not an inference.
    """

    param: Parameter

    def __init__(self, param, val, frame_callsite=None):
        self.param = param
        self.val = val
        self.frame_callsite = frame_callsite  # Location that provides the input, presumably a callsite.
        super().__init__()

    def __str__(self):
        return f"{self.location_string(frame=self.frame_callsite)}: {self.param} was input ✅"

    def __repr__(self):
        return self.__str__()


class State(collections.abc.Iterable):
    """
    A state assigns a value to parameters. Also includes a "trace" for each
    value indicating how it was derived.
    """

    def __init__(self, values: StateDict):
        self.values: StateDict = {}
        self.trace: DefaultDict[
            Parameter, List[Tracepoint]] = collections.defaultdict(list)

        for k, v in values.items():
            self.set(k, v, trace=[])

    def bind_relevant_and_call(self, func):
        """
        Call the given func with values coming from self. Does not do any
        inference as values are already assumed to be present.
        """

        sig = signature(func)

        kwargs = dict()

        for name, param in sig.parameters.items():
            if isinstance(param.annotation, Parameter):
                assert param.annotation in self.values, f"state does not have a value for parameter {name}: {param.annotation}"
                kwargs[name] = self.get(param.annotation)
            elif isinstance(param.annotation, Given
                           ) and isinstance(param.annotation.typ, Parameter):
                assert param.annotation.typ in self.values, f"state does not have a value for given parameter {name}: {param.annotation}"
                kwargs[name] = self.get(param.annotation.typ)
            else:
                values = [v for k, v in self.values.items() if k.name == name]
                assert len(
                    values
                ) <= 1, f"had none or more than 1 possible binding for non-parameter input named {name}"

                if len(values) == 1:
                    kwargs[name] = values[0]
                else:
                    assert param.default is not IParameter.empty, f"state has no value for non-default argument named {name}"

        binding = sig.bind(**kwargs)

        return func(*binding.args, **binding.kwargs)

    def update(self, state: 'State'):
        """
        Update self with the parameters/traces in the given `state`.
        """

        for k, v in state.values.items():
            self._set(k, v, trace=state.trace[k])

        return self

    def delete(self, var: 'Parameter') -> None:
        assert var in self.values, f"Parameter {var} not in state to delete."

        self.values.__delitem__(var)

    def _set(
        self, var: 'Parameter', val: Any, trace: TOptional[List[Tracepoint]]
    ):

        self.values[var] = val
        self.trace[var] = trace

    def set(
        self, var: 'Parameter', val: Any, trace: TOptional[List[Tracepoint]]
    ):
        """
        Set the value `val` for the given parameter `val`. Set its trace to `trace`.
        """

        trace = trace or []

        newval = True

        if var in self:
            newval = False
            if self.get(var) != val:
                raise Backtrack(
                    f"attempting to override parameter {var}={self.get(var)} with value {val} ."
                )

        self._set(var, val, trace)

    def get(self, var: Union['Parameter', str]) -> Any:
        """
        Get the value of the given parameter `var`.
        """
        if isinstance(var, Parameter):
            return self.values.get(var)
        elif isinstance(var, str):
            matching = list(filter(lambda v: v.name == var, self.values))
            if len(matching) == 0:
                return None
            elif len(matching) == 1:
                return self.values.get(matching[0])
            else:
                results = set(self.values.get(m) for m in matching)
                if len(results) == 1:
                    return results.pop()
                raise ValueError(f"More than one parameter matches name {var}.")
        else:
            raise TypeError(
                f"Wrong key type {type(var)}. Parameter or string required."
            )

    def get_trace(self, var: Union['Parameter', str]) -> Any:
        """
        Get the value of the given parameter `var`.
        """
        if isinstance(var, Parameter):
            return self.trace.get(var)
        elif isinstance(var, str):
            matching = list(filter(lambda v: v.name == var, self.values))
            if len(matching) == 0:
                return None
            elif len(matching) == 1:
                return self.trace.get(matching[0])
            else:
                raise ValueError(f"More than one parameter matches name {var}.")
        else:
            raise TypeError(
                f"Wrong key type {type(var)}. Parameter or string required."
            )

    def get_parameter(self, var: str) -> Any:
        """
        Get the parameter with the given name in state if one exists.
        """

        matching = list(filter(lambda v: v.name == var, self.values))
        if len(matching) == 0:
            return None
        elif len(matching) == 1:
            return matching[0]
        else:
            raise ValueError(f"More than one parameter matches name {var}.")

    def __contains__(self, val: Parameter) -> bool:
        return val in self.values

    def __iter__(self):
        return iter(self.values)

    @staticmethod
    def is_stronger(a: Parameter, b: Parameter) -> bool:
        """
        Determine whether `a` is "stronger" than `b` in that `a` can be used in
        places where `b` is expected. This is just a subclass check along with a
        name comparison. Not using the LogicalType system for name comparison,
        could not figure out how to do that.
        """

        return a.name == b.name and issubclass(a, b)

    def get_stronger(self: 'State', var: Parameter) -> Iterable[Any]:
        """
        Get variables that imply the given parameter `var`, other than `var`
        itself.
        """

        for stronger in self:
            if var == stronger:  # skip `var` itself if it is in state.
                continue

            if State.is_stronger(stronger, var):
                yield stronger

    @staticmethod
    def _val_summary(val: Any, max_len: int = 32) -> str:
        str_val = str(val)

        if "\n" in str_val:
            lines = str_val.split("\n")

            str_val = lines[0]
            while str_val == "" and len(lines) > 1:
                lines = lines[1:]
                str_val = lines[0]

            if len(lines) > 1:
                str_val += "..."

        if len(str_val) > max_len:
            str_val = str_val[0:max_len - 2] + "..."

        return str_val

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        ret = "\n"
        for var, val in self.values.items():
            str_val = self._val_summary(val, max_len=64)

            typename = fullname(type(val))

            if (not typename.startswith("builtins")
               ) or ("function" in typename):
                if hasattr(val, "__name__") and val.__name__ is not None:
                    str_val += f"\n\t\t__name__ = {self._val_summary(val.__name__, max_len=64)}"
                if hasattr(val, "__doc__") and val.__doc__ is not None:
                    str_val += f"\n\t\t__doc__ = {self._val_summary(val.__doc__, max_len=64)}"

            ret += f"\t{var}: {self._val_summary(typename, max_len=32)} = {str_val}\n"  # via {self.trace[var]}\n"
        return ret

    # TODO: method might not be used any more
    def is_valid(self, var: 'Parameter') -> bool:
        """
        Determine whether that given parameter `var` is satisfied by this state,
        this is if it is explicitly set or is otherwise implied by something
        that is.
        """

        if var in self:
            return True

        if any(State.is_stronger(stronger, var) for stronger in self):
            return True

        return False

    def copy(self):
        st = State({}).update(self)
        return st


class Rule:
    """
    An inference rule derived from a python function that takes in variable
    assignment (state) of some subset of variables (from method signature) that
    satisfy the rule's antecedent and produces an assignment for some other
    variables (from signature's return) that satisfy the rule's consequent.

    Python functions for defining these rules can only have VarStatement
    annotations on inputs and outputs, or optionally no or non-Statement
    annotations which are interpreted as VarNotNone with or without VarTyped.
    """

    imp: Callable  # "imp" for "implementation"
    sig: inspect.Signature
    sig_annot: inspect.Signature

    name: str  # rule name
    doc: str

    consequents: Tuple[Parameter]
    antecedents: Tuple[Parameter]

    consequents_annot: Tuple[Annotation]
    antecedents_annot: Tuple[Annotation]

    def __str__(self):
        return f"{self.name}: {','.join(map(str, self.antecedents))} -> {','.join(map(str, self.consequents))}"

    __repr__ = __str__

    def __init__(
        self,
        imp,
        sig: inspect.Signature = None,
        sig_annot: inspect.Signature = None,
        globals={}
    ):
        self.name = imp.__name__

        sig_annot = sig_annot or inspect.signature(imp)
        sig = sig or sig_eval_annotations(sig_annot, globals)

        self.imp = imp
        self.sig_annot = sig_annot
        self.sig = sig
        self.doc = imp.__doc__

        self.antecedents = tuple(
            Rule._param_of_parameter(p) for p in self.sig.parameters.values()
        )
        self.antecedents_annot = tuple(
            Rule._param_of_parameter(p)
            for p in self.sig_annot.parameters.values()
        )

        self.consequents = Rule._params_of_annotation(
            self.sig.return_annotation, name="<return>"
        )
        self.consequents_annot = Rule._params_of_annotation(
            self.sig_annot.return_annotation, name="<return>"
        )

    def eval(self, state: State, trace) -> State:
        """
        Evaluate rule in the given state context, setting its consquents in the returned state.
        """
        missing_antecedents = []
        for param in self.antecedents:
            if param not in state:
                missing_antecedents.append(param)

        if len(missing_antecedents):
            raise MissingAntecedentException(
                f"cannot evaluate function {self} without {missing_antecedents}",
                missing_antecedents=missing_antecedents,
                consequents=self.consequents,
            )
        # TODO: fix ordering issues
        kwargs = {
            param.name: state.get(self.antecedents[i])
            for i, param in enumerate(self.sig.parameters.values())
        }

        bindings = self.sig.bind(**kwargs)

        with Capture.for_term() as cap:
            rets = self.imp(*bindings.args, **bindings.kwargs)
        # get the frame of the call here

        #cap.display(prefix=Tracepoint.str_trace(trace))
        #print(Tracepoint.str_trace(trace))

        state = state.copy()

        if len(self.consequents) == 1:
            # Single consequent implementations are not expected to return a
            # tuple and instead just produce their single consequent
            # un-containered.
            rets_as_list = [rets]
        else:
            rets_as_list = rets

        for ret, con in zip(rets_as_list, self.consequents):
            state.set(
                con,
                ret,
                trace=trace + [Inferred(con, ret, rule_frame=self.imp)]
            )  # + [ViaRule(self)])

        return state

    # Several methods for converting a python function to a rule:

    @staticmethod
    def _param_of_parameter(param: inspect.Parameter) -> Parameter:
        if isinstance(param.annotation, str):
            return param.annotation

        if isinstance(param.annotation, Parameter):
            return param.annotation
        else:
            return Rule._param_of_annotation(param.annotation, name=param.name)

    @staticmethod
    def _param_of_annotation(annot, name) -> Parameter:
        if annot is inspect.Parameter.empty:
            return Parameter(name=name, typ=Any, desc="")
        else:
            if isinstance(annot, Parameter):
                return annot
            else:
                return Parameter(name=name, typ=annot, desc="")

    @staticmethod
    def _params_of_annotation(annot, name) -> Tuple[Parameter]:
        if isinstance(annot, Parameter):
            return tuple([annot])

        params = []

        if isinstance(annot, Iterable):
            for a in annot:
                params.append(Rule._param_of_annotation(a, name=name))
        else:
            params.append(Rule._param_of_annotation(annot, name=name))

        return tuple(params)


class MissingAntecedentException(Exception):

    def __init__(
        self, msg: str, missing_antecedents: Parameter, consequents: Parameter
    ):
        self.msg = msg
        self.missing_antecedents = missing_antecedents
        self.consequents = consequents


class InferException(Exception):
    """
    Base class for exceptions relating to rule-based inferences.
    """

    def __init__(
        self,
        msg: str,
        trace: Optional[List[str]] = None,
        infer_param: Parameter = None,
        rest_params: List[Parameter] = None
    ):
        self.msg = msg
        self.infer_param = infer_param
        self.rest_params = rest_params

        # TODO(piotrm): trace work ongoing
        self.trace = trace or []

    def __str__(self):
        return "\n".join(map(str, self.trace)) + "\n" + self.msg

    def pileon(self, part: str) -> InferException:
        """
        Create a copy of this exception with an additional message `part` in its trace.
        """

        return InferException(self.msg, [part] + self.trace)


class NoBacktrack(InferException):
    """
    Throw this in a rule to prevent further rule evaluation.
    """
    pass


class Backtrack(InferException):
    """
    Throw this to indicate that this rule does not apply or failed but that it
    is ok to ignore this and continue with other rules that might apply.
    """
    pass


class Rules:
    """
    A collection of inference rules along with methods for performing the inference.
    """

    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule):
        """
        Add the given `rule` to tracked collection.
        """
        self.rules.append(rule)

    def register_rules(
        self, cls: type
    ):  # TODO(piotrm): is there a better annotation for cls?
        """
        Adds all rules found in the given class `cls` to the `self.rules`
        collection. This includes all methods in that class that have a
        Parameter type in their return annotation (or an iterable of Parameter).
        """

        globals = caller_globals()

        for k in cls.__dict__.keys():
            # NOTE(piotrm): dir(cls) does NOT return contents in order of definition while __dict__ does.
            v = getattr(cls, k)
            if isinstance(v, Callable):
                try:
                    sig_annot = inspect.signature(v)
                    sig = sig_eval_annotations(sig_annot, globals)

                    ret_annot = sig.return_annotation

                    if ret_annot is not inspect.Parameter.empty:
                        if isinstance(ret_annot, Parameter) or (
                            isinstance(ret_annot, Iterable) and
                            all(isinstance(t, Parameter) for t in ret_annot)
                        ):
                            # TODO(piotrm): type printing adjustments work in progress
                            # v.__signature__ = sig

                            self.add_rule(Rule(v))

                except ValueError:
                    pass

        return cls

    def get_rules_for(self, var: Parameter) -> Iterable[Rule]:
        """
        Get all rules that have `var` in the consequents or something stronger than `var`.
        """

        for rule in self.rules:
            if any(
                State.is_stronger(consequent, var)
                for consequent in rule.consequents
            ):
                yield rule
        return

    def eval_rule(
        self,
        state: State,
        rule: Rule,
        sig: Signature,
        backtracked_params: set,
        param_cache: set,
        trace=[]
    ) -> Iterable[State]:
        """
        Evaluate the given `rule` on the given `state`, producing some number of
        resulting states.

        TODO(piotrm): `trace` work ongoing.
        """

        state = state.copy()

        # Callect all states satisfying antecedents here.
        branches = iter([])

        #if all(var in state for var in rule.antecedents):
        # Have all the rule antecedants in the state. Add existing state to
        # branches as is.
        #    branches = chain(branches, [state])

        #else:

        new_trace = trace + [
            ViaRule(rule, frame_rule=rule.imp),
            Inferring(list(rule.antecedents), frame_callsite=rule.imp)
        ]

        # Otherwise we need to infer some antecedents. There may be multiple
        # ways of doing so.
        branches = chain(
            branches,
            self.get(
                state=state,
                need=list(rule.antecedents),
                optional=[],
                trace=new_trace,
                sig=sig,
                backtracked_params=backtracked_params
            )
        )
        try:
            # Evaluate the rule for each antecedents branch.
            for branch in branches:
                #sats = []
                #for var in rule.antecedents:
                #    sats.append(branch.get_trace(var)[-1])
                yield rule.eval(branch, trace=new_trace
                                # + sats
                               )
        except Backtrack as e:
            if e.infer_param and e.infer_param in rule.antecedents:
                # Could not infer an antecedent, raise as MissingAntecedentException instead
                raise MissingAntecedentException(
                    f"Failed to infer {e.infer_param}",
                    missing_antecedents=[e.infer_param],
                    consequents=rule.consequents
                )
            else:
                raise e

    @staticmethod
    def _getparameter(annot):
        if isinstance(annot, Parameter):
            return annot
        elif isinstance(annot, Given) or isinstance(annot, Optional):
            return Rules._getparameter(annot.typ)
        else:
            return None

    def bind(
        self, func: Function, state: State, args: Tuple[Any], kwargs: Dict,
        trace
    ) -> Iterable[inspect.BoundArguments]:
        """
        Produce bound arguments for the given `func` from `args` and `kwargs` or from
        things derivable from them.

        TODO(piotrm): `trace` work ongoing.
        """

        # Copy for popping.
        args: List = list(args)

        # Copy to not clobber the original.
        original_state = state
        state = state.copy()

        # Track parameters that will need to be inferred.
        need = []

        # Track parameters that will be inferred but need not to.
        may_use = []

        sig = inspect.signature(func)

        bindings = {}

        for name, param in sig.parameters.items():
            annot = param.annotation

            annot_param = Rules._getparameter(annot)

            if annot_param is None:
                # If a parameter is not annotated as `Parameter`, treat it like in standard python.
                if param.kind is IParameter.KEYWORD_ONLY:
                    assert name in kwargs, f"Non-parameter keyword argument {name} not provided."
                    bindings[name] = kwargs[name]
                else:
                    assert len(
                        args
                    ) > 0, f"Non-parameter positional argument {name} not provided."
                    bindings[name] = args.pop(0)

                continue

            # Otherewise `annot` is `Parameter`, `Given(Parameter)`, or
            # `Optional(Parameter)`. Check if value is provided and that value
            # is not None.
            if param.kind is IParameter.KEYWORD_ONLY:
                if name in kwargs and kwargs[name] is not None:
                    state.set(
                        annot_param,
                        kwargs[name],
                        trace=[
                            Inferring(annot_param, frame_callsite=func),
                            ViaInput(
                                param=annot_param,
                                val=kwargs[name],
                                frame_callsite=get_frameinfo(6)
                            )
                        ]
                    )
                    # Note(piotrm): Stack depth 6 should be the user's call of
                    # one of the quick.py methods.

            else:
                if len(args) > 0:
                    val = args.pop(0)
                    if val is not None:
                        state.set(
                            annot_param,
                            val,
                            trace=[
                                Inferring(annot_param, frame_callsite=func),
                                ViaInput(
                                    param=annot_param,
                                    val=val,
                                    frame_callsite=get_frameinfo(6)
                                )
                            ]
                        )

            # If the above failed to set a value for annot in state, make note
            # of it as needed to infer.
            if not annot_param in state:
                if isinstance(annot, Optional):
                    # Mark optional parameters as "may use" so failure to derive
                    # them is not treated as error.
                    may_use.append(annot_param)

                elif isinstance(annot, Given):
                    # Should not happen, dispatch should not be calling us if a Given-annotated parameter
                    # was not provided by user.
                    raise RuntimeError(
                        f"Was not given a value for a user-provided parameter: {annot}."
                    )
                else:  # isinstance(annot, Parameter):

                    # Things not marked with Optional must be derived.
                    need.append(annot_param)

        trace = trace + [Inferring(need + may_use, frame_callsite=func)]

        # Enumarate the ways in which to infer `need` from parameters set in
        # `state`. For each create the BoundArguments object which can be used
        # to call the method of interest.
        backtracked_params = set()
        try:
            for state in self.get(
                state=state,
                need=need + may_use,
                optional=may_use,
                trace=trace,
                sig=sig,
                backtracked_params=backtracked_params
            ):
                missing_sig_params = set()
                for name, param in sig.parameters.items():
                    annot = param.annotation
                    annot_param = Rules._getparameter(annot)

                    if annot_param is None:
                        # Should already be in bindings from above.
                        continue
                    elif annot_param in state:
                        bindings[name] = state.get(annot_param)
                    else:
                        missing_sig_params.add(annot_param)

                assert len(
                    missing_sig_params
                ) == 0, f"Do not have value for {missing_sig_params} in parameters state"

                yield state, sig.bind(**bindings)
        except Backtrack as e:
            Tracepoint.log(e.trace)
        except AssertionError:
            pass
        finally:
            if len(backtracked_params) > 0:
                Parameter.display_help_doc(
                    backtracked_params,
                    state=original_state,
                    method_name=func.__overload_name__
                )

    def get(
        self,
        state: State,
        need: List[Parameter],
        optional: List[Parameter],
        trace: List[Tracepoint],
        sig: Signature = None,
        backtracked_params: set = None,
        param_cache: set = None
    ) -> Iterable[State]:
        """
        Starting with `state`, use the registered rules to try to get values for
        everything in `need` list. This may be done in multiple ways hence
        produced is some number of resulting states that each should have values
        for everything in `need`. If a parameter in `need` cannot be derived,
        will not yield a state unless that parameter is also in the `optional`
        list in which case a state will be yielded with an assignment of None to
        that parameter.

        TODO(piotrm): `trace` work ongoing.
        """

        tab = "  " * len(trace)

        # TODO(piotrm): do not evaluate all rules before recurring, evaluate one at a time

        assert isinstance(need, List), f"`need` was not a list but {type(need)}"

        if len(need) == 0:
            # Nothing needed. Return state as is.
            yield state
            return

        # Will focus on the first need first, then the rest recursively.
        first, rest = need[0], need[1:]

        # Skip first if previously seen or else add to param_cache
        if param_cache is None:
            param_cache = set()

        if first in param_cache:
            for state in self.get(
                state,
                need=rest,
                optional=optional,
                trace=trace,
                sig=sig,
                backtracked_params=backtracked_params,
                param_cache=param_cache
            ):
                yield state
        else:
            param_cache.add(first)

        last_need = Tracepoint.last_need(trace, param=first)
        assert first in last_need.params, f"First {first} was not part of the last inference goal {last_need}."
        trace = trace + [
            Inferring(first, frame_callsite=last_need.frame_callsite)
        ]

        tab = tab + f"deriving {first}: "

        if first.name in INGESTION_CUSTOM_KEYS and "TRU_QUICK_NN_INFERENCE_FLAG" in os.environ and os.environ[
            "TRU_QUICK_NN_INFERENCE_FLAG"] == "0":
            return InferException(
                f"Inference is disabled for parameter `{first}`. "
                f"Please supply this as a parameter to the method."
            )

        # Tracks if first is missing a backtracked antecedent. This is set later.
        missed_backtrack_antecedent = False

        # Iterator to collect a set of states that satisfy first. Will be using
        # itertools.chain to add options to this iterator.
        first_branches = iter([])

        logger.debug(tab + f"working on deriving {first}")

        if first in state:
            # First already satisfied.
            Tracepoint.log(trace + [state.get_trace(first)[-1]])  # TODO: better

            logger.debug(tab + "already satisfied")

            state_copy = state.copy()

            first_branches = chain(first_branches, [(state_copy, trace)])

            # NOTE(piotrm -> corey): need adjustments here or in state.get in case
            # the same param name appears in state labeling different parameters.
            """
            elif isinstance(state.get(first.name), first):
                # Check if first is subclassing/stronger than an existing parameter in state.
                # First already satisfied but is in a more specific parameter.

                logger.debug(
                    tab +
                    f"{first} is stronger and compatible with {state.get(first.name)}"
                )

                state_copy = state.copy()
                # TODO: Determine whether we want to keep weaker or delete:
                # weaker_param = state_copy.get_parameter(first.name)
                # state_copy.delete(weaker_param)
                state_copy.set(first, state.get(first.name), trace=trace)

                first_branches = chain(first_branches, [(state_copy, trace)])
            """
        else:
            # NOTE(piotrm->corey): This section makes use of parameters that
            # have the same name but different types. May not be needed if we
            # decide not to do "inference via stronger" automatically. Can still
            # do it explicitly be defining rules.

            # NOTE(piotrm): disabling this section for now. See discussion
            # around "same name, different parameter" in notes near here.

            # Note due to python weirdness, need to pass in the used variables
            # to iterator instead of assuming their value will be captured in
            # closure.
            """
            def iter_stronger_branches(first, state, trace, tab):
                logger.debug(tab + "via stronger...")

                for stronger in state.get_stronger(first):
                    logger.debug(tab + f"via stronger {stronger}")

                    # Satisfy first via a stronger parameter.

                    # `first` is not explicitly satisfied but is implied by a
                    # parameter that is explicitly satisfied. Make a branch for each
                    # of those stronger parameters and in each branch assign the
                    # stronger parameter's value to first.

                    new_state = state.copy()
                    new_trace = trace + [
                        ViaStronger(
                            first, stronger, val=new_state.get(stronger)
                        )
                    ]

                    new_state.set(
                        first, new_state.get(stronger), trace=new_trace
                    )
                    assert first in new_state
                    logger.debug(tab + f"got {first} via {stronger}")

                    Tracepoint.log(new_trace)

                    yield (new_state, new_trace)

                logger.debug(tab + "no more stronger")

            first_branches = chain(
                first_branches,
                iter_stronger_branches(first, state, trace, tab)
            )
            """

            # Try to derive first using rules.
            # Create iterator for branches that use a rule so we don't
            # evaluate any of the rules until needed.
            def iter_rules_branches(first, state, trace, tab):
                logger.debug(tab + "via rules ...")

                for rule in self.get_rules_for(first):
                    # Get every rule that may be used to satisfy first.

                    if ViaRule(rule) in trace:
                        logger.debug(
                            tab + f"skipping rule {rule} since already in trace"
                        )
                        # Do not get into derivation loops which can easily occur if
                        # parameter implication has loops.
                        continue

                    # For each antecedent, check if its name exists in the
                    # state. If it is, ensure the type of the value in the state
                    # is compatible with the type of the antecedent. If it is
                    # not, skip the rule. TODO: Determine whether this should
                    # always be done. Can skip some rules that should not be
                    # used to due framework incompatability but may be a problem
                    # in the future.
                    skip_rule = False

                    for antecedent in rule.antecedents:
                        # NOTE(piotrm -> corey): state.get will fail if there is
                        # more than one parameter with the same name. Perhaps
                        # the goal of this block is to make sure there is never
                        # two params with the same name in state to begin with ?
                        existing_state_val = state.get(antecedent.name)
                        if existing_state_val is not None and not isinstance(
                            existing_state_val, antecedent
                        ):
                            logger.debug(
                                tab +
                                f"skipping rule {rule} since incompatible value for {antecedent.name} in state"
                            )
                            skip_rule = True
                            break
                    if skip_rule:
                        continue

                    # NOTE(piotrm -> corey): if huggingface model and model have
                    # the same parameter name, the following chain will fail.
                    # For now I change the names but if we decide to allow same
                    # name parameters in the future, will have to revisit.

                    # 1. set_model called with a torch model that includes inside it a huggingface model.
                    # 2. Need to derive tokenizer:
                    #       3. try to derive huggingface_model_name, this requires huggingface model
                    #           4. derive huggingface model from pytorch model, success
                    #           5. now can get huggingface_model_name from huggingface model
                    #       6. now can get tokenizer via huggingface_model_name

                    logger.debug(tab + f"via rule {rule}")
                    try:
                        for branch in self.eval_rule(
                            state,
                            rule,
                            sig=sig,
                            backtracked_params=backtracked_params,
                            trace=trace,
                            param_cache=param_cache
                        ):
                            # Evaluate each rule.

                            assert first in branch, f"rule {rule} evaluation did not satisfy first {first}"

                            new_trace = trace + [
                                Inferred(
                                    first,
                                    branch.get(first),
                                    rule_frame=rule.imp
                                )
                            ]

                            Tracepoint.log(new_trace)

                            logger.debug(tab + f"got {first} via rule {rule}")

                            yield (branch, new_trace)

                    except Backtrack as e:
                        tb = sys.exc_info()[2]
                        new_trace = trace + [
                            RuleBacktrack(rule, e, frame_backtrack=tb)
                        ]
                        Tracepoint.log(new_trace)

                        logger.debug(
                            tab +
                            f"Rule {rule} wants to backtrack:\n{render_exception(e)}"
                        )

                        continue  # continue with next rule

                    except InferException as e:
                        # Re-raise the rule's exception but add onto its trace
                        # an indicator of why the failed rule was used.
                        raise e.pileon(f"Inferring {first} via {rule} ...")

                    except MissingAntecedentException as e:
                        # If eval_rule failed because of missing antecedents that have been reported already,
                        # don't report the rule's consequent as missing to the user since it will be inferred
                        # if the missing antecedents are provided.
                        if all(
                            antecedent in backtracked_params
                            for antecedent in e.missing_antecedents
                        ):
                            nonlocal missed_backtrack_antecedent
                            missed_backtrack_antecedent = True
                        continue  # continue with next rule

                    except Exception as e:
                        raise InferException(
                            f"Rule {rule} had unexpected error:\n{retab(render_exception(e))}"
                        )

                logger.debug(tab + "no more rules")

            first_branches = chain(
                first_branches, iter_rules_branches(first, state, trace, tab)
            )

        yielded_something = False

        logger.debug(tab + f"enumerating branches for {first}")

        def satisfy_params(
            params: Iterable[Parameter], branch: State, trace: List[Tracepoint]
        ):
            """
            Iterates through params and tries to satisfy each one sequentially using the given branch state and inference rules.
            If a param cannot be satisfied, a Backtrack exception will be raised and caught. 
            Backtracked parameters are added to the backtracked_params set and logged.
            """
            if len(params) == 0:
                logger.debug(
                    tab + "nothing else to infer, yielding current branch"
                )
                yield branch
                return
            while len(params):
                try:
                    for state in self.get(
                        state=branch,
                        need=params,
                        optional=optional,
                        trace=trace,
                        sig=sig,
                        backtracked_params=backtracked_params,
                        param_cache=param_cache
                    ):
                        yield state
                except Backtrack as e:
                    if e.infer_param:
                        Tracepoint.log(e.trace)
                        backtracked_params.add(e.infer_param)
                    params = e.rest_params[1:]

        # Try to satisfy the rest of the parameters for each of the ways in
        # which first can be satisfied.
        for (branch, trace) in first_branches:
            assert first in branch, f"first {first} was not yet satisfied when considering rest {rest}"

            trace2 = trace  # + [Inferred(first, None)]

            logger.debug(tab + f"current branch={branch}")

            for state in satisfy_params(rest, branch, trace2):
                yielded_something = True
                yield state

        if not yielded_something:
            if first in optional:
                # `first` could not be derived but it is optional so assign None
                # to it and continue with rest. Note that this will not trigger
                # if there was a valid inference for `first`. That is, the None
                # value is not considered a branch but rather an alterative to a
                # case where there are no branches for it.

                print(
                    f"WARNING: optional parameter {first} could not be inferred. Will use default value `None`."
                )

                branch = state.copy()
                branch.set(first, None, trace=trace + [Defaulted(first, None)])
                trace2 = trace + [Defaulted(first, None)]
                # TODO: get optional values from signature
                for state in satisfy_params(rest, branch, trace2):
                    yielded_something = True
                    yield state

                logger.debug(
                    tab + "nothing else to infer, yielding current branch"
                )
                yielded_something = True
                yield branch

            else:
                # Create a message indicating a derivation failure if the above
                # yielded nothing for `first` and `first` was not optional.
                message = f"No way to infer {first}."
                exception_param = None
                # TODO: this could introduce bugs if the names of signature arguments do not match parameter names
                if not missed_backtrack_antecedent and sig and first.name in sig.parameters and first is Parameter.base_param(
                    sig.parameters[first.name].annotation
                ):
                    exception_param = first

                raise Backtrack(
                    message,
                    trace=trace + [Failed(frame_error=get_frameinfo(1))],
                    infer_param=exception_param,
                    rest_params=rest
                )
                # Stack depth 1 should refer to the call site of Failed constructor on the prior line.
                # TODO: Is there a better user-readable location to point the user to if this happens?
