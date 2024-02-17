"""
Types and type constructors, related utilities.

- Owners: piotrm

## New types and Replacements of existing types

Some existing types do not operate in a manner we would like to so they are
provided here with alternate definitions. Note that the benefit of these types
is that isinstance/issubclass work for them but if you only need to use
type-hints without instance/subclass checking, you should use existing typing.*
types. These are:

- Logical types:
    - Optional(t) - Like typing.Optional but isinstance(None, Optional(int)) ==
      True. Equivalent to Union(Literal(None), t).
    - Union(t1, ..., tn) - Like typing.Union but isinstance and issubclass work.
    - Intersection(t1, ..., tn) - Dual of Union, isinstance works as expected.
    - Unit() - Like typing.Never. A type that always fails its isinstance check.
    - Not(t) - A type matching whatever t does not. *** DO NOT USE ***
    - Any - Matches everything.
    - Never - Matches nothing.
    - NoneType - Matches only the value "None".
    - Literal(v) - Matches only instances that have value `v`.

- Function(signature) - like Callable but is a type. Note caveats below.
- TypeMatching(pattern) - makes subtyping checks based on type names that match
  the given pattern. Not caveats below.

Note that in all of these cases, the type parameters are specified as arguments
to constructors as opposed to generic variables which are the cause of their
undesired functionality. That is, we use `Optional(int)` as opposed to
`Optional[int]`.

## Caveats

- No actual static type checking is done using these types. They are purely for
  runtime checking, for type-based dispatches like overloading, and
  documentation.
- The use of negation (Not type constructor) significantly degrades
  instance/subclass check performance so it may be disabled.
- Function and TypeMatching types have naive instance/subclass checks. Function
  types are all equivalent, and TypeMatching is equivalent to any TypeMatching
  with the same regular expression pattern. The signature field of Function is
  presently unused but could see it used for type checking in the future.
- Type constructors that take in types as input need their input types to use
  `type` as metaclass. So things like Optional(A) where A is a ABC (different
  metaclass) will not work and will result in an error that contains "metaclass
  conflict".

## Tests

- Unit Tests
    - `python/truera/test/unit_tests/client/test_types.py`
    - `make test/unit_tests/client/test_types`

"""

from __future__ import annotations

from dataclasses import dataclass
from inspect import cleandoc
from inspect import getsource
from inspect import Signature
import re
from typing import Any as TAny
from typing import Callable, Iterable
from typing import Optional as TOptional
from typing import Set, Tuple
from typing import Union as TUnion

import sympy
from sympy.logic import boolalg as B

from truera.client.util.annotations import eval_type
from truera.client.util.annotations import render_annotation
from truera.client.util.container_utils import Lens
from truera.client.util.python_utils import Annotation
from truera.client.util.python_utils import caller_globals
from truera.client.util.type_utils import AutoNone
from truera.client.util.type_utils import fullname
from truera.client.util.type_utils import is_typelike
from truera.client.util.type_utils import shortname
from truera.client.util.type_utils import typelike_bases

# logger = logging.getLogger(name=__name__)


class TypeMatching(type):  # not LogicalType
    """
    A Type whose membership is determined by a regular expression on type/class
    names. This type does not interact with the logical types below so should
    not be used with them.
    """

    def __new__(cls, pattern):
        # This is needed for Type subtypes.

        return super().__new__(cls, f"/{pattern}/", (), {})

    def __init__(
        self,
        pattern: str,
    ):
        self.pattern = re.compile(pattern)

    def __instancecheck__(cls, obj: TAny):
        fname = fullname(type(obj))
        return cls.pattern.fullmatch(fname) is not None

    @staticmethod
    def _mro_cls(cls):
        if cls is type:
            return cls.mro(cls)
        else:
            return cls.mro()

    def __subclasscheck__(cls, cls2: type):
        # Subclass check needs to find a class with a matching name in any of
        # the bases which can be retrieved from the method resolution order
        # list. TODO: maybe there are more clear ways of getting base/parent
        # types?
        return any(
            cls.pattern.fullmatch(fullname(c)) is not None
            for c in TypeMatching._mro_cls(cls2)
        )


