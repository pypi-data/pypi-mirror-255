from abc import ABC
import logging
import shutil
import sys
import tempfile
from typing import Any, Mapping, Optional, Sequence
import uuid

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

from truera.client.cli.cli_utils import ModelType
from truera.client.ingestion.sdk_model_packaging import SklearnModelPackager
from truera.client.model_preprocessing import PipDependencyParser
from truera.client.services.artifact_interaction_client import \
    ArtifactInteractionClient
from truera.client.services.artifact_interaction_client import Project
from truera.utils.package_requirement_utils import get_python_version_str

MIN_DATA_REQUIRED = 50


class BaselineModel(ABC):

    def __init__(
        self,
        project_id: Optional[str],
        project_name: str,
        split_name: str,
        min_data_required: int = MIN_DATA_REQUIRED,
        log_level: int = logging.INFO
    ) -> None:
        self.project_id = project_id
        self.project_name = project_name
        self.split_name = split_name
        self.model = None
        self.model_output_type = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.train_params: Mapping[str, Any] = dict()
        self.min_data_required = min_data_required
        self.model_name = ""

    def validate_data(self, xs, ys):
        if xs.shape[0] < self.min_data_required:
            raise ValueError(
                f"Missing sufficient data to build model. Current data size: {xs.shape[0]}, minimum data points required {self.min_data_required}"
            )
        if isinstance(ys, pd.DataFrame) and ys.shape[1] == 1:
            y_label = ys.columns[0]
            ys = ys[y_label].values
        if len(np.unique(ys)) < 2:
            raise ValueError(
                f"Invalid prediction data, number of unique data points: {len(np.unique(ys))}. For classification, we expect at least two classes. For regression, we do not expect constant target variable."
            )

    def build_model(self, xs, ys):
        self.validate_data(xs, ys)
        self.model.fit(xs, ys)

    def score(self, xs, ys):
        return self.model.score(xs, ys)

    def ingest_model(
        self,
        ar_client: ArtifactInteractionClient,
        data_collection_name: str,
        additional_pip_dependencies: Optional[Sequence[str]] = None
    ):
        # devnote (rroy): This is optional since local projects do not have ids.
        # We will use this method only for remote, in which case, hitting this error is an implementation error on our end.
        if self.project_id is None:
            raise AssertionError("Need project id to ingest model.")
        output_dir = tempfile.mkdtemp()
        shutil.rmtree(output_dir, ignore_errors=True)
        additional_pip_dependencies = PipDependencyParser(
            additional_pip_dependencies
        )
        additional_pip_dependencies.add_default_model_runner_dependencies()
        SklearnModelPackager(
            self.model,
            transformer=None,
            model_output_type=self.model_output_type,
            python_version=get_python_version_str(),
            additional_pip_dependencies=additional_pip_dependencies
        ).save_model(self.logger, output_dir)
        project = Project(
            self.project_name, ar_client, project_id=self.project_id
        )
        model = project.create_model(
            self.model_name,
            ModelType.PyFunc,
            self.model_output_type,
            output_dir,
            data_collection_name=data_collection_name,
            train_split_name=self.split_name,
            train_parameters=self.train_params,
            user_generated_model=False
        )
        return model.upload(ar_client)


class ClassificationBaseLineModel(BaselineModel):

    def __init__(
        self,
        project_id: str,
        project_name: str,
        split_name: str,
        min_data_required: int = MIN_DATA_REQUIRED,
        log_level: int = logging.INFO
    ) -> None:
        super().__init__(
            project_id, project_name, split_name, min_data_required, log_level
        )
        self.model_output_type = "classification"
        self.model = LogisticRegression(random_state=0)
        self.train_params = {
            "model_type":
                f"{type(self.model).__module__}.{type(self.model).__name__}",
            "random_state":
                0
        }
        self.model_name = f"truera-{type(self.model).__name__}-{self.split_name}"


class RegressionBaseLineModel(BaselineModel):

    def __init__(
        self,
        project_id: str,
        project_name: str,
        split_name: str,
        min_data_required: int = MIN_DATA_REQUIRED,
        log_level: int = logging.INFO
    ) -> None:
        super().__init__(
            project_id, project_name, split_name, min_data_required, log_level
        )
        self.model_output_type = "regression"
        self.model = LinearRegression()
        self.train_params = {
            "model_type":
                f"{type(self.model).__module__}.{type(self.model).__name__}"
        }
        self.model_name = f"truera-{type(self.model).__name__}-{self.split_name}"
