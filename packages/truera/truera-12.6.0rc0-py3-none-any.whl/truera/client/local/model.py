from abc import ABC
from abc import abstractmethod

import numpy as np
import pandas as pd

from truera.protobuf.public.metadata_message_types_pb2 import \
    ModelMetadata  # pylint: disable=no-name-in-module


class Model(ABC):

    @abstractmethod
    def predict(self, xs: pd.DataFrame, score_type: str) -> np.ndarray:
        pass

    @property
    def name(self) -> str:
        pass


class VirtualModel(Model):

    def __init__(self, metadata: ModelMetadata, data_collection):
        self.metadata: ModelMetadata = metadata
        self.data_collection = data_collection
        self.model_type = "virtual"

    def predict(self, xs: pd.DataFrame, score_type: str) -> np.ndarray:
        raise ValueError(
            f"Model '{self.name}' is a virtual model. "
            "Computations are not supported for virtual models. "
            "Please use `attach_packaged_python_model_object` to upgrade a virtual model."
        )

    @property
    def name(self) -> str:
        return self.metadata.name
