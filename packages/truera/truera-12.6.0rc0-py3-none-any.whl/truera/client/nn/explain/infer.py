"""
Helpers for inferring wrapper parameters. Putting all of the logic here so that
the dispatch in quick.py does not grow too big.
"""

import dataclasses
from inspect import BoundArguments
from inspect import Signature
import os
import random
import re
import sys
import tempfile
import typing
from typing import Callable, Iterable, Mapping
from typing import Optional as TOptional

import numpy as np
from pandas import DataFrame

from truera.client.nn.client_configs import LayerAnchor
from truera.client.nn.explain.parameters import PBlackboxTokenizer
from truera.client.nn.explain.parameters import PDataCollectionName
from truera.client.nn.explain.parameters import PDataInstance
from truera.client.nn.explain.parameters import PDataIterable
from truera.client.nn.explain.parameters import PDataPandas
from truera.client.nn.explain.parameters import PDataSequence
from truera.client.nn.explain.parameters import PDataSplitName
from truera.client.nn.explain.parameters import PDataTorchColumnwise
from truera.client.nn.explain.parameters import PDataTorchDataLoader
from truera.client.nn.explain.parameters import PDebugArg
from truera.client.nn.explain.parameters import PDebugInfer
from truera.client.nn.explain.parameters import PDebugModel
from truera.client.nn.explain.parameters import PDSFromSource
from truera.client.nn.explain.parameters import PEvalModel
from truera.client.nn.explain.parameters import PFieldLabel
from truera.client.nn.explain.parameters import PFieldsMeta
from truera.client.nn.explain.parameters import PFieldText
from truera.client.nn.explain.parameters import PGetModel
from truera.client.nn.explain.parameters import PHugsModelName
from truera.client.nn.explain.parameters import \
    PKerasTextVectorizationTokenizer
from truera.client.nn.explain.parameters import PLabelInstance
from truera.client.nn.explain.parameters import PLabelsIterable
from truera.client.nn.explain.parameters import PLabelsSequence
from truera.client.nn.explain.parameters import PMetaPandas
from truera.client.nn.explain.parameters import PModel
from truera.client.nn.explain.parameters import PModelHugsBase
from truera.client.nn.explain.parameters import PModelLoadWrapper
from truera.client.nn.explain.parameters import PModelName
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
from truera.client.nn.explain.parameters import PScoreType
from truera.client.nn.explain.parameters import PSpecialTokens
from truera.client.nn.explain.parameters import PSplitLoadWrapper
from truera.client.nn.explain.parameters import PStandardizeDatabatch
from truera.client.nn.explain.parameters import PTextToInputs
from truera.client.nn.explain.parameters import PTextToSpans
from truera.client.nn.explain.parameters import PTextToTokenIds
from truera.client.nn.explain.parameters import PTF2Tokenizer
from truera.client.nn.explain.parameters import PTFTextTokenizer
from truera.client.nn.explain.parameters import PTFTextTokenizerWithOffsets
from truera.client.nn.explain.parameters import PTokenEmbeddingsAnchor
from truera.client.nn.explain.parameters import PTokenEmbeddingsLayer
from truera.client.nn.explain.parameters import PTokenizer
from truera.client.nn.explain.parameters import PTokenizerHugs
from truera.client.nn.explain.parameters import PTokenizerWrapper
from truera.client.nn.explain.parameters import PTokenWordPrefix
from truera.client.nn.explain.parameters import PTrulensWrapper
from truera.client.nn.explain.parameters import PUnkTokenId
from truera.client.nn.explain.parameters import PVocab
from truera.client.nn.explain.psys import Backtrack
from truera.client.nn.explain.psys import InferException
from truera.client.nn.explain.psys import NoBacktrack
from truera.client.nn.explain.psys import Rules
from truera.client.nn.explain.psys import State
from truera.client.nn.wrappers import nlp as nlp
from truera.client.nn.wrappers.tf import import_tf
from truera.client.util.debug import retab
from truera.client.util.iter_utils import LenIterable
from truera.client.util.overload import BindingsHook
from truera.client.util.pandas_utils import is_integer_dtype
from truera.client.util.pandas_utils import is_string_dtype
from truera.client.util.python_utils import CodeMapper
from truera.client.util.python_utils import copy_bindings
from truera.client.util.python_utils import import_optional

# TODO(piotrm): remaining wrapping issues with some huggingface models:
# model loading problems
#   - layoutlm-base-uncased
# "not a string" error ???
#   - google/reformer-enwik8
# non-fast tokenizer gets loaded even if fast is available
#   - many examples, see quick_test_results.ipynb
# "object of type 'NoneType' has no len()"
#   - google.tapas-* models

trulens_nn_backend = import_optional(
    "trulens.nn.backend", "neural networks explanations"
)
trulens_nn_models = import_optional(
    "trulens.nn.models", "neural networks explanations"
)

transformers = import_optional("transformers", "huggingface model wrapping")

rules = Rules()


def derive_defaults(
    state_factory: TOptional[Callable[[BoundArguments], State]] = None
):
    """
    Create a post-bind hook for overload that infers `Parameter` arguments that
    have their default value. 
    
    - `state_factory` may be provided and will be called to produce a `State`
      with existing parameters if needed; it gets called with bindings of the
      functions whose defaults are being derived, before the derivations happen.
    """

    # TODO(piotrm): incorporate accumulated inference warnings as was done in
    # the overload-based version.

    # Caller's globals are required if __future__.annotation is enabled to be
    # able to evaluate names to types.
    # _globals = caller_globals()

    hook: BindingsHook

    def hook(
        acc: State, func: Callable, sig: Signature, bindings: BoundArguments
    ) -> Iterable[BoundArguments]:
        """
        Infers Parameter arguments from inference rules. This is called in
        overload.py::sig_bind().

        Arguments:
        
        - acc: State -- "accumulator" passed between each hook. In this case it
          a state. We need it here to provide existing parameters to rules.bind
          . Infer defaults is assumed to be the first in the chain that produces
          a state and it will get passed along to subsequent hooks.

        - func: Callable -- the method whose bindings we are processing.

        - sig: Signature -- the signature of the above function.

        - bindings: BoundArguments -- and its already-bound arguments before we
          get to inferring better defaults.
        """

        infer_bindings = copy_bindings(bindings)
        infer_bindings.apply_defaults()

        if state_factory is not None:
            state = state_factory(bindings)
        else:
            state = State({})

        for state, bindings in rules.bind(
            func,
            state,
            args=infer_bindings.args,
            kwargs=infer_bindings.kwargs,
            trace=[]
        ):
            # TODO: returning only the first possible binding, what if the first
            # one fails downstream?

            return state, bindings

        raise Exception(f"Could not infer optional arguments.")

    return hook


