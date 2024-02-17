"""
# Quickstart: Unmanaged Anonymous Explanations.

The highest-level interface to nlp explanations. In this interface, the truera
workspace object is not exposed and all required ingestion elements are treated
anonymously, in that no name is needed to be given to a model, data split, or
data collection. The user needs to provide some model and some data. After this,
they can ask for any of the existing explanation types.

## Basic Usage

The `Explainer` object handles the highlevel interface. A model can be provided
either with the `Explainer` constructor or the `set_model` method, both of which
are overloaded for various model types and configuration options. Data is then
provided either with the `explain` or `set_data` methods, the first of which
also produces a default explanation. Finally, explanation parameters can be
provided to the `explain` or `config` methods.

```python
    Explainer(model).explain("hello there") 

    Explainer(model, tokenizer).explain(["first sentence", "second sentence"])
    
    Explainer(model, tokenizer, resolution=32).explain(...)

    exp = Explainer(model) # Do model wrapping and checking here.

    exp.explain(['first sentence', 'second sentence'])
    # Do the data wrapping, checking, and then produce some explanations.

    exp.explain(Path("somefile.csv"))

    exp.explain(Path("somefile.csv"), textfield="tweet", labelfield="sentiment")

    # Further usage

    explanations exp.global_token_influence(...)
    # ... is global_token_influence configuration

    exp.global_token_influence(data=somedataset, ...) 
    # TODO: should we try to get something like the working as well?
```

This should produce some basic explanations for "hello there" model input, the
two example sentences, or the contents of some CSV files. This, however, assumes
`model` is one of the recognized models types for which wrappers can be
inferred. We expect huggingface sentence classifiers to be one of the few
examples for which explanations can be retrieved as above.

# Input Types Robustness

Before explanations are provided, the user needs to provide at least a model and
at least one instance (instance requirement may be relaxed). These can be in
many forms.

## Data Types

    - TODO: datasets <class 'datasets.arrow_dataset.Dataset'> 
    - TODO: torch <class 'torch.utils.data.dataset.Dataset'> 
    - TODO: torch <class 'torch.utils.data.dataloader.DataLoader'> 
    - TODO: pandas <class 'pandas.core.frame.DataFrame'> 
    - TODO: pandas <class 'pandas.core.series.Series'>
    - TODO nltk datasets 
    - TODO: numpy <class 'numpy.ndarray'> 
    - TODO: python typing.Mapping or <class 'dict'> 
    - python typing.Sequence or <class 'list'> or <class 'tuple'>
    - python typing.Iterable 
    - python string (a single text instance)
    - TODO filenames 
    - TODO tensorflow 
    - TODO remote sources?

## Model Types

    - transformers/huggingface pytorch text classifiers
      `PModelHugsTextClassifier` (see `parameters.py`)
    - TODO: transformers tf classifiers `TTFHugsTextClassifier` (see
      `parameters.py`)
    - TODO: transformers classifiers `THugsTextClassifier` (see `parameters.py`)
    - TODO: transformers <class 'transformers.modeling_utils.PreTrainedModel'>
    - TODO: torch <class 'torch.nn.modules.module.Module'>
    - TODO: tensorflow <class 'tensorflow.python.framework.ops.Graph'> 
    - TODO: tensorflow <class 'keras.engine.training.Model'> 
    - TODO: blackbox / callable predict function

## Tokenizer Types

Tokenizers can sometimes be inferred from model but if not, they can be provided
in one of several forms:

    - transformers tokenizers `PTokenizerHugs` (see `parameters.py`)
    - tensorflow pre-processors 
    - TODO: nltk tokeninzers

# Keyword/Position Robustness

The `Explainer` constructor should be robust in terms of how it extracts the
required information from arguments if they are provided by keyword or by
position. No keywords should be mandatory but if given, they should contain
specific contents (not be robust in terms of their contents). For example:

```python
   Explainer(model=some_pretrained_model).explain(data='some sentence')
```

The `model` keyword should always specific a model and `data` should always
specify data. On the other hand, positional arguments are handled be their type,
not their position. If one of the data types (as above) is encountered, it is
assumed to be data, not anything else. Thus these are equivalent:

```python
    Explainer(tokenizer, model) 
    
    Explaimer(model, tokenizer)
```

This might cause problems if multiple arguments with the same type are provided
at once. Will have to reconsider this in the future.

# Dispatch

The robustness described above is a generalization of the concept of "dispatch"
or method overloading in typed languages. There a method may have multiple
definitions with different argument types. The runtime determines the
appropriate method to use from among options based on the types provided as
arguments. We generalize the concept to python and our use case in several ways:

- Position independence. Non-keyword arguments can be placed in any position.
- Types from optional packages. Some types may refer to packages not installed
  hence we need to be able to resolve them only if installed but otherwise
  ignore.

# Optional Parameters and Inference

The overloaded `Explainer` methods come with many optional arguments. For
example, this model specification based on a pytorch huggingface classification
model:

```python
    def set_model(self,
          model: Given(PModelHugsTextClassifier), 
          tokenizer: PTokenizerHugs,
          token_embeddings_layer: PTokenEmbeddingsLayer,
          ...
    ) -> str:
```

The arguments annotated with a parameter type (start with "P") indicate that they can be
inferred but that if the inference fails, an error is raised. These are filled
in automatically before the method is called using the various infernce
utilities in `infer.py`. For example this method
for figuring out the `token_embeddings_layer`:

```python
    def token_embeddings_layer(
        self, model: PHugsTextClassifier, trulens_wrapper: PTrulensWrapper
    ) -> PTokenEmbeddingsLayer:
```

Notice that this method itself includes arguments annotated with `Parameter`
types so they get filled in as well. See `psys.py` on how this is done.

# TODO(piotrm): not yet done/tested
Arguments annotated with `Optional` (our own Optional variant, not the one that
comes with python), are also inferred but failure of inference is a warning and
results in disabled features.

# External Robustness vs Internal Interfaces

Even though dispatch is robust to many types of arguments, and we can wrap
different types of models and datasets, it is important that after dispatch is
done, we have a consistent set of objects to work with. At the surface level
this is in terms of producing a collection of wrappers with strict interfaces.
Regardless of what a user provides as data, we will store it and process it
using a very specific type. Therefore, any functionality we provide will be in
terms of the specific type, not in terms of the provided type.

# Limitations

As the main operation of this file is producing wrappers from a wide variety of
data, we have some limitations in terms of what can be made visible to a user
after wrappers are made. If a user provides data as a torch DataLoader, for
example, they will not be able to interact with us in through DataLoader after
we have produced our wrappers, they can only interact with us in terms
implemented by the produced wrappers.

## pylint

The method overloading confuses pylint. One can use these exceptions:

- pylint: disable=E1101

  Use this if pylint complains about unexpected keyword arguments to overloaded
  methods.

- pylint: disable=E1123

  Same.

# Ramp to Managed Experience

The user has several avenues to expand towards the more custom managed
experience via the TrueraWorkspace. 

## Names and Workspace

One can retrieve and/or provide a workspace object to/from the `Explainer`:

```python
    e = Explainer(workspace=some_existing_workspace)

    e.workspace # is the underlying workspace
```

Secondly, a user can give optional names to models and data_splits so that they
can then be accessed from the managed workspace:

```python
    e = Explainer(model, model_name="foo")
    e.explain(["hello there", "bob !"], data_split_name="mysplit")

    e.workspace.get_models() # contains model "foo"
    e.workspace.get_data_splits() # contains data_split "mysplit"
```

One can also let `Explainer` generate random names for them which can then be
used with a workspace.

```python
    e = Explainer()

    model_name = e.set_model(model)

    data_split_name = e.set_data("some data")
```

## Use autowrap

The second ramp is via access to `autowrap`:

```python
    e = Explainer().autowrap(...) # ... is all autowrap arguments
```

The produced wrappers are then stored in the `Explainer`.

TODO: Presently this is not useful as autowrap wraps models and data at once so
there is no reason at all to use autowrap and the other Explainer methods at the
same time.

## Use existing wrappers

Finally, one can specify existing wrappers to the `Explainer`:

```python
    e = Explainer()
    
    e.set_model(model_run=..., model_load=...)

    e.set_data(split_load=...)

    e.explain()

### Partial inference experience

If something needed for our underlying explainer cannot be determined from what
the user gives us, they need to fill in the missing pieces. The workflow looks
like this:

```python
    e = Explainer().set_model(MODELARGS1)

    >>> error, cannot determine something, error message includes the following code snippet:

    # BEGIN CODE SNIPPET

    partial_model = Explainer.prepare_model(MODELARGS1)

    required_missing_value: int = ...
    # Documentation about this required value.

    # TODO: figure out whether we want to give partial_model as additional input
    def required_missing_function(partial_model, ...): ...
        something = partial_model.inferred_value
        return something+42

    def required_missing_function(...): ...
        something = partial_model.inferred_value
        return something+42

    # Documentation about this function.
    # (user can use partial_model.inferred_value and partial_model.inferred_function inside here)
    ... verify call here ...

    # Rest of the snippet contains overview of the parameters which were
    # inferred which can be used inside the above. Noting that they can
    # override any of them if desired.

    # inferred_value: int = 42 
    # Documentation about inferred_value.

    # def inferred_function(...): ...
    # Documentation about inferred_function.
    ...        

    # TODO: figure out which if these is best:
    e = Explainer().set_model(MODELARGS1, required_missing_value, required_missing_function)
    e = Explainer().set_model(partial_model, required)
    e = Explainer().set_model(partial_model) # if they extended partial model with reqs.

    # END CODE SNIPPET
```

In the above, the user is requested to fill in some missing pieces in a
class definition by extending `partial_model`. This is an abstract class
whick will prevent the extension from initializing unless all requirements
are met.

Once filled in, the class can be initialized and given to
Explainer.set_model.

#### Partial inference of data wrapper

`set_data` may also fail to infer some parameters. It is less clear here that
partially inferred parameters are useful for the user though. Letting them know
the inferred values, however, may be useful. This the proposed workflow is this:

```python

    e = Explainer(MODELARGS1) # succeeds

    explanation = e.explain(DATAARGS1)

    >>> error, cannot determine something, the error message includes the following text:

    Please provide values for arg3, arg4 and/or adjust values for the other arguments.

    - arg3: arg3 documentation
    - arg4: arg4 documentation

    Inferred arguments:

    - arg1 = arg1 value: arg1 documentation
    - arg2 = arg2 value: arg2 documentation
```

TODO(piotrm): figure out whether it is worthwhile to have a separate
"set_schema" method from "set_data" or "explain" methods, to indicate things
like text column names in a pandas dataframe that are not the actual data but
are needed to extract it.

#### Hidden parameters

With respect to the prior section, notice that there are more things being
inferred in `infer.py` than there are possible arguments to the overloaded
user-facing methods in `quick.py`. Those extra "hidden" parameters cannot be
provided by the user given the present overloaded methods interface here. If any
of those parameters ends up being more convenient for users to provide, either
add them as optional parameters to an overloaded user-facing method or
reconsider the separation between overloaded user-facing and hidden inferences
design.
"""

