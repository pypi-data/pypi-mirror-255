from typing import Any, Generic, TypeVar

# Backend-specific models:
BaseModel = TypeVar("BaseModel")

# Backend-specific tensors:
BaseTensor = TypeVar("BaseTensor")

# from trulens.utils.typing import BaselineLike
BaselineLike = Any
# Any is actually BaselineLike from trulens but don't want to import trulens
# here. This file is imported by truera.client.truera_workspace which is common
# across diagnostic and nn products.


class NNBackend(Generic[BaseTensor, BaseModel]):
    """
    Various decorators over the base tensor type to indicate their function in a
    model or ML pipeline. Included here are Model and Tensor which are meant to
    extend BaseModel and BaseTensor respectively. The goal of these is to be
    able to distinguish objects which are wrapped for us or by us from ones
    which are not. Base versions may not be ready for us, while the ones in this
    backend are created or wrapped by us. They can further indicate some
    information like whether a tensor represents an input or output or something
    else.

    The tensor types form a hierarchy:

        Tensor
            Inputs
                Batchable
                    Embeddings
                    Masks
                    Words
                Parameter
            Outputs
                Logits
                Probits

    """

    # TODO: reuse or merge with trulens backends
    class Model(object):  # WANT: subclass BaseModel
        """
        Backend's representation of a model. A user model should contain this
        somewhere inside of it (or be it). This should subclass BaseModel
        but cannot specify that in python right now.
        """
        ...

    class Tensor(object):  # WANT: subclass BaseTensor
        """
        Framework-specific tensors annotated with Truera-related indicators such
        as Input vs. Output, Batchable vs. Non-Batchable.
        """
        ...

    class Inputs(Tensor):
        """
        Input tensors.
        """

    class Batchable(Inputs):
        """
        Batchable input tensors.
        """

    class Parameter(Inputs):
        """
        Non-batchable input tensors.
        """

    class Embeddings(Batchable):
        """
        Embeddings tensors.
        """

    class Masks(Batchable):
        """
        Attention masks tensors.
        """

    class Words(Batchable):
        """
        Words tensors (i.e. not embeddings).
        """

    class Outputs(Tensor):
        """
        Model output tensors.
        """

    class Logits(Outputs):
        """
        Logit outputs.
        """

    class Probits(Outputs):
        """
        Probit outputs.
        """