class LogicalType(type):
    """
    Base class of all the following types that makes use of logical formulas for
    checking subtype/subclass relation. These replicate some of `typing.*` types
    except isinstance and issubclass works here. These types may be removed once
    `typing.*` (or if) supports that functionality in the future. instance
    checks are implemented adhoc using python whereas subclass checking is done
    symbolically using sympy. Note, however, that special type aliases like
    those in typing.* such as Sequence will not work with subclass checks as
    those required evaluating special methods for determining type
    relationships.
    """

    subtype_relations = set([])
    subtype_relations_form = B.BooleanFalse()

    negation_enabled = False

    @staticmethod
    def symbol_function(t: Function = None, signature: Signature = None) -> str:
        # Presently all functions/callables are equivalent. See class Function.
        return "instance:function"

    @staticmethod
    def symbol_type(t: type) -> str:
        if isinstance(
            t, Function
        ) or (not isinstance(t, type) and isinstance(t, Function)):
            return LogicalType.symbol_function(t)

        return f"type:{fullname(t)}"

    @staticmethod
    def symbol_literal(obj: TAny) -> str:
        return f"instance:literal:{str(obj)}"

    @staticmethod
    def symbol_parameter(name: str, typ: type) -> str:
        # From the perspective of logical types, parameters are viewed as their
        # enclosed type. The name checking is done outside of the type system.

        return LogicalType.symbol_type(typ)

    @staticmethod
    def add_subtype_relations(t: type):
        update = False

        for b in typelike_bases(t):
            LogicalType.add_subtype_relations(b)
            if (t, b) not in LogicalType.subtype_relations:
                LogicalType.subtype_relations.add((t, b))
                update = True

        if update:
            LogicalType.subtype_relations_form = B.And(
                *(
                    B.Implies(
                        sympy.Symbol(LogicalType.symbol_type(t)),
                        sympy.Symbol(LogicalType.symbol_type(b))
                    ) for t, b in LogicalType.subtype_relations
                )
            )

    @staticmethod
    def assert_types(*types) -> None:
        """Assert that the given values are all types."""

        assert all(is_typelike(typ) for typ in types), (
            f"some inputs are not types: {types}, "
            f"their respective types: {tuple(type(typ) for typ in types)}"
        )

    @staticmethod
    def form_of_type(t: type):
        if isinstance(t, LogicalType):
            return t.form
        else:
            LogicalType.add_subtype_relations(t)
            return sympy.Symbol(LogicalType.symbol_type(t))

    @staticmethod
    def form_of_instance(obj: TAny):
        if obj is None:
            # TODO: consider other literals here
            return NoneType().form
        else:
            type_form = LogicalType.form_of_type(type(obj))
            if isinstance(obj, Callable):
                return B.And(
                    type_form, sympy.Symbol(LogicalType.symbol_function(obj))
                )
            else:
                return type_form

    @staticmethod
    def types_of_form(form):
        """
        Get all the ways in which the formula can be satisfied in terms of the
        mentioned types which are set to True in the formula's satisfying assignments.
        """

        types_list = []

        for model in sympy.logic.inference.satisfiable(
            B.And(LogicalType.subtype_relations_form, form), all_models=True
        ):
            if model is False:
                break

            types = [eval_type(str(sym)) for sym, val in model.items() if val]
            types_list.append(set(types))

        return types_list

    @staticmethod
    def subtype(form1, form2):
        """
        Is the type formulated by `form1` a subtype of the type formulated by `form2`.
        """

        if not LogicalType.negation_enabled:
            # This method only works if we don't allow negation.
            if sympy.logic.inference.satisfiable(
                B.And(LogicalType.subtype_relations_form, form1, B.Not(form2))
            ) is not False:
                return False
            return True

        # The rest of this method works if negation is allowed but is too slow use.

        # Get the minimal set of types satisfying form1. These types represent
        # all of the methods that are available for types represented by form1.
        lhs_mros = LogicalType.types_of_form(form1)

        # Get the set of types/methods that can be expected of anything typed as form2 (and form1).

        rhs_mros1 = LogicalType.types_of_form(B.And(form1, form2))
        if len(rhs_mros1) == 0:
            return False

        rhs_mros2 = LogicalType.types_of_form(B.And(form1, B.Not(form2)))
        if len(rhs_mros2) == 0:
            return True

        lhs_mro = set.intersection(*lhs_mros)
        rhs_mro1 = set.union(*rhs_mros1)
        rhs_mro2 = set.union(*rhs_mros2)

        # (union(form1 & form2) - union(form1 & ~form2)) subset intersection(form1)
        # form1, form2
        # (union(form1 & form2) - union(form1 & ~form2)) subset intersection(form1)
        return set.issubset(rhs_mro1 - rhs_mro2, lhs_mro)

    def __init__(self, form: B.Boolean):
        self.form = form

    def __subclasscheck__(cls, cls2):
        return LogicalType.subtype(LogicalType.form_of_type(cls2), cls.form)

    def __instancecheck__(cls, obj):
        raise NotImplementedError(
            f"Instance check for type {cls} not implemented."
        )