def gen_name(base: str, name: TOptional[str] = None):
    if name is not None:
        return name

    return f"__{base}__{nonce()}"


def nonce() -> str:
    return str(random.randint(0, sys.maxsize))


@rules.register_rules
class Inferences:
    # Internal uses.

    @staticmethod
    def trulens_wrapper_pytorch(model: PModelTorch) -> PTrulensWrapper:
        # backend = trulens_nn_backend.get_backend(trulens_nn_backend.Backend.PYTORCH)

        # TODO(piotrm): let backend below take in a backend instead of string or
        # at least verify the input type
        return trulens_nn_models.get_model_wrapper(model, backend="pytorch")

    @staticmethod
    def trulens_wrapper(model: PModel) -> PTrulensWrapper:
        return trulens_nn_models.get_model_wrapper(model)

    # Managed workspaces related.

    @staticmethod
    def default_score_type() -> PScoreType:
        # verify_nn_wrappers will fail for negative scores with models set up as probit outputing
        return "probits"  # TODO: determine this? shouldn't matter once we decouple the tru workspace.

    @staticmethod
    def model_name_random() -> PModelName:
        """Generate a random model name."""

        return gen_name("model")

    @staticmethod
    def project_name() -> PProjectName:
        """Generate a random project name."""

        return gen_name("project")

    @staticmethod
    def data_split_name() -> PDataSplitName:
        """Generate a random data split name."""

        return gen_name("data_split")

    @staticmethod
    def data_collection_name() -> PDataCollectionName:
        """Generate a random data collection name."""

        return gen_name("data_collection")

    # Model architecture related.

    @staticmethod
    def model_pytorch_of_model(model: PModel) -> PModelTorch:
        # Note that this is required since huggingface models can be both tf and pytorch.
        if isinstance(model, PModelTorch):
            return model
        else:
            raise Backtrack("Not a pytorch model.")

    @staticmethod
    def model_tensorflow2_of_model(model: PModel) -> PModelTF2:
        # Note that this is required since huggingface models can be both tf and pytorch.
        if isinstance(model, PModelTF2):
            return model
        else:
            raise Backtrack("Not a tensorflow 2 model.")

    @staticmethod
    def keras_tokenizer_of_tokenizer(
        tokenizer: PTokenizer
    ) -> PKerasTextVectorizationTokenizer:
        if isinstance(tokenizer, PKerasTextVectorizationTokenizer):
            return tokenizer
        else:
            raise Backtrack("Not a Keras Text Vectorization Tokenizer.")

    @staticmethod
    def tf2_tokenizer_of_tokenizer(tokenizer: PTokenizer) -> PTF2Tokenizer:
        if isinstance(tokenizer, PTF2Tokenizer):
            return tokenizer
        else:
            raise Backtrack("Not a TF2 Tokenizer.")

    @staticmethod
    def vocab_from_keras_tokenizer(tokenizer: PTF2Tokenizer) -> PVocab:
        """TFHub BERT Encoder stores vocabulary on disk. This rule tries finding the path and reading it there"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                tokenizer.save(tmp_dir)
                vocab_file = f'{tmp_dir}/assets/vocab.txt'
            except:
                raise Backtrack("Unable to infer vocab from tokenizer")
            else:
                if not os.path.isfile(vocab_file):
                    raise Backtrack("Unable to infer vocab from tokenizer")
            with open(vocab_file) as f:
                return {v: i for i, v in enumerate(f.read().splitlines())}

    @staticmethod
    def vocab_from_keras_tokenizer_nodes(tokenizer: PTF2Tokenizer) -> PVocab:
        """TFHub BERT Encoder stores vocabulary on disk. This rule tries finding the path and reading it there"""
        try:
            encoder = tokenizer.outbound_nodes[-1].layer
            vocab_path = encoder.resolved_object.vocab_file.asset_path.numpy(
            ).decode("utf-8")
            assert vocab_path and os.path.isfile(vocab_path)
            with open(vocab_path, "r") as f:
                return {v: i for i, v in enumerate(f.read().splitlines())}
        except:
            raise Backtrack("Unable to infer vocab from tokenizer")

    @staticmethod
    def n_tokens_from_wrapper(trulens_wrapper: PTrulensWrapper) -> PNTokens:
        for _, layer in trulens_wrapper._layers.items():
            try:
                seq_length = layer._arguments['seq_length']
                assert isinstance(seq_length, int) and seq_length > 0
                return seq_length
            except:
                continue

        raise Backtrack("Unable to infer n_tokens")

    @staticmethod
    def n_embeddings(
        token_embeddings_layer: PTokenEmbeddingsLayer,
        trulens_wrapper: PTrulensWrapper
    ) -> PNEmbeddings:
        embedding = trulens_wrapper._layers[token_embeddings_layer]

        if hasattr(embedding, "embedding_dim"):
            # most huggingface models
            return embedding.embedding_dim

        if hasattr(embedding, "dim"):
            # ibert.QuantEmbedding saves embedding_dim in the dim field
            return embedding.dim

        if hasattr(embedding, "normalized_shape"):
            # if layer is LayerNorm, this may work
            return embedding.normalized_shape[0]

        if hasattr(embedding, "output_dim"):
            # keras.layers.Embedding
            return embedding.output_dim

        if hasattr(embedding, "output"):
            # Keras OnDeviceEmbeddings
            return embedding.output.shape[-1]

        # TODO: Add verification for this. MLNN-508
        # TODO: check that embedding is of the right type
        raise Backtrack("Unable to infer n_embeddings")

    @staticmethod
    def classification_output_layer(
        model: PModelTorch, trulens_wrapper: PTrulensWrapper
    ) -> (POutputLayer, POutputAnchor):
        """
        If the given pytorch model is a classifier, guess its output layer name.
        """

        #if isinstance(model, PModelHugsBase): # this test does not work as intended
        # This message might be more informative if user gives a base hugs
        # model (does not have a classification layer).
        #    raise NoBacktrack(
        #        "The given model is a huggingface base model (feature extractor). "
        #        "Presently only classification models are supported. "
        #        "Either use a huggingface classifier (ends in 'ForSequenceClassification`) or wrap the base model with a classification layer."
        #    )

        layer_names = list(reversed(trulens_wrapper._layers.keys()))

        # TODO: Move this to somewhere else.
        common_names = [
            "classifier",
            "classifier_out_proj",
            "classifier_linear_out",
            "classification_head_out_proj",
            "score",
            "perceiver_decoder_decoder_final_layer",
            "logits_proj",
            "sequence_summary_summary"  # e.g. FlaubertForSequenceClassification
        ]

        found_names = [name for name in common_names if name in layer_names]

        if len(found_names) == 0:
            print(
                f"WARNING: Did not infer output by common names. Instead using the last layer: {layer_names[0]}. "
                "If this is incorrect, Please specify the correct one using the `output_layer` argument."
            )
            return layer_names[0], LayerAnchor.OUT

        elif len(found_names) > 1:
            raise Backtrack(
                f"More than one layer found that could be the classifier output: {found_names}."
                f"Please specify the correct one in the `output_layer` parameter. "
                f"The layers are:\n" + retab("\n".join(layer_names), tab="\t")
            )
        else:
            return found_names[0], LayerAnchor.OUT

    @staticmethod
    def output_layer(trulens_wrapper: PTrulensWrapper) -> POutputLayer:
        return list(trulens_wrapper._layers.keys())[-1]

    @staticmethod
    def output_anchor(layer: POutputLayer) -> POutputAnchor:
        print(f"WARNING: Guessing that output anchor (for {layer}) is 'out'.")
        return LayerAnchor.OUT

    @staticmethod
    def token_embeddings_layer(
        model: PModelTorch, trulens_wrapper: PTrulensWrapper
    ) -> (PTokenEmbeddingsLayer, PTokenEmbeddingsAnchor):
        """
        Guess embedding layer from layer name in a pytorch model.
        """

        layer_names = trulens_wrapper._layers.keys()

        # The following names cover most huggingface text classifiers.
        r_token_embeddings_layer_name = re.compile(
            r"|".join(
                [
                    r".+_word_embeddings",
                    r".*transformer_word_emb",  # e.g. TransfoXLForSequenceClassification
                    # TODO(piotrm): check if appropriate
                    r".+(?<!decoder)_embed_tokens",
                    r".+_wte",  # "word token embedding" maybe?
                    r".*transformer_w",  # "word embedding" maybe?
                    r".*transformer_embeddings",
                    # TODO(piotrm): check if appropriate
                    r".*transformer_embeddings_dropout",
                    r".+_tokens_embed",  # e.g. OpenAIGPTForSequenceClassification
                    r".+_preprocessor_embeddings",  # e.g. PerceiverForSequenceClassification
                    r".*word_emb_emb_layers_0",  # e.g. transfo-xl-wt103
                    r".*canine_char_embeddings_LayerNorm",  # .e.g. google/canine-s
                ]
            )
        )

        # TODO(piotrm):
        # - facebook/opt-6.7b has decoder_embed_tokens without encoder_embed_tokens
        # - some models have both of these, leading to error:
        #   ['transformer_embeddings_word_embeddings', 'transformer_embeddings_dropout']
        # -

        candidates = list(
            filter(r_token_embeddings_layer_name.fullmatch, layer_names)
        )

        if len(candidates) == 0:
            # Try less certain ones
            r_token_embeddings_layer_name = re.compile(
                r"|".join([
                    r".*embed.*",
                ])
            )
            # TODO: Is is possible to infer this by layer size if its the first
            # layer? Maybe via trulens when the intervention is called.
            candidates = list(
                filter(r_token_embeddings_layer_name.fullmatch, layer_names)
            )
            if len(candidates) == 0:
                raise Backtrack(
                    "No layers with name hinting at token/word embedding found. "
                    "Please specify one using the `token_embeddings_layer` argument. "
                    "Layers are:\n" + retab("\n".join(layer_names), tab="\t")
                )
            elif len(candidates) == 1:
                print(
                    f"WARNING: Used a soft match on term embed to find the layer: {candidates}. "
                    "If this is incorrect, Please specify the correct one using the `token_embeddings_layer` argument."
                )

        if len(candidates) > 1:
            raise Backtrack(
                f"More than one layer with expected name found: {candidates}. "
                "Please specify the correct one using the `token_embeddings_layer` argument."
            )

        return candidates[0], LayerAnchor.OUT

    @staticmethod
    def token_embeddings_anchor(
        layer: PTokenEmbeddingsLayer
    ) -> PTokenEmbeddingsAnchor:
        print(
            f"WARNING: Guessing that embedding layer anchor (for {layer}) is 'out'."
        )
        return LayerAnchor.OUT

    @staticmethod
    def n_output_neurons_torch(
        model: PModelTorch, output_layer: POutputLayer,
        trulens_wrapper: PTrulensWrapper
    ) -> PNOutputNeurons:
        """
        Guess the number of output neurons in a pytorch classifier.
        """

        output = trulens_wrapper._layers[output_layer]

        # TODO: handle Identity, Dropout, Tanh???

        # TODO: check that layer is of the right type
        if hasattr(output, "out_features"):
            return output.out_features

        if hasattr(model, "num_labels"):
            return model.num_labels

        # TODO: Infer this from the predict operation.
        # TODO: Add verification for this. MLNN-508
        temp = Backtrack(
            f"Layer type {type(output)} does not specify the output dimension. "
            f"Please specify the correct one using the `n_output_neurons` argument. "
        )
        print(f"WARNING: {temp.msg}")

        raise temp

    @staticmethod
    def n_output_neurons_tf2(
        model: PModelTF2, output_layer: POutputLayer,
        trulens_wrapper: PTrulensWrapper
    ) -> PNOutputNeurons:
        """
        Guess the number of output neurons in a keras classifier.
        """

        output = trulens_wrapper._layers[output_layer]

        # TODO: handle Identity, Dropout, Tanh???

        # TODO: check that layer is of the right type
        if hasattr(output, "output_shape"):
            return output.output_shape[-1]

        if hasattr(model, "output_shape"):
            return model.output_shape[-1]

        # TODO: Infer this from the predict operation.
        # TODO: Add verification for this. MLNN-508
        temp = Backtrack(
            f"Layer type {type(output)} does not specify the output dimension. "
            f"Please specify the correct one using the `n_output_neurons` argument. "
        )
        print(f"WARNING: {temp.msg}")

        raise temp

    ## Autowrap model related requirements.

    @staticmethod
    def model_from_wrapper(wrapper: PModelLoadWrapper) -> PModel:
        return wrapper.get_model()

    # NOTE(piotrm->corey): without automatic "infer by stronger", things like
    # this will be required:
    @staticmethod
    def torch_model_is_model(model: PModelTorch) -> PModel:
        return model

    @staticmethod
    def tf2_model_is_model(model: PModelTF2) -> PModel:
        return model

    @staticmethod
    def tf1_model_is_model(model: PModelTF1) -> PModel:
        return model

    @staticmethod
    def get_model(model: PModel) -> PGetModel:
        """
        Default `get_model`.
        """

        def default_get_model(_):

            return model

        default_get_model.__doc__ = f"Default `get_model` implementation for {model}."

        return default_get_model

    @staticmethod
    def _probits_of_pytorch_output(output):

        import torch

        if isinstance(output, torch.Tensor):
            # TODO: better way to check if output is probits

            if output.shape[1] == 1:
                probit_fn, probit_fn_name = torch.nn.functional.sigmoid, "sigmoid"
            else:
                probit_fn, probit_fn_name = torch.nn.functional.softmax, "softmax"

            if probit_fn_name in output.grad_fn.__class__.__name__.lower():
                temp = output
            else:
                print(
                    f"WARNING: Cannot tell whether model output is in probits or logits, wrapping it in {probit_fn_name}."
                )

                temp = probit_fn(output)

        else:
            # For other output structures, check if they have some common keys indicating probits/logits.

            if isinstance(output, Mapping):
                d = output
            else:
                # handles torch's SequenceClassifierOutput
                d = dir(output)

            if "probits" in d and isinstance(d['probits'], torch.Tensor):
                temp = d['probits']

            elif "logits" in d and isinstance(d['logits'], torch.Tensor):
                temp = torch.nn.functional.softmax(d['logits'])

            else:
                raise RuntimeError(
                    f"Could not determine output tensor in output structure of type {type(output)}. "
                    f"You may need to provide the `eval_model` parameter."
                )

        return temp

    @staticmethod
    def pytorch_eval_model(model: PModelTorch) -> PEvalModel:
        """
        Default `eval_model` for pytorch models.
        """

        def inferred_eval_model(model, args, kwargs):
            output = model(*args, **kwargs)

            return Inferences._probits_of_pytorch_output(output).float().detach(
            ).cpu().numpy()

        inferred_eval_model.__doc__ = f"Default implementation of `eval_model` for pytorch model {model}."

        return inferred_eval_model

    @staticmethod
    def tf2_eval_model(model: PModelTF2) -> PEvalModel:
        """
        Default `eval_model` for tensorflow 2 models.
        """

        def inferred_eval_model(model, args, kwargs):
            return model(*args, **kwargs).numpy()

        inferred_eval_model.__doc__ = f"Default implementation of `eval_model` for tensorflow 2 model {model}."

        return inferred_eval_model

    ## Huggingface models related.

    @staticmethod
    def huggingface_model_name(model: PModelHugsBase) -> PHugsModelName:
        model_name = model.name_or_path
        # TODO: what if it is path?

        if model_name is None or model_name == "":
            raise Backtrack("Got a blank name from model.")

        return model_name

    @staticmethod
    def model_name_from_hugs(
        huggingface_model_name: PHugsModelName
    ) -> PModelName:
        """
        Use huggingface model name as workspace model name.
        """

        return huggingface_model_name

    @staticmethod
    def basehugs_model_from_torch(model: PModelTorch) -> PModelHugsBase:
        """
        Get the huggingface classifier from within a pytorch module.
        """

        # If model already is a huggingface classifier, return as is.
        # TODO(piotrm): allow this to be done automatically in psys.get ?
        if isinstance(model, PModelHugsBase):
            return model

        emb_hugs = [
            layer for layer in model.children()
            if isinstance(layer, PModelHugsBase)
        ]

        if len(emb_hugs) == 1:
            return emb_hugs[0]
        elif len(emb_hugs) > 1:
            raise Backtrack("More than one huggingface layer in model.")
        else:
            raise Backtrack(
                "Given pytorch model is not a huggingface base model nor does it embed one."
            )

    #@staticmethod
    #def huggingface_model_from_name(
    #    huggingface_model_name: PHugsModelName
    #) -> PModelHugsClassifier:
    #    """Get a huggingface model from its name."""
    #    print(f"Load huggingface model by name: {huggingface_model_name}.")

    #    transformers = import_optional(
    #        "transformers", "huggingface model wrapping"
    #    )
    #    model = transformers.AutoModelForSequenceClassification.from_pretrained(
    #        huggingface_model_name
    #    )
    #    return model

    # Tokenizer related

    @staticmethod
    def tokenizer_wrapper_params(
        tok: PTokenizerWrapper
    ) -> (PNTokens, PVocab, PUnkTokenId, PPadTokenId, PSpecialTokens):
        """
        Get tokenizer parameters from a tokenizer wrapper.
        """

        return (
            tok.n_tokens, tok.vocab, tok.unk_token_id, tok.pad_token_id,
            tok.special_tokens
        )

    @staticmethod
    def tokenizer_from_huggingface(
        huggingface_model_name: PHugsModelName
    ) -> PTokenizerHugs:
        """
        Get a huggingface tokenizer if it is bundled with a model of the same name.
        """

        print(f"Getting tokenizer from model: {huggingface_model_name}")

        # TODO: Wav2Vec2CTCTokenizer fails to load
        # TODO: ESMTokenizer might have been renamed

        tok = transformers.AutoTokenizer.from_pretrained(
            huggingface_model_name, use_fast=True
        )

        if not isinstance(tok, transformers.PreTrainedTokenizerFast):
            raise Backtrack("Fast huggingface tokenizer is not available.")

        return tok

    @staticmethod
    def n_tokens_from_huggingface_tokenizer(
        tokenizer: PTokenizerHugs
    ) -> PNTokens:
        """
        Use huggingface tokenizer's `model_max_length` as `n_tokens`.
        """

        n_tokens = tokenizer.model_max_length

        print(
            f"WARNING: using default n_tokens={n_tokens} for tokenizer {tokenizer}."
        )

        if n_tokens > 128:
            print(
                f"WARNING: n_tokens={n_tokens} is very large, reducing to 128."
            )
            n_tokens = 128

        return n_tokens

    @staticmethod
    def unk_token_id_hugs(tokenizer: PTokenizerHugs) -> PUnkTokenId:
        return tokenizer.unk_token_id

    @staticmethod
    def pad_token_id_hugs(tokenizer: PTokenizerHugs) -> PPadTokenId:
        return tokenizer.pad_token_id

    @staticmethod
    def special_tokens(tokenizer: PTokenizerHugs) -> PSpecialTokens:
        return list(tokenizer.all_special_ids)

    # NOTE(piotrm): started to figure out how to get the new word token prefix
    # below but realized I don't yet need it for the models I'm testing with.
    # Keeping the progress here since it will likely come up for some models.
    """
    @staticmethod
    def token_word_prefix(tokenizer: PTokenizerHugs) -> PTokenWordPrefix:
        enc1 = np.array(tokenizer.encode("good"))
        enc2 = np.array(tokenizer.encode(" good"))
        diffs = np.argwhere(enc1 != enc2)

        if len(diffs) == 0:
            return None
        elif len(diffs) == 1:
            tok1 = enc1[diffs[0][0]]
            tok2 = enc2[diffs[0][0]]

            word1 = tokenizer.decode(tok1)
            word2 = tokenizer.decode(tok2)

            # TODO: continue here
    """

    @staticmethod
    def vocab(tokenizer: PTokenizerHugs) -> PVocab:
        seen_vocab = dict([])

        def rep_prefix(k, id):
            # Replace a prefix, here only " " with "_" to make it more readable.
            # Note that we expect to use tokenizer.decode(tok_id) which
            # typically returns space prefix instead of the special prefix
            # indicators like "Ġ" or "##".

            ret = k
            if len(ret) >= 1 and ret[0] == " ":
                ret = "_" + ret[1:]

            if ret in seen_vocab:
                print(
                    f"WARNING: Could not standardize vocabulary: token "
                    f"'{seen_vocab[ret]}' and '{k}' would be ambiguous as "
                    f"{ret}, adding token_id={id} indicator to disambiguate."
                )
                ret = ret + "({id})"
            else:
                seen_vocab[ret] = k

            return ret

        if hasattr(tokenizer, "vocab_size"):
            token_ids = list(range(tokenizer.vocab_size))
            return {
                rep_prefix(tokenizer.decode(token_id), token_id): token_id
                for token_id in token_ids
            }

        else:
            raise Backtrack(
                f"Could not get vocabulary from tokenizer {tokenizer}."
            )

    @staticmethod
    def vocab_keras_textvectorizer(
        tokenizer: PKerasTextVectorizationTokenizer
    ) -> PVocab:
        return {tok: i for i, tok in enumerate(tokenizer.get_vocabulary())}

    @staticmethod
    def search_vocab_for_special_tokens(vocab: PVocab) -> PSpecialTokens:
        common_wrappings = [
            "[{}]",
            "<{}>",
            "({})"
            "{{{}}}",
            "{}",
        ]
        common_special_tokens = ["MASK", "RANDOM", "CLS", "SEP"]

        for wrapping in common_wrappings:
            special_tokens = [
                wrapping.format(tok) for tok in common_special_tokens
            ]
            special_token_ids = [
                vocab[tok] for tok in special_tokens if tok in vocab
            ]
            if len(special_token_ids):
                return special_token_ids
        return []

    @staticmethod
    def search_vocab_for_unk(vocab: PVocab) -> PUnkTokenId:
        common_wrappings = [
            "[{}]",
            "<{}>",
            "({})"
            "{{{}}}",
            "{}",
        ]
        for wrapping in common_wrappings:
            for unk in ["UNK", 'unk']:
                unk_tok = wrapping.format(unk)
                if unk_tok in vocab:
                    return vocab[unk_tok]

        raise Backtrack(f"Could not find UNK token ID in vocab.")

    @staticmethod
    def search_vocab_for_pad(vocab: PVocab) -> PPadTokenId:
        common_wrappings = [
            "[{}]",
            "<{}>",
            "({})"
            "{{{}}}",
            "{}",
        ]
        for wrapping in common_wrappings:
            for pad in ["PAD", 'pad']:
                pad_tok = wrapping.format(pad)
                if pad_tok in vocab:
                    return vocab[pad_tok]

        raise Backtrack(f"Could not find PAD token ID in vocab.")

    ## Autowrap tokenizer-related requirements

    @staticmethod
    def text_to_inputs(
        tokenizer: PTokenizerHugs, n_tokens: PNTokens
    ) -> PTextToInputs:
        """
        Default input constructor for huggingface models given their tokenizers.
        """

        tok_args = dict(
            padding='max_length', max_length=n_tokens, truncation=True
        )

        def default_text_to_inputs(texts):
            from truera.client.nn.wrappers.torch import Torch
            """Default implementation of text_to_inputs."""
            return dict(
                args=[],
                kwargs=dict(
                    tokenizer.batch_encode_plus(
                        list(texts),
                        return_tensors="pt",  # model eval needs pytorch tensors
                        **tok_args
                    ).to(Torch.get_device())
                )
            )

        return default_text_to_inputs

    @staticmethod
    def text_to_token_ids(
        tokenizer: PTokenizerHugs, n_tokens: PNTokens
    ) -> PTextToTokenIds:
        """
        Default token_ids extractor for huggingface models given their tokenizers.
        """

        tok_args = dict(
            padding='max_length', max_length=n_tokens, truncation=True
        )

        def default_text_to_token_ids(texts):
            """Default implementation of text_to_token_ids."""

            return tokenizer.batch_encode_plus(
                list(texts),
                return_tensors='np',  # truera wants numpy tensors instead
                **tok_args
            )['input_ids']

        return default_text_to_token_ids

    @staticmethod
    def text_to_inputs_tf(
        tokenizer: PTokenizer, model: PModelTF2
    ) -> PTextToInputs:
        """
        Default input constructor for tensorflow models.
        """

        tf = import_tf(version=2)

        if model.input.dtype == tf.string:
            # Input is raw text
            def default_text_to_inputs(texts):
                """Default implementation of text_to_inputs."""
                return {"args": [tf.constant(list(texts))], "kwargs": {}}

        else:
            # Input may be tokenized text
            def default_text_to_inputs(texts):
                """Default implementation of text_to_inputs."""
                return {
                    "args": [tokenizer(tf.constant(list(texts)))],
                    "kwargs": {}
                }

        return default_text_to_inputs

    @staticmethod
    def text_to_token_ids_tftext(
        tokenizer: PTokenizer, model: PModelTF2
    ) -> PTextToTokenIds:
        """
        Default token_ids extractor for tf text tokenizers.
        """
        tf = import_tf(version=2)

        def default_text_to_token_ids(texts):
            """Default implementation of text_to_token_ids."""
            out = tokenizer(tf.constant(list(texts)))
            if isinstance(out, dict):
                return out["input_word_ids"].numpy()
            else:
                return out.numpy()

        return default_text_to_token_ids

    @staticmethod
    def text_to_token_ids_blackbox(
        tokenizer: PBlackboxTokenizer,
    ) -> PTextToTokenIds:
        """
        Default token_ids extractor for tf text tokenizers.
        """

        def default_text_to_token_ids(texts):
            """Default implementation of text_to_token_ids."""

            return tokenizer(list(texts))

        return default_text_to_token_ids

    @staticmethod
    def text_to_spans(
        tokenizer: PTokenizerHugs, n_tokens: PNTokens
    ) -> PTextToSpans:
        tok_args = dict(
            padding='max_length', max_length=n_tokens, truncation=True
        )
        """
        Default spans extractor for huggingface models given their tokenizers.
        """

        def default_text_to_spans(texts):
            """Default implementation of text_to_spans."""
            return tokenizer.batch_encode_plus(
                list(texts),
                return_tensors='np',
                return_offsets_mapping=True,
                **tok_args
            )['offset_mapping']

        return default_text_to_spans

    @staticmethod
    def text_to_spans_tftext(
        tokenizer: PTFTextTokenizerWithOffsets
    ) -> PTextToSpans:
        """
        Default spans extractor for TF Text tokenizers with offsets.
        """

        def default_text_to_spans(texts):
            """Default implementation of text_to_spans."""
            _, starts, ends = tokenizer.tokenize_with_offsets(list(texts))
            return np.array(list(zip(starts.numpy(), ends.numpy())))

        return default_text_to_spans

    # Data related

    @staticmethod
    def labels_of_instance(label: PLabelInstance) -> PLabelsSequence:
        return [label]

    # NOTE1: The LogicalType system cannot determine subclass relationships
    # involving special type aliases of `typing.*` "types". Due to this, you
    # might need to include some rules to guide inference without needing
    # subclass checks. For example, a `typing.Sequence` is an `typing.Iterable`
    # but a subclass check like this is beyond capabilities of LogicalType so
    # you need to provide a rule annotated as producing an iterable given a
    # sequence.

    # NOTE1
    #@staticmethod
    #def dataiterable_of_datasequence(data: PDataSequence) -> PDataIterable:
    #    return iter(data)

    # NOTE1
    # @staticmethod
    #def labeliterable_of_labelsequence(
    #    labels: PLabelsSequence
    #) -> PLabelsIterable:
    #    return iter(labels)

    @staticmethod
    def datasequence_of_datainstance(data: PDataInstance) -> PDataSequence:
        return [data]

    # NOTE2: strings get matched by Sequences and Iterables causing bugs.
    @staticmethod
    def n_records_of_datasequence(data: PDataSequence) -> PNRecords:
        if isinstance(data, str):  #  NOTE2
            raise Backtrack("Data was a single instance.")

        if len(data) == 0:
            raise NoBacktrack(f"Data sequence had zero length: {data}")

        return len(data)

    @staticmethod
    def n_records_of_split_load_wrapperd(
        wrapper: PSplitLoadWrapper
    ) -> PNRecords:
        dat: LenIterable = wrapper.get_ds()

        return dat.flat_len

    ## Pandas

    @staticmethod
    def meta_of_pandas(
        data: PDataPandas, meta_fields: PFieldsMeta
    ) -> PMetaPandas:
        return data[meta_fields]

    @staticmethod
    def meta_and_fields_of_pandas(
        data: PDataPandas, text_field: PFieldText, label_field: PFieldLabel
    ) -> (PFieldsMeta, PMetaPandas):
        """
        Guess that all fields in a dataframe are meta fields except for the text and label fields.
        """
        all_cols = list(data.columns)
        all_cols.remove(text_field)
        all_cols.remove(label_field)

        meta = data[all_cols]

        return (all_cols, meta)

    @staticmethod
    def text_field_of_pandas(data: PDataPandas) -> PFieldText:
        """Guess the text field in a pandas DataFrame."""

        cols_types = zip(data.columns, data.dtypes)

        obj_fields = [
            (col, typ) for col, typ in cols_types if is_string_dtype(typ)
        ]

        if len(obj_fields) == 0:
            raise Backtrack("DataFrame has no text fields.")

        elif len(obj_fields) > 1:
            raise Backtrack("DataFrame has more than 1 text field.")

        else:
            return obj_fields[0][0]

    @staticmethod
    def label_field_of_pandas(data: PDataPandas) -> PFieldLabel:
        """Guess the label field in a pandas DataFrame."""

        cols_types = zip(data.columns, data.dtypes)

        int_fields = [
            (col, typ) for col, typ in cols_types if is_integer_dtype(typ)
        ]

        if len(int_fields) == 0:
            raise Backtrack("DataFrame has no label fields.")

        elif len(int_fields) > 1:
            raise Backtrack("DataFrame has more than 1 label field.")

        else:
            return int_fields[0][0]

    @staticmethod
    def labels_of_pandas_field(
        data: PDataPandas, label_field: PFieldLabel
    ) -> PLabelsSequence:
        if label_field not in data:
            raise NoBacktrack(
                f"DataFrame has no field named {label_field}. It has {list(data.columns)}."
            )

        series = data[label_field]
        if not is_integer_dtype(series.dtype):
            raise NoBacktrack(
                f"The DataFrame field {label_field} is not an integer type expected of labels."
            )

        return list(series)

    @staticmethod
    def data_of_pandas_field(
        data: PDataPandas, text_field: PFieldText
    ) -> PDataSequence:
        if text_field not in data:
            raise NoBacktrack(
                f"DataFrame has no field named {text_field}. It has {list(data.columns)}."
            )

        series = data[text_field]
        if not is_string_dtype(series.dtype):
            raise NoBacktrack(
                f"The DataFrame field {text_field} is not a string type expected of text input."
            )

        return list(series)

    ## pytorch data

    # The torch data pipeline is thus: if a DataLoader is given, we assume the
    # enclosed dataset is a mapping with column names as key. These are
    # extracted as PDataTorchColumnwise and then this is treated similarly to a
    # pandas DataFrame to find text and label fields if not provided.

    @staticmethod
    def pytorch_columnwise_data_of_dataloader(
        data: PDataTorchDataLoader
    ) -> PDataTorchColumnwise:
        if isinstance(data.dataset, typing.Mapping):
            return data.dataset
        else:
            raise Backtrack("DataLoader does not contain a columnwise mapping.")

    @staticmethod
    def _is_val_text(val):
        return type(val) == str

    @staticmethod
    def _is_val_label(val):
        return type(val) in [bool, int]

    @staticmethod
    def pytorch_textfield_of_columnwise(
        data: PDataTorchColumnwise
    ) -> PFieldText:
        text_fields = [
            k for k in data.keys() if Inferences._is_val_text(data[k][0])
        ]
        # TODO: will not work if empty or not sequence

        if len(text_fields) == 0:
            raise Backtrack("Dataset does not contain any text fields.")
        elif len(text_fields) > 1:
            raise Backtrack("Dataset contains more than one text field.")
        else:
            return text_fields[0]

    @staticmethod
    def pytorch_labelfield_of_columnwise(
        data: PDataTorchColumnwise
    ) -> PFieldLabel:
        label_fields = [
            k for k in data.keys() if Inferences._is_val_label(data[k][0])
        ]
        # TODO: will not work if empty or not sequence

        if len(label_fields) == 0:
            raise Backtrack("Dataset does not contain any label fields.")
        elif len(label_fields) > 1:
            raise Backtrack("Dataset contains more than one label field.")
        else:
            return label_fields[0]

    @staticmethod
    def labels_of_pytorch_field(
        data: PDataTorchColumnwise, label_field: PFieldLabel
    ) -> PLabelsSequence:
        if label_field not in data:
            raise NoBacktrack(
                f"DataLoader has no field named {label_field}. It has {list(data.keys())}."
            )

        series = data[label_field]
        if not Inferences._is_val_label(series[0]):  # TODO: iterable
            raise NoBacktrack(
                f"The DataLoader field {label_field} is not an integer type expected of labels."
            )

        return list(series)

    @staticmethod
    def data_of_pytorch_field(
        data: PDataTorchColumnwise, text_field: PFieldText
    ) -> PDataSequence:
        if text_field not in data:
            raise NoBacktrack(
                f"DataLoader has no field named {text_field}. It has {list(data.keys())}."
            )

        series = data[text_field]
        if not Inferences._is_val_text(series[0]):  # TODO: iterable
            raise NoBacktrack(
                f"The DataLoader field {text_field} is not a string type expected of text input."
            )

        return list(series)

    ## Autowrap data related requirements

    # NOTE: Make sure the following rule is the last one for PTextToInputs.
    @staticmethod
    def raw_text_to_inputs() -> PTextToInputs:
        print(
            f"WARNING: Assuming this model takes text as input. "
            "If this is incorrect, please specify a function `text_to_inputs` that takes string as input and model args and kwargs as output."
        )

        def default_text_to_inputs(texts):
            """Raw text_to_inputs implementation assumes model text in raw text instead of tokenization."""
            return dict(args=[texts], kwargs={})

        return default_text_to_inputs

    @staticmethod
    def process_ds_from_sequence(
        data: PDataSequence, labels: PLabelsSequence
    ) -> (PDSFromSource, PStandardizeDatabatch):
        data = np.array(data)
        n_records = len(data)
        labels = np.array(labels)

        ids = np.array(list(range(n_records)))

        def default_ds_from_source(_):
            return nlp.Types.StandardBatch(text=data, labels=labels, ids=ids)

        default_ds_from_source.__doc__ = f"Default `ds_from_source` implementation for ({len(data)} instance(s)) in collection type {type(data)}."

        # currently trubatch refers to dict
        standardize_databatch = dataclasses.asdict

        return (default_ds_from_source, standardize_databatch)

    @staticmethod
    def datasequence_of_dataiterable(data: PDataIterable) -> PDataSequence:
        if isinstance(data, str):
            # NOTE2
            raise Backtrack(
                "Data is a single instance. This inference is not applicable."
            )

        if isinstance(data, DataFrame):
            raise Backtrack("Pandas DataFrame have special handling.")

        print(
            f"WARNING: converting iterable data if type {type(data)} to a sequence. This may cause errors if it is performed more than once."
        )

        return list(data)

    @staticmethod
    def labelsequence_of_labeliterable(
        labels: PLabelsIterable
    ) -> PLabelsSequence:
        if isinstance(labels, str):
            # NOTE2
            raise Backtrack(
                "Labels is a single instance. This inference is not applicable."
            )

        print("WARNING: converting iterable labels to a sequence")

        return list(labels)

    @staticmethod
    def process_ds_from_iterable(
        data: PDataIterable, labels: PLabelsIterable
    ) -> (PDSFromSource, PStandardizeDatabatch):
        raise NotImplementedError("figure out how to support non-sequence data")

    # label defaults

    # NOTE: This needs to below any of label type conversion rules so it doesn't
    # try to get applied before them.
    @staticmethod
    def labels_default(n_records: PNRecords) -> PLabelsSequence:
        print(
            f"WARNING: Could not find labels, assuming all {n_records} instance(s) have label 0."
        )
        return [0] * n_records

    # The below is needed since the set_data variant that accepts a single
    # instance will also try to derive a single label, even though the ingestion
    # process converts everything to sequences anyway for further processing.
    @staticmethod
    def label_default(n_records: PNRecords) -> PLabelInstance:
        if n_records != 1:
            raise Backtrack("Data is not a single instance.")
        print(
            f"WARNING: Could not find labels, assuming the instance has label 0."
        )
        return 0

    # The below is needed since the set_data variant that accepts an iterable
    # will also try to derive an iterable for labels, even though the ingestion
    # process converts everything to sequences anyway for further processing.
    @staticmethod
    def labels_default_iterable(n_records: PNRecords) -> PLabelsIterable:
        # Note that this will convert data to sequence first but this should be
        # happening either way as current pipeline converts everything to
        # sequence.
        return iter([0] * n_records)

    # Explanation configuration.

    @staticmethod
    def rebatch_size_cuda(model: PModelTorch) -> PRebatchSize:
        """
        Determine rebatch size from CUDA memory usage and availability.
        """
        from truera.client.nn.wrappers.torch import Torch

        if Torch.get_device().type != "cuda":
            raise Backtrack("Pytorch model is not using CUDA.")

        torch = import_optional("torch")

        # Free unused gpu ram first so the available/used measurement below
        # is accurate.
        torch.cuda.empty_cache()

        # Get how much cuda memory torch is using which is hopefully the
        # same as how much the given model is using. TODO(piotrm):
        # figure out what to do here if above assumption is not true.
        mem_free, mem_total = torch.cuda.mem_get_info()
        mem_used = mem_total - mem_free

        # Assume we can use all of the GPU ram.
        mem_available = mem_total

        size = mem_available // int(mem_used * 3)
        # 3 is a heuristic for ram needed for back-propagation per
        # forward-propagation. TODO(piotrm): unclear whether an actual
        # forward pass has been done at this point so we cannot be sure of
        # actual forward pass RAM usage.

        if size == 0:
            size = 1
            print(
                f"WARNING: model {model.__class__.__name__} may be too big to fit in memory."
            )

        return size

    # TODO: same as above but for tensorflow

    @staticmethod
    def rebatch_size_cpu() -> PRebatchSize:
        """
        Determine rebatch size from cpu memory usage and availability.
        """

        import os

        import psutil

        mem_used = psutil.Process(os.getpid()).memory_info().rss
        vmem = psutil.virtual_memory()
        mem_total = vmem.total
        mem_free = vmem.available

        # Unlike in the gpu case, we cannot assume we can use all of GPU
        # ram for our purposes, so we presume we can use the rest of
        # free CPU ram only.
        mem_available = mem_free

        size = mem_available // int(mem_used * 3)
        # 3 is a heuristic for ram needed for back-propagation per
        # forward-propagation. TODO(piotrm): unclear whether an actual
        # forward pass has been done at this point so we cannot be sure of
        # actual forward pass RAM usage.

        if size == 0:
            size = 1
            print(f"WARNING: model may be too big to fit in memory.")

        return size

    @staticmethod
    def n_metrics_records(n_records: PNRecords) -> PNMetricsRecords:
        return n_records

    @staticmethod
    def ref_token_from_wrapper(
        tokenizer_wrapper: PTokenizerWrapper
    ) -> PRefToken:
        """
        Get reference token from an explicit tokenizer wrapper.
        """
        return tokenizer_wrapper.pad_token

    @staticmethod
    def ref_token_default() -> PRefToken:
        """
        If all else fails, just use [PAD].
        """
        return "[PAD]"

    # Rules for debugging and demonstration purposes.

    @staticmethod
    def debug_arg1(debug_model: PDebugModel) -> PDebugArg:
        """Fail to infer anything the first time."""

        print("failing debug_arg1")

        # Do not seperate this from the next line and make sure it is only one
        # line long.
        CodeMapper.default().next_line("debug_arg1:raise")
        raise Backtrack("First failure reason.")

    @staticmethod
    def debug_arg2(debug_model: PDebugModel) -> PDebugArg:
        """Fail to infer anything the second time."""

        print("failing debug_arg2")

        # Do not seperate this from the next line and make sure it is only one
        # line long.
        CodeMapper.default().next_line("debug_arg2:raise")
        raise Backtrack("Second failure reason.")

    @staticmethod
    def debug_arg3(
        debug_model: PDebugModel, debug_infer_me: PDebugInfer
    ) -> PDebugArg:
        """Infer debug_arg only if debug_model is secret."""

        if debug_model == "secret":
            print("succeeding debug_arg3")
            return 42 + debug_infer_me

        print("failing debug_arg3")

        # Do not seperate this from the next line and make sure it is only one
        # line long.
        CodeMapper.default().next_line("debug_arg3:raise")
        raise Backtrack("Third failure reason.")

    @staticmethod
    def debug_infer_me(debug_model: PDebugModel) -> PDebugInfer:
        """Infer debug_infer_me from debug_model."""

        return 100