# TODO: Lots of things here should be moved to utilities and/or shared with
# utilities in trulens.

from __future__ import annotations

from inspect import BoundArguments
from inspect import Signature
import logging
import os
from pathlib import Path
from typing import Any, Callable, List
from typing import Optional as TOptional
from typing import TYPE_CHECKING, Union
from uuid import uuid4

import pandas as pd

from truera.client.local.intelligence.local_nlp_explainer import \
    LocalNLPExplainer
from truera.client.nn.client_configs import NLPAttributionConfiguration
from truera.client.nn.explain.infer import derive_defaults
from truera.client.nn.explain.parameters import PClassificationThreshold
from truera.client.nn.explain.parameters import PDataCollectionName
from truera.client.nn.explain.parameters import PDataInstance
from truera.client.nn.explain.parameters import PDataIterable
from truera.client.nn.explain.parameters import PDataPandas
from truera.client.nn.explain.parameters import PDataSequence
from truera.client.nn.explain.parameters import PDataSplitName
from truera.client.nn.explain.parameters import PDataTorchDataLoader
from truera.client.nn.explain.parameters import PDebugArg
from truera.client.nn.explain.parameters import PDebugModel
from truera.client.nn.explain.parameters import PDSFromSource
from truera.client.nn.explain.parameters import PEvalModel
from truera.client.nn.explain.parameters import PFieldLabel
from truera.client.nn.explain.parameters import PFieldsMeta
from truera.client.nn.explain.parameters import PFieldText
from truera.client.nn.explain.parameters import PGetModel
from truera.client.nn.explain.parameters import PLabelInstance
from truera.client.nn.explain.parameters import PLabelsIterable
from truera.client.nn.explain.parameters import PLabelsSequence
from truera.client.nn.explain.parameters import PMetaPandas
from truera.client.nn.explain.parameters import PModel
from truera.client.nn.explain.parameters import PModelBlackbox
from truera.client.nn.explain.parameters import PModelHugsAudioClassifier
from truera.client.nn.explain.parameters import PModelHugsTextClassifier
from truera.client.nn.explain.parameters import PModelLoadWrapper
from truera.client.nn.explain.parameters import PModelName
from truera.client.nn.explain.parameters import PModelRunWrapper
from truera.client.nn.explain.parameters import PModelTF1
from truera.client.nn.explain.parameters import PModelTF2
from truera.client.nn.explain.parameters import PModelTorch
from truera.client.nn.explain.parameters import PNEmbeddings
from truera.client.nn.explain.parameters import PNMetricsRecords
from truera.client.nn.explain.parameters import PNOutputNeurons
from truera.client.nn.explain.parameters import PNRecords
from truera.client.nn.explain.parameters import PNTokens
from truera.client.nn.explain.parameters import POutputAnchor
from truera.client.nn.explain.parameters import POutputLayer
from truera.client.nn.explain.parameters import PPadTokenId
from truera.client.nn.explain.parameters import PProjectName
from truera.client.nn.explain.parameters import PRebatchSize
from truera.client.nn.explain.parameters import PRefToken
from truera.client.nn.explain.parameters import PResolution
from truera.client.nn.explain.parameters import PScoreType
from truera.client.nn.explain.parameters import PSpecialTokens
from truera.client.nn.explain.parameters import PSplitLoadWrapper
from truera.client.nn.explain.parameters import PStandardizeDatabatch
from truera.client.nn.explain.parameters import PTextToInputs
from truera.client.nn.explain.parameters import PTextToSpans
from truera.client.nn.explain.parameters import PTextToTokenIds
from truera.client.nn.explain.parameters import PTokenEmbeddingsAnchor
from truera.client.nn.explain.parameters import PTokenEmbeddingsLayer
from truera.client.nn.explain.parameters import PTokenizer
from truera.client.nn.explain.parameters import PTokenizerHugs
from truera.client.nn.explain.parameters import PTokenizerWrapper
from truera.client.nn.explain.parameters import PUnkTokenId
from truera.client.nn.explain.parameters import PUseTrainingMode
from truera.client.nn.explain.parameters import PVocab
from truera.client.nn.explain.psys import State
from truera.client.nn.wrappers import nlp as nlp
from truera.client.nn.wrappers.autowrap import autowrap as autowrapper_autowrap
from truera.client.util.debug import Capture
from truera.client.util.doc import doc_untab
from truera.client.util.func import bind_relevant_and_call
from truera.client.util.func import sig_render
from truera.client.util.overload import BindingsHook
from truera.client.util.overload import overload
from truera.client.util.python_utils import import_optional
from truera.client.util.types import Given
from truera.client.util.types import NoneType
from truera.client.util.types import Optional
from truera.client.util.types import Parameter