class Type(LogicalType):
    """
    Promote a python type to a LogicalType.
    """

    def __new__(cls, typ: Annotation):
        typ = eval_type(typ, globals=caller_globals())
        LogicalType.assert_types(typ)

        return super().__new__(cls, fullname(typ), (), {})

    def __init__(self, typ: Annotation):
        self.typ = eval_type(typ, globals=caller_globals())
        LogicalType.assert_types(self.typ)

        LogicalType.__init__(self, form=LogicalType.form_of_type(self.typ))

    def __instancecheck__(cls, obj):
        return isinstance(obj, cls.typ)


class Given(LogicalType):
    """
    Annotation for parameters that should not be inferred.
    """

    def __new__(cls, typ: Annotation):
        # __new__ needed for type subtypes.
        typ: type = eval_type(typ, globals=caller_globals())

        LogicalType.assert_types(typ)

        return super().__new__(
            cls, f"{cls.__name__}({render_annotation(typ)})", (), {}
        )

    def __init__(self, typ: Annotation):
        self.typ_as_named = fullname(typ)
        self.typ = eval_type(typ, globals=caller_globals())

        LogicalType.__init__(self, form=LogicalType.form_of_type(self.typ))

    def __instancecheck__(cls, obj):
        return isinstance(obj, cls.typ)


class Optional(AutoNone, LogicalType):
    """
    An optional type with an instance check that returns true when tested with
    None.
    """

    # TODO: replace with Union(NoneType, Type(typ)) ?

    def __new__(cls, typ: Annotation):
        # __new__ needed for type subtypes.
        typ: type = eval_type(typ, globals=caller_globals())

        LogicalType.assert_types(typ)

        return super().__new__(
            cls, f"{cls.__name__}({render_annotation(typ)})", (), {}
        )

    def __init__(self, typ: Annotation):
        self.typ_as_named = fullname(typ)
        self.typ = eval_type(typ, globals=caller_globals())

        LogicalType.__init__(
            self,
            form=B.Or(LogicalType.form_of_type(self.typ),
                      NoneType().form)
        )

    def __instancecheck__(cls, obj):
        return obj is None or isinstance(obj, cls.typ)


class Function(LogicalType):
    """
    Function type. Can be used instead of Callable. Can give a method signature
    optionally for documentation but not for type checking presently.
    Instance/subclass check presently ignores signature. Any function is an
    instance of every Function type. This is implemented via
    LogicalType.symbol_function .
    """

    def __init__(self, signature: TOptional[Signature] = None):
        self.signature = signature
        LogicalType.__init__(
            self, form=sympy.Symbol(LogicalType.symbol_function(signature))
        )

    def __new__(cls, signature: TOptional[Signature] = None):
        return super().__new__(cls, "Function", (), {})

    def __instancecheck__(cls, obj):
        return isinstance(obj, Callable)


class Unit(LogicalType):
    """
    A type that cannot have any instances. Instance check always fail. This is
    used for types/classes which are not installed or cannot be retrieved for
    whatever reason.
    """

    def __init__(self):
        LogicalType.__init__(self, form=B.BooleanFalse())

    def __new__(cls):
        return super().__new__(cls, "Unit", (), {})

    def __instancecheck__(cls, obj):
        return False


class Any(LogicalType):
    """
    A type that contains everything. isinstance is always true and so is issubclass.
    """

    def __init__(self):
        LogicalType.__init__(self, form=B.BooleanTrue())

    def __new__(cls):
        return super().__new__(cls, "Any", (), {})

    def __instancecheck__(cls, obj):
        return True


class Literal(LogicalType):
    """
    Type inhabited only be a single given value. This assumes the value has an
    implementation for __str__ and this is used for type checking.
    """

    def __new__(cls, val: TAny):
        # __new__ needed for type subtypes.
        return super().__new__(cls, f"{val}Type", (), {})

    def __init__(self, val: TAny):
        self.val = val
        LogicalType.__init__(
            self, form=sympy.Symbol(LogicalType.symbol_literal(val))
        )

    def __instancecheck__(cls, obj):
        return cls.val == obj


class NoneType(Literal):
    """
    Type containing only the value `None`.
    """

    def __new__(cls):
        # __new__ needed for type subtypes.
        return Literal.__new__(cls, val=None)

    def __init__(self):
        Literal.__init__(self, val=None)


class Intersection(LogicalType):
    """
    Intersection type that can be used for isinstance and issubclass .
    """

    def __new__(cls, *types):
        # __new__ needed for type subtypes.

        globals = caller_globals()

        annotations = types
        types = tuple(eval_type(name, globals=globals) for name in types)

        LogicalType.assert_types(*types)

        if len(types) <= 3:
            display_names = ', '.join(map(str, annotations))
        else:
            display_names = "..."

        return super().__new__(cls, f"Intersection({display_names})", (), {})

    def __init__(self, *types: Tuple[Annotation]):
        # TODO(piotrm): printing work ongoing
        #self.types_as_named = tuple(
        #    t if isinstance(t, str) else fullname(t) for t in types
        #)
        globals = caller_globals()

        self.types = tuple(eval_type(typ, globals=globals) for typ in types)

        super().__init__(
            form=B.And(*(LogicalType.form_of_type(t) for t in self.types))
        )

    def __instancecheck__(cls, obj):
        return all(isinstance(obj, typ) for typ in cls.types)


class Union(LogicalType):
    """
    Union type that can be used for isinstance and issubclass .
    """

    def __new__(cls, *types: Tuple[Annotation]):
        # __new__ needed for type subtypes.

        globals = caller_globals()

        annotations = types
        types = tuple(eval_type(name, globals=globals) for name in types)

        LogicalType.assert_types(*types)

        if len(types) <= 3:
            display_names = ', '.join(map(str, annotations))
        else:
            display_names = "..."

        return super().__new__(cls, f"Union({display_names})", (), {})

    def __init__(self, *types: Tuple[Annotation]):
        globals = caller_globals()

        self.types = tuple(eval_type(typ, globals=globals) for typ in types)

        super().__init__(
            form=B.Or(*(LogicalType.form_of_type(t) for t in self.types))
        )

    def __instancecheck__(cls, obj):
        return any(isinstance(obj, typ) for typ in cls.types)


# TODO: replace with "Except" type.
class Not(LogicalType):
    """
    Not type. The use of this type introduces extreme computational requirements
    onto type checking methods. Please avoid.
    """

    def __new__(cls, typ):
        # __new__ needed for type subtypes.
        raise RuntimeError("Please do not use this type.")

        LogicalType.negation_enabled = True

        typ = eval_type(typ, globals=caller_globals())
        LogicalType.assert_types(typ)

        return super().__new__(cls, f"Not({fullname(typ)})", (), {})

    def __init__(self, typ: Annotation):
        self.type_as_named = typ if isinstance(typ, str) else fullname(typ)

        self.typ = eval_type(typ, globals=caller_globals())

        LogicalType.assert_types(self.typ)

        LogicalType.__init__(
            self, form=B.Not(LogicalType.form_of_type(self.typ))
        )

    def __instancecheck__(cls, obj):
        return not isinstance(obj, cls.typ)


@dataclass
class HelpInfo:
    imports: Union[Set[str], str] = None
    parameter_deps: dict[str, 'Parameter'] = None
    definition: list[str] = None
    args_map: dict[str, str] = None