if TYPE_CHECKING:
    from truera.client.local.intelligence.local_explainer import LocalExplainer
    from truera.client.local.local_truera_workspace import LocalTrueraWorkspace

logger = logging.getLogger(name=__name__)

trulens = import_optional("trulens", "NLP model explanations")

delete_stale_parameters: BindingsHook


def delete_stale_parameters(
    acc: State, func: Callable, sig: Signature, bindings: BoundArguments
):
    """
    Delete existing parameters that appear in function signature. This hook is
    called in overload.py::sig_bind() .
    """

    explainer: NLPExplainer = bindings.arguments['self']
    state: State = explainer.state

    for name, param in sig.parameters.items():
        p = None
        if isinstance(param.annotation, Parameter):
            p = param.annotation
        elif isinstance(param.annotation,
                        Given) and isinstance(param.annotation.typ, Parameter):
            p = param.annotation.typ

        if p is not None and p in state:
            state.delete(p)

    return acc, bindings  # unchanged


save_inferred_state: BindingsHook


def save_inferred_state(
    acc: State, func: Callable, sig: Signature, bindings: BoundArguments
):
    """
    Save inferred Parameter arguments to finalized state. This hook is called in overload.py::sig_bind()
    """
    explainer: NLPExplainer = bindings.arguments['self']
    bound_state: State = acc
    state: State = explainer.state
    state.update(bound_state)

    return state, bindings

    # TODO(piotrm): do we want to save things which were involved in an
    # inference even if they were not seen in the signatures in quick.py (but
    # seen in rules in infer.py)?
    """
    for name, param in sig.parameters.items():
        if isinstance(param.annotation, Parameter):
            state.set(param.annotation, bindings.arguments[name])
        elif isinstance(param.annotation,
                        Given) and isinstance(param.annotation.typ, Parameter):
            state.set(param.annotation.typ, bindings.arguments[name])
        elif isinstance(param.annotation, Optional
                       ) and isinstance(param.annotation.typ, Parameter):
            state.set(param.annotation.typ, bindings.arguments[name])

    return acc, bindings  # unchanged
    """