class Parameter(AutoNone, LogicalType):
    """
    A parameter is a type decorated with a name and documentation. Its logical
    relationship to other types is the same as the enclosed type.
    """

    @staticmethod
    def base_param(param: TUnion['Parameter', Given, Optional]) -> 'Parameter':
        """
        If the given type is constructed from Parameter or (Given/Optional with
        a wrapped Parameter), get that Parameter. If given is a type that is not
        expected, returns None instead.
        """

        lens = Parameter.base_param_lens(param)
        if lens is None:
            return None
        else:
            return lens.get(param)

    @staticmethod
    def base_param_lens(
        param: TUnion['Parameter', Given, Optional]
    ) -> Lens[TUnion['Parameter', Given, Optional], Parameter]:
        """
        If the given type is constructed from Parameter or (Given/Optional with
        a wrapped Parameter), get a lens to access/set that Parameter. If given
        is a type that is not expected, returns None instead.
        """

        if isinstance(param, Parameter):
            return Lens(get=lambda t: t, set=lambda t, p: p)
        elif isinstance(param, Given) and isinstance(param.typ, Parameter):
            return Lens(get=lambda g: g.typ, set=lambda g, p: Given(p))
        elif isinstance(param, Optional) and isinstance(param.typ, Parameter):
            return Lens(get=lambda o: o.typ, set=lambda o, p: Optional(p))
        else:
            return None

    def __new__(
        cls,
        name: str,
        typ: Annotation,
        desc: str = "",
        help_info: HelpInfo = None
    ):
        # __new__ needed for type subtypes.

        typ = eval_type(typ, globals=caller_globals())

        display_name = Parameter._display_name(name, typ, desc)

        return super().__new__(cls, display_name, (), {})

    @staticmethod
    def _display_name(
        name: str, typ: type, desc: str, display_name: str = None
    ):
        return display_name or f"P({name}:{shortname(typ)})"

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return str(self)

    def __init__(
        self,
        name: str,
        typ: type,
        desc: str = "MISSING_ABOUT",
        help_info: HelpInfo = None
    ):
        self.name = name
        self.desc = desc
        self.param_name = None
        self.typ = eval_type(typ, globals=caller_globals())
        self.help_info = help_info
        # if self.help_info is None and self.param_name is not in <LIST_OF_SIGNATURE_VARIABLES>:
        #     raise ValueError(f"Missing user help documentation for parameter {self.param_name}")

        display_name = Parameter._display_name(name, self.typ, desc)
        self.display_name = display_name

        LogicalType.assert_types(self.typ)

        LogicalType.__init__(
            self, form=B.And(LogicalType.form_of_type(self.typ))
        )

    def __instancecheck__(cls, obj):
        if hasattr(cls.typ, "__origin__") and cls.typ.__origin__:
            origin_cls = cls.typ.__origin__
        else:
            origin_cls = cls.typ

        return isinstance(obj, origin_cls)

    @classmethod
    def display_help_doc(
        cls, params: Iterable[Parameter], state: 'State', method_name: str
    ):
        imports = set()
        definition_code = []
        method_args = {}
        resolved_params = set()

        def resolve_param(param):
            nonlocal method_args
            help_info: HelpInfo = param.help_info
            if param in resolved_params or help_info is None:
                return

            if help_info.parameter_deps:
                for var_name, param in help_info.parameter_deps.values():
                    if param.name not in state:
                        resolve_param(param)
                        if var_name != param.name:
                            definition_code.append(f"{var_name} = {param.name}")

            if help_info.definition:
                definition_code.append("\n".join(help_info.definition))

            if help_info.args_map:
                method_args = {**method_args, **help_info.args_map}
            resolved_params.add(param)

        for param in params:
            resolve_param(param)

        if len(imports):
            import_block = []
            for pkg in imports:
                if "." in pkg:
                    modules = pkg.split(".")
                    pkg_path = ".".join(modules[:-1])
                    import_block.append(f"from {pkg_path} import {modules[-1]}")
                else:
                    import_block.append(f"import {pkg}")
            import_block = "\n".join(import_block) + "\n"
        else:
            import_block = ""

        definition_code_str = "\n\n".join(definition_code)
        method_args = ", ".join(
            f"{arg_name}={arg_value}"
            for arg_name, arg_value in method_args.items()
        )

        help_template = cleandoc(
            """
        {import_block}
        from truera.client.nn.explain import NLPExplainer
        e = Explainer()

        # Define missing sample arguments used in {method_name} 
        {definition_code_str}

        # Call {method_name}
        e.{method_name}({method_args})
        """
        )
        help_doc = help_template.format(
            import_block=import_block,
            method_name=method_name,
            definition_code_str=definition_code_str,
            method_args=method_args
        )
        result = f"\n🚨 NOTE: You may be able to resolve some of these issues by adding the following arguments to {method_name}(). " \
        "Replace the sample values your own:\n" + help_doc
        print(result)