def save_bound_signature(
    acc: State, func: Callable, sig: Signature, bindings: BoundArguments
):
    """
    Store bound signature in Explainer. This hook is called in overload.py::sig_bind()
    """
    explainer: NLPExplainer = bindings.arguments['self']
    explainer.ingestion_signatures.append(sig)
    if hasattr(func, '__overload_name__'):
        explainer.called_methods.add(func.__overload_name__)
    else:
        explainer.called_methods.add(func.__name__)
    return acc, bindings


_overload = overload(
    post_bind_hooks=[
        # first delete state parameters
        delete_stale_parameters,
        # then derive parameter values
        derive_defaults(
            state_factory=lambda bindings: bindings.arguments['self'].state
        ),  # self is Explainer
        # then save them into Explainer.state
        save_inferred_state,
        save_bound_signature,
    ]
)


def disable_inference():
    os.environ["TRU_QUICK_NN_INFERENCE_FLAG"] = "0"


def enable_inference():
    os.environ["TRU_QUICK_NN_INFERENCE_FLAG"] = "1"


class NLPExplainer:
    """
    High-level explanations interface for NLP models. There is no model, data
    collection, or split naming in this interface. 
    """

    # Value for these parameters need to be known before autowrap is called:
    AUTOWRAP_PARAMETERS = [
        PGetModel, PEvalModel, PVocab, PUnkTokenId, PPadTokenId, PSpecialTokens,
        PTextToInputs, PTextToTokenIds, PTextToSpans, PNEmbeddings, PNTokens,
        PDSFromSource, PStandardizeDatabatch
    ]

    # These need to be known before attribution can be configured (see
    # NLPAttributionConiguration):
    ATTRIBUTION_PARAMETERS = [
        PTokenEmbeddingsLayer, PTokenEmbeddingsAnchor, POutputLayer,
        POutputAnchor, PNOutputNeurons, PNMetricsRecords, PRefToken,
        PResolution, PRebatchSize, PUseTrainingMode
    ]

    # These need to be known before a model and data can be ingested by
    # TrueraLocalWorkspace:
    WORKSPACE_PARAMETERS = [
        PProjectName, PModelName, PDataCollectionName, PDataSplitName,
        PScoreType
    ]

    # These have to be specified in order to skip the autowrapping.
    WRAPPER_PARAMETERS = [
        PTokenizerWrapper, PModelLoadWrapper, PModelRunWrapper,
        PSplitLoadWrapper
    ]

    # TODO(piotrm): migrating this Parameter keys in self.state.
    CACHE_KEYS = set(
        [
            'model',

            # autowrap
            'get_model',
            'eval_model',
            'vocab',
            'unk_token_id',
            'pad_token_id',
            'special_tokens',
            'text_to_inputs',
            'text_to_token_ids',
            'text_to_spans',
            'n_embeddings',
            'n_tokens',
            'ds_from_source',
            'standardize_databatch',
            "n_records",

            # NLPAttributionConfiguration
            'token_embeddings_layer',
            'token_embeddings_anchor',
            'output_layer',
            'output_anchor',
            'n_output_neurons',
            'n_metrics_records',
            'ref_token',
            'resolution',
            'rebatch_size',
            'use_training_mode',

            # LocalTrueraWorkspace
            'project_name',
            'model_name',
            'data_collection_name',
            'data_split_name',
            'score_type',
            'classification_threshold'
        ]
        # 'model_path' # autowrap, not using
        # 'data_path' # autowrap, not using
    )

    def __init__(
        self,
        *args,
        workspace: TOptional[LocalTrueraWorkspace] = None,
        persist: TOptional[Path] = None,
        **kwargs
    ):
        """
        Initalize and create model parameters from the given args if any. If
        `workspace` is given, uses it under the hood or otherwise creates one.
        If `persist` is given, will cache explanations in the specified folder
        which can be reloaded in another notebook/process.
        """

        from truera.client.local.local_truera_workspace import \
            LocalTrueraWorkspace

        self.tru = workspace or LocalTrueraWorkspace(persist=persist)

        # Once project parameters are figured out, add the various named objects
        # with anonymous or specified names.
        self.project_name = None
        self.model_name = None
        self.data_collection_name = None
        self.data_split_name = None
        self.ingestion_signatures = []
        self.called_methods = set()

        # Once wrappers are constructed, hold them here.
        self.wrappers = nlp.WrapperCollection()

        self.state = State({})  # parameter to value map

        # If arguments were given to constructor, assume they were setting up a model.
        if len(args) + len(kwargs) > 0:
            self.set_model(*args, **kwargs)

        # Will be filled in later once enough wrappers are constructed.
        self.explainer: LocalNLPExplainer = None

    @property
    def workspace(self):
        return self.tru

    def autowrap(self, **kwargs) -> None:
        # NOTE(piotrm): docstring comes from autowrap.autowrapper below.
        # TODO: fix signature in printout to be also from autowrap.autowrapper .

        new_wrappers = bind_relevant_and_call(autowrapper_autowrap, **kwargs)

        self.wrappers.join_in_place(new_wrappers)

        return self

    # Use autowrap's docstring.
    autowrap.__doc__ = autowrapper_autowrap.__doc__

    def help(self) -> None:
        """Print out starting documentation on NLPExplainer usage."""

        msg = doc_untab(NLPExplainer)[1]
        msg += "\n\n"
        msg += self._help_methods(withdoc=True)

        print(msg)

    def __getattr__(self, name: str) -> Any:
        """
        Dispatch looking for not found attributes to LocalNLPExplainer if they are 
        defined there. If neither NLPExplainer nor LocalNLPExplainer has the required 
        attribute, an index of available methods is printed.
        """

        if hasattr(LocalNLPExplainer, name) and self.explainer is None:
            raise RuntimeError(
                "Before calling `LocalNLPExplainer` methods, a model and data need to be specified."
            )

        if self.explainer is not None and hasattr(self.explainer, name):
            return getattr(self.explainer, name)

        # TODO: Potentially restrict to these? NOTE(piotrm): Keeping the comment
        # string here so that people searching for any of these names will find
        # __getattr__ .
        """
        def get_feature_influences(self): pass
        def compute_feature_influences(self): pass
        def list_performance_metrics(self): pass
        def compute_performance(self): pass
        def global_token_summary(self): pass
        def data_exploration_tab(self): pass
        def record_explanations_attribution_tab(self): pass
        def model_robustness_analysis_tab(self): pass
        def token_influence_comparison_tab(self): pass
        def evaluate_text_tab(self): pass
        def upload_project(self): pass
        """

        msg = f"NLPExplainer has no such attribute {name}.\n\n"
        msg += self._help_methods()
        raise AttributeError(msg)

    def _help_methods(self, withdoc=False) -> str:
        msg = ""
        msg += "Available methods:\n\n"
        for k in dir(self):
            v = getattr(self, k)
            if not isinstance(v, Callable):
                continue
            if k[0] == "_":
                continue
            msg += "  " + sig_render(v, withdoc=withdoc) + "\n\n"

        msg += "\n\n"
        msg += "Available explanation methods:\n\n"
        for k in dir(LocalNLPExplainer):
            v = getattr(LocalNLPExplainer, k)
            if not isinstance(v, Callable):
                continue
            if k[0] == "_":
                continue
            msg += "  " + sig_render(v, withdoc=withdoc) + "\n\n"

        return msg

    def _build_wrappers(self, verify: bool = True):
        """
        Build or rebuild wrappers using autowrap. Most of the truera workspace
        state management is here.
        """

        cap = Capture.for_term()
        try:
            with cap:

                if all(p in self.state for p in self.WRAPPER_PARAMETERS):
                    # If wrappers were ingested, do not rebuild.
                    print("Using specified wrappers.")
                    wrappers = {
                        p.name: self.state.get(p)
                        for p in self.WRAPPER_PARAMETERS
                    }
                    self.wrappers = nlp.WrapperCollection(**wrappers)

                else:
                    for p in self.AUTOWRAP_PARAMETERS:
                        if p not in self.state:
                            raise RuntimeError(
                                f"Parameter {p} is required for autowrap."
                            )
                            # TODO(corey): better help about parameter p here.

                    print("Building wrappers using autowrap.")
                    # Fill in arguments to autowrap from ones contained in config.
                    # Call autowrap and add the results to our wrappers.
                    autowrap_wrappers = self.state.bind_relevant_and_call(
                        autowrapper_autowrap
                    )
                    # TODO(corey): if autowrap fails, produce guidence in terms
                    # of quicker quickstart parameters if possible..
                    self.wrappers.join_in_place(autowrap_wrappers)

                wrappers = self.wrappers

                model_run_wrapper = wrappers.model_run_wrapper
                model_load_wrapper = wrappers.model_load_wrapper

                # Check that some data has been specified.
                assert PNRecords in self.state, "Need to specify some data to explain first."

                for p in self.ATTRIBUTION_PARAMETERS:
                    if p not in self.state:
                        raise RuntimeError(
                            f"Parameter {p} is required for attribution configuration."
                        )
                        # TODO(corey): better help about parameter p here.

                # Create an attribution configuration, from the common set of
                # configuration parameters that are accepted by the NLP variant.
                attr_config = self.state.bind_relevant_and_call(
                    NLPAttributionConfiguration
                )
                # also save for debugging purposes:
                self.attr_config = attr_config

                # TODO: consider allowing these as optional inputs in the quick interface.
                # Create a project if not already present in the stateful interface.
                if self.project_name is None:
                    # Need to keep the project name fixed so cache directory generation
                    # can find existing caches.
                    # self.project_name = "anonymous_project"  # gen_name("project")
                    self.project_name = f"project_{uuid4()}"
                    self.tru.add_project(
                        self.project_name,
                        score_type=self.state.get(PScoreType),
                        input_type="text"
                    )
                    print(f"created anonymous project {self.project_name}")

                # Create a data collection in the stateful interface.
                if self.data_collection_name is None:
                    # Need to keep the data collection name fixed so cache directory
                    # generation can find existing caches.
                    self.data_collection_name = f"data_collection_{uuid4()}"  # gen_name("data_collection_name")
                    self.tru.add_data_collection(self.data_collection_name)
                    print(
                        f"created anonymous data collection {self.data_collection_name}"
                    )

                # Create a split in the stateful interface. Delete the old one if one
                # already exist with the given name.
                if self.data_split_name is None:
                    self.data_split_name = self.state.get(PDataSplitName)

                    # TODO: This has to be done somewhere else:
                    # if self.data_split_name in self.tru.get_data_splits():
                    #     self.tru.delete_data_split(self.data_split_name)

                    self.tru.add_nn_data_split(
                        self.data_split_name, wrappers, split_type="test"
                    )

                    logger.debug(
                        f"created anonymous data_split {self.data_split_name}."
                    )

                # Same with model.
                if self.model_name is None:
                    if PModelName in self.state:
                        self.model_name = self.state.get(PModelName)
                    else:
                        self.model_name = "model"

                    # Create a model in the stateful interface.
                    # TODO(piotrm): does this also need a new data collection?
                    self.tru.add_nn_model(
                        self.model_name,
                        model_load_wrapper,
                        model_run_wrapper,
                        attr_config,
                        classification_threshold=self.state.
                        get(PClassificationThreshold)
                    )
                    self.tru.set_model(self.model_name)

                    print(f"created anonymous model {self.model_name}")

                model = self.state.get(PModel)

                if verify:
                    print("verifying ...")
                    self.tru.verify_nn_wrappers(
                        clf=model,
                        model_run_wrapper=wrappers.model_run_wrapper,
                        split_load_wrapper=wrappers.split_load_wrapper,
                        model_load_wrapper=wrappers.model_load_wrapper,
                        tokenizer_wrapper=wrappers.tokenizer_wrapper,
                        attr_config=attr_config
                    )
                    print("done")
                # TODO(corey): if verify here fails, try to produce messages in
                # terms of parameters if possible.

                # Finally get an explainer.
                self.explainer: LocalExplainer = self.tru.get_explainer(
                    self.data_split_name
                )

                self.explainer._metadata = self.state.get(PMetaPandas)
                # TODO(piotrm): better metadata handling
                # TODO(infra): storage and retrieval of metadata alongside other data

        finally:
            if not cap.ok():
                cap.display()

    def _reset_model(self):
        # Force adding a new model to stateful interface next time explanation is asked for.
        if self.model_name is not None:
            self.model_name = None

    def _reset_data(self):
        # Force rebuild of wrappers next time an explanation is asked for.
        if self.explainer is not None:
            self.explainer = None

        # Also make sure new data_split_name gets picked up from infered parameters.
        if self.data_split_name is not None:
            self.data_split_name = None

    def _reset_config(self):
        # Reset various explanation-related parameters in preparation for `configure`.
        pass

    def _reset_tokenizer(self):
        # Reset various tokenizer-related parameters in preparation for `set_tokenizer`.
        pass

    def explain(
        self,
        *args,
        data: Optional[Union[str, List[str], List[List[str]],
                             pd.DataFrame]] = None,
        token_type: str = "word",
        pad_influences: bool = False,
        verify: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """Produce an explanation. The data to explain must be specified via data kwarg or by a prior set_data call.

        Args:
            data (Optional[Union[str, List[str], List[List[str]], pd.DataFrame]], optional): Data to explain. Can also be provided via a prior call to set_data. Defaults to None.
            token_type (str, optional): Determines the level of granularity for the explanations computed. Can be "token" or "word". Defaults to "word".. Defaults to "word".
            pad_influences (bool, optional): If True, returns influences as zero-padded array
            verify (bool, optional): If True, runs validation on provided arguments. Defaults to True.

        Returns:
            pd.DataFrame: A pandas DataFrame consisting of explanations for each token along with other record information.
        """
        if token_type == "word" and self.state.get(PTextToSpans) is None:
            logger.info(
                "text_to_spans is not provided. Setting `token_type = 'token'`"
            )
            token_type = "token"

        rebuild: bool = False

        if len(args) + len(kwargs) > 0:
            if PNRecords in self.state:
                print(
                    "Data already previously specified. Ignoring data parameter."
                )
            else:
                print("Ingesting data.")
                self.set_data(*args, data=data, **kwargs)

            # This causes attribution configuration to be recreated:
            rebuild = True

        if rebuild or self.explainer is None:
            # build the wrappers
            if PRebatchSize not in self.state:
                # IF PRebatchSize is known, config must already have been called
                self.config(
                    **kwargs
                )  # no positional arguments can be given here

            self._build_wrappers(verify=verify)

        kwargs['token_type'] = token_type
        kwargs['pad_influences'] = pad_influences

        return bind_relevant_and_call(
            self.explainer.compute_feature_influences, kwargs
        )

    # Model Wrappers

    @_overload(user_visible=False)
    def set_model(
        self,
        model_run: Given(PModelRunWrapper),
        model_load: Given(PModelLoadWrapper),
        tokenizer: Given(PTokenizerWrapper),
        model_name: Optional(PModelName),
        token_embeddings_layer: PTokenEmbeddingsLayer,
        token_embeddings_anchor: PTokenEmbeddingsAnchor,
        output_layer: POutputLayer,
        output_anchor: POutputAnchor,
        n_output_neurons: PNOutputNeurons,
        n_embeddings: PNEmbeddings,
        n_tokens: PNTokens,
        score_Type: PScoreType,
        classification_threshold: Optional(PClassificationThreshold),
        vocab: PVocab,
        unk_token_id: PUnkTokenId,
        pad_token_id: PPadTokenId,
        special_tokens: Optional(PSpecialTokens),
        __model: PModel  # make sure PModel is inferred and stored in self.state
    ) -> str:
        """
        Use existing wrappers.
        """

        print("Using existing model and tokenizer wrappers.")
        # Wrappers get saved in self.state and used in _build_wrappers.

        self._reset_model()

        return model_name

    set_model.dispatch.redoc(
        f"""
Specify a model.

        Common arguments:
        
        - model_name: {PModelName.typ} -- {PModelName.desc}

        - token_embeddings_layer: {PTokenEmbeddingsLayer.typ} -- {PTokenEmbeddingsLayer.desc}

        - token_embeddings_anchor: {PTokenEmbeddingsAnchor.typ} -- {PTokenEmbeddingsAnchor.desc}

        - output_layer: {POutputLayer.typ} -- {POutputLayer.desc}

        - output_anchor: {POutputAnchor.typ} -- {POutputAnchor.desc}

        - n_output_neurons: {PNOutputNeurons.typ} -- {PNOutputNeurons.desc}

        - n_embeddings: {PNEmbeddings.typ} -- {PNEmbeddings.desc}

        - n_tokens: {PNTokens.typ} -- {PNTokens.desc}

        - score_type: {PScoreType.typ} -- {PScoreType.desc}

        - classification_threshold: {PClassificationThreshold.typ} -- {PClassificationThreshold.desc}

        - vocab: {PVocab.typ} -- {PVocab.desc}

        - unk_token_id: {PUnkTokenId.typ} -- {PUnkTokenId.desc}

        - pad_token_id: {PPadTokenId.typ} -- {PPadTokenId.desc}

        - special_tokens: {PSpecialTokens.typ} -- {PSpecialTokens.desc}
    """
    )

    @set_model.register(user_visible=False)
    def _(self, model: Given(PModelHugsAudioClassifier)) -> str:
        # Keep this one here to catch any uses of an audio classifier that we do
        # not support so that the latter more general options don't get called.
        raise NotImplementedError("Audio classifiers are not yet supported.")

    @set_model.register
    def _(self,
          model: Given(PModelHugsTextClassifier),
          tokenizer: PTokenizerHugs,
          token_embeddings_layer: PTokenEmbeddingsLayer,
          token_embeddings_anchor: PTokenEmbeddingsAnchor,
          output_layer: POutputLayer,
          output_anchor: POutputAnchor,
          n_output_neurons: PNOutputNeurons,
          n_embeddings: PNEmbeddings,
          n_tokens: PNTokens,
          model_name: Optional(PModelName),
          vocab: PVocab,
          unk_token_id: PUnkTokenId,
          pad_token_id: PPadTokenId,
          special_tokens: PSpecialTokens,
          get_model: PGetModel,
          eval_model: PEvalModel,
          text_to_inputs: PTextToInputs,
          text_to_token_ids: PTextToTokenIds,
          text_to_spans: PTextToSpans,
          score_Type: PScoreType,
          classification_threshold: Optional(PClassificationThreshold),
          __model: PModel
         ) -> str:
        """
        Wrap a huggingface torch sequence classifier model.
        """

        print("Wrapping huggingface classifier.")

        self._reset_model()

        return model_name

    @set_model.register
    def _(self,
          model: Given(PModelTorch),
          tokenizer: PTokenizerHugs,
          token_embeddings_layer: PTokenEmbeddingsLayer,
          token_embeddings_anchor: PTokenEmbeddingsAnchor,
          output_layer: POutputLayer,
          output_anchor: POutputAnchor,
          n_output_neurons: PNOutputNeurons,
          n_embeddings: PNEmbeddings,
          n_tokens: PNTokens,
          model_name: Optional(PModelName),
          vocab: PVocab,
          unk_token_id: PUnkTokenId,
          pad_token_id: PPadTokenId,
          special_tokens: PSpecialTokens,
          get_model: PGetModel,
          eval_model: PEvalModel,
          text_to_inputs: PTextToInputs,
          text_to_token_ids: PTextToTokenIds,
          text_to_spans: PTextToSpans,
          score_Type: PScoreType,
          classification_threshold: Optional(PClassificationThreshold),
          __model: PModel
         ) -> str:
        """
        Wrap a torch module.
        """

        print("Wrapping pytorch model.")

        self._reset_model()

        return model_name

    @set_model.register(user_visible=False)
    def _(self, model: Given(PModelTF1),
          model_name: Optional(PModelName), __model: PModel) -> str:
        """
        Wrap a tensorflow 1 Graph.
        """

        raise NotImplementedError(
            "Explanations for tensorflow version 1 models are not supported."
        )

    @set_model.register
    def _(self,
          model: Given(PModelTF2),
          tokenizer: Optional(PTokenizer),
          vocab: PVocab,
          unk_token: PUnkTokenId,
          pad_token: PPadTokenId,
          text_to_inputs: PTextToInputs,
          text_to_token_ids: PTextToTokenIds,
          text_to_spans: Optional(PTextToSpans),
          get_model: Optional(PGetModel),
          eval_model: Optional(PEvalModel),
          special_tokens: Optional(PSpecialTokens),
          token_embeddings_layer: PTokenEmbeddingsLayer,
          token_embeddings_anchor: PTokenEmbeddingsAnchor,
          output_layer: POutputLayer,
          output_anchor: POutputAnchor,
          n_output_neurons: PNOutputNeurons,
          model_name: Optional(PModelName),
          n_embeddings: PNEmbeddings,
          n_tokens: PNTokens,
          score_Type: PScoreType,
          #   ds_from_source: PDSFromSource,
          __model: PModel) -> str:
        """Wrap a Tensorflow 2 Model."""
        print("Wrapping Tensorflow 2 model.")
        self._reset_model()
        return model_name

    @set_model.register(user_visible=False)
    def _(self, model: Given(PModelBlackbox),
          model_name: Optional(PModelName), __model: PModel) -> str:
        """Wrap a blackbox Callable predictor."""

        raise NotImplementedError(
            "Explanations for black-box models are not yet supported."
        )

    # This signature is only for demonstration purposes to show how errors get
    # reported to the user. Giving this one a unique name so we can look it up
    # in some unit tests.
    @set_model.register(user_visible=False)
    def set_model_debug(
        self, debug_model: Given(PDebugModel), debug_arg: PDebugArg
    ) -> str:
        """
        This is a dummy definition meant for debugging and demonstration
        purposes only.
        """

        self._reset_model()

        assert debug_model is not None
        assert debug_arg is not None

        print("set_model debug method called with:")
        print("\tdebug_model=", debug_model)
        print("\tdebug_arg=", debug_arg)

        return "lol"

    # Explanation Configuration

    @_overload
    def config(
        self,
        rebatch_size: PRebatchSize,
        ref_token: PRefToken,
        resolution: PResolution = 16,
        n_metrics_records: PNMetricsRecords = 128,
        use_training_mode: PUseTrainingMode = False,
    ) -> NoneType():
        """
        Set explanation parameters, controlling its quality, among other options.
        """
        self._reset_config()

        if ref_token is None:
            if self.wrappers.tokenizer_wrapper is not None:
                ref_token = self.wrappers.tokenizer_wrapper.pad_token
            else:
                ref_token = "[PAD]"

    config.dispatch.redoc(
        f"""
        Set explanation parameters, controlling its quality, among other options.

        Common arguments:

        - rebatch_size: {PRebatchSize.typ} -- {PRebatchSize.desc}

        - ref_token: {PRefToken.typ} -- {PRefToken.desc}

        - resolution: {PResolution} = 16 -- {PResolution.desc}

        - n_metrics_records: {PNMetricsRecords} = 128 -- {PNMetricsRecords.desc}

        - use_training_mode: {PUseTrainingMode} = False - {PUseTrainingMode.desc}
    """
    )

    # Tokenizer Wrappers

    @_overload(user_visible=False)
    def set_tokenizer(self, tokenizer: Given(PTokenizerWrapper)) -> NoneType():
        """
        Use existing tokenizer wrapper.
        """

        self._reset_tokenizer()
        # Save tokenizer in self.state and use later.

    @set_tokenizer.register(user_visible=False)
    def _(
        self,
        tokenizer: Given(PTokenizerHugs)
    ) -> NoneType():
        """
        Wrap a huggingface tokenizer.
        """

        self._reset_tokenizer()

        # TODO: these two tokenizers have slightly different methods
        # batch_encode vs. batch_encode_plus

        raise NotImplementedError()

    # Data Wrappers

    @_overload(user_visible=False)
    def set_data(
        self, data: Given(PSplitLoadWrapper), data_split_name: PDataSplitName,
        __metadata: Optional(PMetaPandas), __n_records: PNRecords
    ) -> str:
        """
        Load instances using an existing split load wrapper.
        """

        self._reset_data()
        # Wrapper gets saved in self.state and used in self._build_wrappers.

        return data_split_name

    set_data.dispatch.redoc(
        f"""
    Specify data to be explained.

    Common arguments:

    - data_split_name: {PDataSplitName.typ} -- {PDataSplitName.desc}

    - data: type varies -- source of data; additional arguments may be necessary.

    - label(s): type varies -- source of labels (if not part of `data`); additional arguments may be necessary.

    - metadata: type varies -- source of metadata
    """
    )

    @set_data.register
    def _(
        self,
        data: Given(PDataInstance),
        label: PLabelInstance,
        data_split_name: PDataSplitName,
        __metadata: Optional(PMetaPandas),
        __n_records: PNRecords,
        __ds_from_source: PDSFromSource,
        __standardize_databatch: PStandardizeDatabatch
    ) -> str:
        """
        Load a single string.
        """

        self._reset_data()

        return data_split_name

    @set_data.register
    def _(
        self,
        data: Given(PDataPandas),
        text_field: PFieldText,
        label_field: Optional(PFieldLabel),
        meta_fields: Optional(PFieldsMeta),
        data_split_name: PDataSplitName,
        __metadata: Optional(PMetaPandas),
        __n_records: PNRecords,
        __ds_from_source: PDSFromSource,
        __standardize_databatch: PStandardizeDatabatch
    ) -> str:
        """
        Load instances from a pandas DataFrame. The given DataFrame must contain
        text inputs and optionally labels.
        """

        self._reset_data()

        return data_split_name

    @set_data.register
    def _(
        self,
        data: Given(PDataTorchDataLoader),
        text_field: PFieldText,
        label_field: Optional(PFieldLabel),
        meta_fields: Optional(PFieldsMeta),
        data_split_name: PDataSplitName,
        __metadata: Optional(PMetaPandas),
        __n_records: PNRecords,
        __ds_from_source: PDSFromSource,
        __standardize_databatch: PStandardizeDatabatch
    ) -> str:
        """
        Load instances from a pytorch DataLoader. Assumes wrapped dataset is a
        mapping from column names to iterables of text and labels.
        """

        self._reset_data()

        return data_split_name

    # Not strictly necessary given them more general iterable type but keeping
    # this here for user-facing documentation purposes.
    @set_data.register
    def _(
        self,
        data: Given(PDataSequence),
        labels: PLabelsSequence,
        metadata: Optional(PMetaPandas),
        data_split_name: PDataSplitName,
        __n_records: PNRecords,
        __ds_from_source: PDSFromSource,
        __standardize_databatch: PStandardizeDatabatch
    ) -> str:
        """
        Load instances from an iterable.
        """

        self._reset_data()

        return data_split_name

    @set_data.register
    def _(
        self,
        data: Given(PDataIterable),  # most general type here
        labels: PLabelsIterable,
        metadata: Optional(PMetaPandas),
        data_split_name: PDataSplitName,
        __n_records: PNRecords,
        __ds_from_source: PDSFromSource,
        __standardize_databatch: PStandardizeDatabatch
    ) -> str:
        """
        Load instances from an iterable.
        """

        self._reset_data()

        return data_split_name
