from __future__ import annotations

from abc import ABC
from abc import abstractmethod
import json
import logging
from typing import Any, Mapping, Optional, Sequence, TYPE_CHECKING, Union

import numpy as np
import pandas as pd

from truera.client.client_environment import LocalContextStorage
from truera.client.client_utils import _STRING_TO_INPUT_DATA_FORMAT
from truera.client.client_utils import _STRING_TO_QOI
from truera.client.ingestion import ColumnSpec
from truera.client.ingestion import ModelOutputContext
from truera.client.ingestion import NLPColumnSpec
from truera.client.ingestion.schema import BinaryClassificationColumns
from truera.client.ingestion.schema import RegressionColumns
from truera.client.ingestion.schema import Schema
from truera.client.ingestion_client import Credential
from truera.client.ingestion_client import IngestionClient
from truera.client.ingestion_client import Table
from truera.client.intelligence.explainer import Explainer
from truera.client.intelligence.segment import SegmentGroup
from truera.client.public.communicator.http_communicator import \
    AlreadyExistsError
from truera.client.util import workspace_validation_utils
from truera.protobuf.public import qoi_pb2 as qoi_pb
from truera.protobuf.public.scheduled_ingestion_service import \
    scheduled_ingestion_service_pb2 as scheduled_pb
from truera.protobuf.public.util import split_mode_pb2 as sm_pb
from truera.public.feature_influence_constants import \
    get_output_type_from_score_type
import truera.public.feature_influence_constants as fi_constants

if TYPE_CHECKING:
    from truera.client.nn import wrappers as base
    from truera.client.nn.client_configs import AttributionConfiguration
    from truera.client.nn.client_configs import RNNUserInterfaceConfiguration


class BaseTrueraWorkspace(ABC):

    _DEFAULT_NUM_DEFAULT_INFLUENCES = 1000

    def __init__(self):
        self.logger = logging.Logger(__name__)

    def __str__(self) -> str:
        return json.dumps(self.get_context(), indent=4)

    def __repr__(self) -> str:
        return json.dumps(self.get_context(), indent=4)

    @abstractmethod
    def get_projects(self) -> Sequence[str]:
        """Get all projects accessible by current user for the current workspace environment.
        """
        pass

    @abstractmethod
    def set_project(self, project: str):
        """Set the current project to use for the current workspace environment. This will unset the rest of the context (data collection, data split, model, etc.) if set prior.
        Args:
            project: Name of the project.
        Raises:
            ValueError: Raised if the project does not exist.
        """
        pass

    @abstractmethod
    def add_project(
        self,
        project: str,
        score_type: str,
        input_type: Optional[str] = "tabular",
        num_default_influences: Optional[int] = None
    ):
        """Adds and sets project to use for the current workspace environment. This will unset the rest of the context (data collection, data split, model, etc) if set prior.
        Args:
            project: Name of the project.
            score_type: Scorer type configuration for the project. Options are ["logits", "probits", "classification", "regression"].
            input_type: Input data type for the project. Must be one of ["tabular", "time_series_tabular"]. Defaults to "tabular".
            num_default_influences: Number of influences used by default for most influence-requiring graphs, computations, etc. Note that this will take the first of the provided many from the data split --- therefore, shuffling data splits is generally advised prior to ingestion. If creating a project and left as None, then will be set as 1000.
                
        Examples:
        ```python
        # Create a probits project
        >>> tru.add_project("Project Name", score_type = "probits")
        ```
        """
        pass

    def list_valid_score_types(self) -> Sequence[str]:
        """List the valid score types that can be set for the currently set project.
        Returns:
            Sequence[str]: Valid score types.
        """
        if self._get_output_type() == "regression":
            return fi_constants.VALID_SCORE_TYPES_FOR_REGRESSION
        elif self._get_output_type() == "ranking":
            return fi_constants.VALID_SCORE_TYPES_FOR_RANKING
        return fi_constants.VALID_SCORE_TYPES_FOR_CLASSIFICATION

    @abstractmethod
    def set_score_type(self, score_type: str):
        """Set the score type of the currently set project.
        Args:
            score_type: Scorer type configuration.
                Options are ["logits", "probits", "classification", "regression", None]. Defaults to None.
        """
        pass

    @abstractmethod
    def set_influence_type(self, algorithm: str):
        """Set the influence algorithm type of the currently set project.
        Args:
            algorithm: Algorithm type. Options are ["truera-qii", "shap"]. Defaults to "truera-qii" if available, and otherwise "shap".
        """
        pass

    @abstractmethod
    def get_influence_type(self) -> str:
        """Get the influence algorithm type of the currently set project.
        """
        pass

    @abstractmethod
    def get_num_default_influences(self) -> int:
        """Get the number of influences computed by default of the currently set project.
        Returns:
            int: Number of default influences.
        """
        pass

    @abstractmethod
    def set_num_default_influences(self, num_default_influences: int):
        """Set the number of influences computed by default of the currently set project.
        Args:
            num_default_influences: Number of influences used by default for most influence-requiring graphs, computations, etc. Note that this will take the first of the provided many from the data split --- therefore, shuffling data splits is generally advised prior to ingestion.
        """
        pass

    @abstractmethod
    def list_performance_metrics(self) -> Sequence[str]:
        """
        Lists the available metrics that can be supplied to compute performance, and be set as the project default.

        Returns:
            Sequence[str]: Available metrics.
        """

    @abstractmethod
    def get_default_performance_metrics(self) -> Sequence[str]:
        """Get the default performance metrics of the currently set project.

        Returns:
            Sequence[str]: Default performance metrics.
        """

    @abstractmethod
    def set_default_performance_metrics(
        self, performance_metrics: Sequence[str]
    ):
        """Set the default performance metrics of the currently set project.

        Args:
            performance_metrics: Performance metrics to use by default.
        """
        pass

    @abstractmethod
    def get_num_internal_qii_samples(self) -> int:
        """Get the number of samples used internally in influence computations of the currently set project.

        Returns:
            int: Number of samples to be used internally for influence computations.
        """
        pass

    @abstractmethod
    def set_num_internal_qii_samples(self, num_samples: int):
        """Set the number of samples used internally in influence computations of the currently set project.
        Args:
            num_samples: Number of samples to be used internally for influence computations.
        """
        pass

    @abstractmethod
    def set_maximum_model_runner_failure_rate(
        self, maximum_model_runner_failure_rate: float
    ):
        """Sets the maximum model runner failure rate (fraction of points on which the model can fail for a model run to be considered successful) for the current project.
        Args:
            maximum_model_runner_failure_rate (float): Maximum failure rate. Must be in [0, 1). By default, it is set to 0.
        """
        pass

    @abstractmethod
    def get_maximum_model_runner_failure_rate(self) -> float:
        """Get the maximum model runner failure rate (fraction of points on which the model can fail for a model run to be considered successful) for the current project.
        """
        pass

    @abstractmethod
    def set_ranking_k(self, ranking_k: int):
        """Sets the ranking k for the current project.

        Args:
            ranking_k: Must be in >= 0.
        """
        pass

    @abstractmethod
    def get_ranking_k(self) -> int:
        """Gets the ranking k for the current project.

        Returns:
            int: Ranking k.
        """
        pass

    def _validate_num_default_influences(self, num_default_influences: int):
        self._ensure_project()
        if num_default_influences <= 0:
            raise ValueError("`num_default_influences` must be > 0!")

    def _validate_num_samples_for_influences(self, num_samples: int):
        self._ensure_project()
        if num_samples <= 0:
            raise ValueError("`num_samples` must be > 0!")

    @abstractmethod
    def get_models(self) -> Sequence[str]:
        """Get all models in the connected project.
        Raises:
            ValueError: Raised if the workspace isn't connected to any project.
        Returns:
            Name of models in the project.
        """
        pass

    @abstractmethod
    def set_model(self, model_name: str):
        """Set the current model to use for all operations in the current workspace. This will also change the data collection to the one corresponding to the provided model if different than the priorly set data collection.
        Args:
            model_name: Name of the model. If None, will unset the model.
        Raises:
            ValueError: Raised if no project is associated with the current workspace.
                Use set_project to set the correct project.
            ValueError: Raised if there is no such model in the project.
        """
        pass

    @abstractmethod
    def delete_model(
        self, model_name: Optional[str] = None, *, recursive: bool = False
    ):
        """Delete a model from the current TruEra workspace. This will only delete artifacts within the current location context (either local or remote).
        Args:
            model_name: Name of the model to be deleted. By default the currently set model will be deleted.
            recursive: Whether to delete any model tests associated with the model. Defaults to False.
        """
        pass

    @abstractmethod
    def get_data_collections(self) -> Sequence[str]:
        """Get all data-collections in the connected project.
        Raises:
            ValueError: Raised if the workspace isn't connected to any project.
        Returns:
            Name of data-collections in the project.
        """
        pass

    @abstractmethod
    def get_data_splits(self) -> Sequence[str]:
        """Get all data-splits in the connected data-collection.
        Raises:
            ValueError: Raised if the workspace isn't connected to any project.
            ValueError: Raised if the workspace isn't connected to any data-collection.
        Returns:
            Name of data-splits in the project.
        """
        pass

    @abstractmethod
    def set_data_collection(self, data_collection_name: str):
        """Set the current data collection to use for all operations in the workspace. This will also unset the current model if it is not associated with the provided data collection.
        Args:
            data_collection_name: Name of the data_collection. If None, will unset the data collection.
        Raises:
            ValueError: Raised if no project is associated with the current workspace.
                Use set_project to set the correct project.
            ValueError: Raised if there is no such data_collection in the project.
        """
        pass

    @abstractmethod
    def _get_feature_transform_type_for_data_collection(self):
        pass

    @abstractmethod
    def set_data_split(self, data_split_name: str):
        """Set the current data split to use for all operations in the current workspace.
        Args:
            data_split_name: Name of the data_split. If None, will unset the data split.
        Raises:
            ValueError: Raised if no project is associated with the current workspace.
                Use set_project to set the correct project.
            ValueError: Raised if no data_collection is associated with the current workspace.
                Use set_data_collection to set the correct data_collection.
            ValueError: Raised if there is no such data_split in the data_collection.
        """
        pass

    @abstractmethod
    def add_python_model(
        self,
        model_name: str,
        model: Any,
        transformer: Optional[Any] = None,
        *,
        additional_pip_dependencies: Optional[Sequence[str]] = None,
        additional_modules: Optional[Sequence[Any]] = None,
        classification_threshold: Optional[float] = None,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        verify_model: bool = True,
        compute_predictions: Optional[bool] = None,
        compute_feature_influences: bool = False,
        compute_for_all_splits: bool = False,
        **kwargs
    ):
        """Registers and adds a new model, including the executable model object provided. This method deduces the model framework to appropriately serialize
            and upload the model object to TruEra server. Models of supported frameworks can be passed directly.
            Supported Model Frameworks: sklearn, xgboost, catboost, lightgbm, pyspark (tree models only).
            If you cannot ingest your model via this function due to custom logic, feature transforms, etc., see `create_packaged_python_model()`.
        [ALPHA] For frameworks that are not yet supported, or for custom model implementations the prediction
            function for the model can be provided as the model.
            For binary classifiers, the prediction function should accept a pandas DataFrame as input and produce
            a pandas DataFrame as output with the class probabilities and [0, 1] as the column header.
            For regression models, the prediction function should accept a pandas DataFrame as input and produce
            the result as a pandas DataFrame with "Result" as the column header.
            All required dependencies to execute the prediction function should be provide as additional_pip_dependencies.
            For example:"""
        """
            ```python
            def predict(df):
                return pd.DataFrame(my_model.predict_proba(df, validate_features=False), columns=[0, 1])
            tru.add_python_model("my_model", predict, additional_pip_dependencies=["xgboost==1.3.1", "pandas==1.1.1"])
            ```
        Args:
            model_name: Name assigned to the model.
            model: The python model object or the prediction function.
                Supported frameworks are catboost, lightgbm, sklearn (including sklearn.pipeline) and xgboost, and tree-based PySpark models. For prediction function, please see the description above.
            transformer: The python transform object or callable function.
            additional_pip_dependencies: List of pip dependencies required to execute the model. When model object
                is from a supported framework, pip dependency for that framework is automatically inferred. If a prediction function is provided as the model,
                additional pip dependencies are not automatically inferred and must be explicitly provided.
                Defaults to None. Example: ["pandas==1.1.1", "numpy==1.20.1"]
            additional_modules: List of modules not available as pip packages required for the model. These must already be imported.  Defaults to None.
            classification_threshold: Threshold that is applied to model predictions to determine classification outcomes. Ignored for regression models.
            train_split_name: The name of the train split of the model
            train_parameters: Train parameters of the model. Ex. {'n_estimators": 10}"}
            verify_model: Locally verify the model is packaged properly and can operate on existing split data. Defaults to True.
            compute_predictions: Trigger computations of model predictions on the base/default split of the model's data collection, if such a split exists. Ignored for local models. Defaults to True when using `local_execution` for remote workspace..
            compute_feature_influences: Trigger computations of model feature influences on the base/default split of the model's data collection, if such a split exists. Ignored for local models.
            compute_for_all_splits: If `compute_predictions` and/or `compute_feature_influences`, triggers computations for all existing data splits (not solely the base/default split). Ignored for local models.
        Raises:
            NotSupportedError: Raised if the model type is not supported.
                You can still use the [`add_packaged_python_model`][truera.client.truera_workspace.TrueraWorkspace.add_packaged_python_model]
                method to upload a pre-serialized model to TruEra server.

        Examples:
        ```python
        >>> tru.set_project("Project Name")
        >>> tru.set_data_collection("Data Collection Name")

        # Add a python model (model_v1) and specify its metadata including the training data and parameters
        >>> tru.add_python_model("model_v1",
                                model_object_v1,
                                train_split_name="train",
                                train_parameters = {'max_depth': 5, eta = 0.3, 'num_leaves': 32})
        ```
        """
        pass

    @abstractmethod
    def add_packaged_python_model(
        self,
        model_name: str,
        model_dir: str,
        *,
        data_collection_name: Optional[str] = None,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        verify_model: bool = True,
        compute_predictions: Optional[bool] = None,
        compute_feature_influences: bool = False,
        compute_for_all_splits: bool = False
    ):
        """Registers and adds a new model, along with a pre-serialized and packaged executable Python model object.
        The model is also attached to the workspace as the current model.
        Args:
            model_name: Name assigned to the model.
            model_dir: Directory where packaged model is located.
            data_collection_name: Data collection to attach to the model,
                by default the data collection attached to the workspace will be used. Defaults to None.
            train_split_name: The name of the train split of the model
            train_parameters: Train parameters of the model. Ex. {'n_estimators": 10}"}
            verify_model: Locally verify the model is packaged properly and can operate on existing split data. Defaults to True.
            compute_predictions: Trigger computations of model predictions on the base/default split of the model's data collection, if such a split exists. Ignored for local models. Defaults to True when using `local_execution` for remote workspace.
            compute_feature_influences: Trigger computations of model feature influences on the base/default split of the model's data collection, if such a split exists. Ignored for local models.
            compute_for_all_splits: If `compute_predictions` and/or `compute_feature_influences`, triggers computations for all existing data splits (not solely the base/default split). Ignored for local models.
        """
        pass

    @abstractmethod
    def create_packaged_python_model(
        self,
        output_dir: str,
        model_obj: Optional[Any] = None,
        additional_pip_dependencies: Optional[Sequence[str]] = None,
        additional_modules: Optional[Sequence[Any]] = None,
        model_path: Optional[str] = None,
        model_code_files: Optional[Sequence[str]] = None
    ):
        """Creates a template of a packaged Python model object to be edited and then uploaded to TruEra server.
        Can be used to package either Python model objects, or serialized model data. This workflow should only be used for custom models or to debug model ingestion.
        To upload a models of a known framework, it is recommended to use the `add_python_model()` function.
        Args:
            output_dir: Path to the directory to create template. Cannot be an existing directory.
            model_obj: The Python model object to package. Supported frameworks are catboost, lightgbm, sklearn, xgboost, and tree-based PySpark models.
            additional_pip_dependencies: List of pip dependencies required to execute the model. When model object
                is from a supported framework, pip dependency for that framework is automatically inferred. If a prediction function is provided as the model,
                additional pip dependencies are not automatically inferred and must be explicitly provided.
                Defaults to None. Example: ["pandas==1.1.1", "numpy==1.20.1"].
            additional_modules: List of modules not available as pip packages required for the model. These must already be imported.  Defaults to None.
            model_path: Path to a model file or directory. Can be a serialized model or a directory containing multiple files of serialized data.
                Ignored if `model_obj` is passed in.
            model_code_files: List of paths to additional files to be packaged with the model. Ignored if `model_obj` is passed in.
        """
        pass

    @abstractmethod
    def verify_packaged_model(self, model_path: str):
        """Locally verifies a packaged Python model by loading the model and, if available, running it on split data ingested into the TruEra system.
        The model must already be packaged, e.g. via `create_packaged_python_model()`. The project and data collection for the model must also be set in the current workspace context.
        This function assumes that it is running an environment with any model dependencies/packages installed.
        Args:
            model_path (str): Path to packaged model directory.
        """
        pass

    @abstractmethod
    def add_nn_model(
        self,
        model_name: str,
        truera_wrappers: base.WrapperCollection,
        attribution_config: dict,
        model: Optional[Any] = None,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        **kwargs
    ):
        """[Alpha] Upload a NN model to TruEra server. The model is also attached to the workspace as the current model.

        Example:
        ```python
        # During NN Ingestion you will create two objects
        >>> from truera.client.nn.client_configs import NLPAttributionConfiguration
        >>> attr_config = NLPAttributionConfiguration(...)

        >>> from truera.client.nn.wrappers.autowrap import autowrap
        >>> truera_wrappers = autowrap(...) # Use the appropriate NN Diagnostics Ingestion to create this

        # Add the model to the truera workspace
        >>> tru.add_nn_model(
        >>>     model_name="<model_name>",
        >>>     truera_wrappers,
        >>>     attr_config
        >>> )
        ```


        Args:
            model_name: Name assigned to the model.
            truera_wrappers: A set of wrappers to help truera run your model. The tutorial should help you get them.
            attribution_config: An attribution config containing attribution run parameters.
            model: Your model object.
            train_split_name: The name of the train split of the model.
            train_parameters: Train parameters of the model. Ex. {'n_estimators": 10}"}

        Raises:
            ValueError: Raised if no project is associated with the current workspace. Use set_project
                to set the correct project.
            ValueError: Raised if workspace is not attached to a data_collection. Either attach workspace
                to a data-collection or provide the data_collection_name.
            ValueError: Raised if the provided data_collection_name does not exist in the current project.
        """
        pass

    @abstractmethod
    def add_model(
        self,
        model_name: str,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None
    ):
        """Registers and adds a new model in TruEra. By default, the model is "virtual" in that it
        does not have an executable model object attached. To add the model object itself, see `add_python_model()`.
        Args:
            model_name: Name of model to create
            train_split_name: The name of the train split of the model
            train_parameters: Train parameters of the model. Ex. {'n_estimators": 10}"}
        """
        pass

    @abstractmethod
    def delete_data_split(
        self,
        data_split_name: Optional[str] = None,
        *,
        recursive: bool = False
    ):
        """Delete a data split from the current TruEra workspace. This will only delete artifacts within the current location context (either local or remote).
        Args:
            data_split_name: Name of the data split to be deleted. By default the currently set data split will be deleted.
            recursive: Whether to delete any model tests associated with the data split. Defaults to False.
        """
        pass

    @abstractmethod
    def delete_data_collection(
        self,
        data_collection_name: Optional[str] = None,
        *,
        recursive: bool = False
    ):
        """Delete a data collection from the current TruEra workspace. This will only delete artifacts within the current location context (either local or remote). Note: Data collection can be deleted only after all
            the data splits in the data collection have been deleted.
        Args:
            data_collection_name: Name of the data collection to be deleted. By default the currently set
                data collection will be deleted.
            recursive: Whether to delete any data splits as well in the data collection. Defaults to False.
        """
        pass

    @abstractmethod
    def add_data(
        self,
        data: Union[pd.DataFrame, 'Table'],
        *,
        data_split_name: str,
        column_spec: Union[ColumnSpec, NLPColumnSpec,
                           Mapping[str, Union[str, Sequence[str]]]],
        model_output_context: Optional[Union[ModelOutputContext, dict]] = None,
        is_production_data: bool = False,
        **kwargs
    ):
        """Add data by either creating a new split or appending to an existing split. The split will be set in the current context.

        ColumnSpec/NLPColumnSpec and ModelOutputContext classes can be imported from `truera.client.ingestion`.
        Alternatively `column_spec` and `model_output_context` can be specified as Python dictionaries.

        Args:
            data: A pd.DataFrame or Table containing the data to be added.
            data_split_name: The name of the split to be created or appended to.
            column_spec: The ColumnSpec or NLPColumnSpec mapping column names in the data to corresponding data kind.
                Parameters include:
                    id_col_name, timestamp_col_name, pre_data_col_names, post_data_col_names, prediction_col_names, label_col_names,
                    extra_data_col_names, feature_influence_col_names, token_influence_col_names, tags_col_name, token_col_name, sentence_embeddings_col_name
            model_output_context: Contextual information about data involving a model, such as the model name and score type.
                This argument can be omitted in most cases, as the workspace infers the appropriate values from the context.
        """

    @abstractmethod
    def add_production_data(
        self,
        data: Union[pd.DataFrame, 'Table'],
        *,
        column_spec: Union[ColumnSpec, NLPColumnSpec,
                           Mapping[str, Union[str, Sequence[str]]]],
        model_output_context: Optional[Union[ModelOutputContext, dict]] = None,
        **kwargs
    ):
        """Add production data.

        ColumnSpec and ModelOutputContext classes can be imported from `truera.client.ingestion`.
        Alternatively `column_spec` and `model_output_context` can be specified as Python dictionaries.

        Args:
            data: A pd.DataFrame or Table containing the data to be added.
            column_spec: The ColumnSpec mapping column names in the data to corresponding data kind.
                Parameters include:
                    id_col_name, timestamp_col_name, pre_data_col_names, post_data_col_names, prediction_col_names, label_col_names,
                    extra_data_col_names, feature_influence_col_names, token_influence_col_names, tags_col_name, token_col_name, sentence_embeddings_col_name
            model_output_context: Contextual information about data involving a model, such as the model name and score type.
                This argument can be omitted in most cases, as the workspace infers the appropriate values from the context.
        """
        pass

    @abstractmethod
    def add_labels(
        self, label_data: Union[Table, str], label_col_name: str,
        id_col_name: str, **kwargs
    ):
        """[Alpha] Add labels to an existing data split.

        Args:
            label_data: A Table or URI of file containing the label data.
                Table:
                    Use `add_data_source` or `get_data_source` to get a Table. You can optionally futher filter the Table by applying `filter`.
                URI:
                    Used to load external data source into the system. This is similar to ingesting via `add_data_source` and Table,
                    without the filters. The data in the external data source will be sub-sampled (random or first N) and ingested into the system.
                    By default up to 5000 rows are ingested as the split. You can override this by specifying `sample_count=X`.
                    Sampling is either done by using first N rows or sampling rows randomly (without replacement). Defaults to random. You can override this by specifying `sample_kind="first"`.
            label_col_name: Column name for the labels or ground truth in the provided label_data.
            id_col_name: Column name for the unique row identifier in the provided label_data.  Used to match labels with corresponding data points.

            **credential (Credential, optional): Provide the credential object if the data source requires authentication to read from it. Defaults to None.
            **format (str):The format in which the file (local) or blob (AWS S3, Azure WASB etc.) are stored in.
            **first_row_is_header (bool): For text based delimited files (csv, tsv etc.), indicates if the first row provides header information. Defaults to True.
            **column_delimiter (str): For text based delimited files (csv, tsv etc.), provides the delimiter to separate column values. Defaults to ','.
            **quote_character (str): For text based delimited files (csv, tsv etc.), if quotes are used provide the quote character. Defaults to '"'.
            **null_value (str): For text based delimited files (csv, tsv etc.), the string that signifies null value. Defaults to 'null'.
            **empty_value (str): For text based delimited files (csv, tsv etc.), the string that signifies empty value. Defaults to '""'.
            **date_format (str): For text based delimited files (csv, tsv etc.), if any column has date time, provide the format string. Defaults to 'yyyy-MM-dd HH:mm:ssZZ'.
            **account_key (str): For reading from Azure Storage Blob (WASB), provide the account_key to be used to read the blob. Not required if `credential` object is provided.
            **access_key_id (str): For reading from a s3 bucket, provide the access key id to be used to read the blob. Not required if `credential` object is provided or the underlying deployment is in a role with access to the bucket.
            **secret_access_key (str): For reading from a s3 bucket, provide the secret access key to be used to read the blob. Not required if `credential` object is provided or the underlying deployment is in a role with access to the bucket.
            **database_name (str): For reading from MySQL database, provide the database name to use. Required for MySQL data source.
            **table_name (str): For reading from MySQL database, provide the table name to use. Required for MySQL data source.
            **sample_count (int): Maximum rows to use when creating the split. Defaults to 5000.
            **sample_kind (str): Specifies the strategy to use while sub-sampling the rows. Defaults to "random".
            **timeout_seconds (int): Number of seconds to wait for data source. Defaults to 300.
        """

        pass

    @abstractmethod
    def add_extra_data(
        self, extra_data: Union[Table, str],
        extras_col_names: Union[str, Sequence[str]], id_col_name: str, **kwargs
    ):
        """[Alpha] Add extra data to an existing data split.
        Args:
            extra_data: A Table or URI of file containing the label data.
                Table:
                    Use `add_data_source` or `get_data_source` to get a Table. You can optionally futher filter the Table by applying `filter`.
                URI:
                    Used to load external data source into the system. This is similar to ingesting via `add_data_source` and Table,
                    without the filters. The data in the external data source will be sub-sampled (random or first N) and ingested into the system.
                    By default up to 5000 rows are ingested as the split. You can override this by specifying `sample_count=X`.
                    Sampling is either done by using first N rows or sampling rows randomly (without replacement). Defaults to random. You can override this by specifying `sample_kind="first"`.
            extras_col_names: Column name(s) for the extra data columns to be ingested.
            id_col_name: Column name for the unique row identifier in the provided label_data.  Used to match labels with corresponding data points.
            **credential (Credential, optional): Provide the credential object if the data source requires authentication to read from it. Defaults to None.
            **format (str):The format in which the file (local) or blob (AWS S3, Azure WASB etc.) are stored in.
            **first_row_is_header (bool): For text based delimited files (csv, tsv etc.), indicates if the first row provides header information. Defaults to True.
            **column_delimiter (str): For text based delimited files (csv, tsv etc.), provides the delimiter to separate column values. Defaults to ','.
            **quote_character (str): For text based delimited files (csv, tsv etc.), if quotes are used provide the quote character. Defaults to '"'.
            **null_value (str): For text based delimited files (csv, tsv etc.), the string that signifies null value. Defaults to 'null'.
            **empty_value (str): For text based delimited files (csv, tsv etc.), the string that signifies empty value. Defaults to '""'.
            **date_format (str): For text based delimited files (csv, tsv etc.), if any column has date time, provide the format string. Defaults to 'yyyy-MM-dd HH:mm:ssZZ'.
            **account_key (str): For reading from Azure Storage Blob (WASB), provide the account_key to be used to read the blob. Not required if `credential` object is provided.
            **access_key_id (str): For reading from a s3 bucket, provide the access key id to be used to read the blob. Not required if `credential` object is provided or the underlying deployment is in a role with access to the bucket.
            **secret_access_key (str): For reading from a s3 bucket, provide the secret access key to be used to read the blob. Not required if `credential` object is provided or the underlying deployment is in a role with access to the bucket.
            **database_name (str): For reading from MySQL database, provide the database name to use. Required for MySQL data source.
            **table_name (str): For reading from MySQL database, provide the table name to use. Required for MySQL data source.
            **sample_count (int): Maximum rows to use when creating the split. Defaults to 5000.
            **sample_kind (str): Specifies the strategy to use while sub-sampling the rows. Defaults to "random".
            **timeout_seconds (int): Number of seconds to wait for data source. Defaults to 300.
        """

        pass

    @abstractmethod
    def add_nn_data_split(
        self,
        data_split_name: str,
        truera_wrappers: base.WrapperCollection,
        split_type: Optional[str] = "all",
        *,
        pre_data: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        label_data: Optional[pd.DataFrame] = None,
        label_col_name: Optional[str] = None,
        id_col_name: Optional[str] = None,
        extra_data_df: Optional[pd.DataFrame] = None
    ):
        """[Alpha] Upload NN data split to TruEra server.

        Example:
        ```python
        # During NN Ingestion to add a split you will create wrappers
        >>> from truera.client.nn.wrappers.autowrap import autowrap
        >>> truera_wrappers = autowrap(...) # Use the appropriate NN Diagnostics Ingestion to create this

        # Add the data split to the truera workspace
        >>> tru.add_nn_data_split(
        >>>     data_split_name="<split_name>",
        >>>     truera_wrappers,
        >>>     split_type="<split_type_train_or_test>"
        >>> )
        ```

        Args:
            data_split_name: Name of the split to be uploaded.
            truera_wrappers: A Base.WrapperCollection housing a base.Wrappers.SplitLoadWrapper that helps load data files from files. This must be implemented via subclassing the truera.client.nn.wrappers.Base.SplitLoadWrapper
            split_type: The type of the data split. Options are ["all", "train", "test", "validate", "oot", "prod", "custom"]. Defaults to "all".
            pre_data: Data.
            label_data: Label data.
            label_col_name: The column name in `pre_data` containig label data
            id_col_name: The column name in `pre_data` containing record ID data
            extra_data_df: Extra columns which are not used / consumed by the model, but could be used for other analysis like defining segments.
        """
        pass

    @abstractmethod
    def add_model_predictions(
        self,
        prediction_data: Union[pd.DataFrame, Table],
        id_col_name: str = None,
        *,
        prediction_col_name: Optional[str] = None,
        data_split_name: Optional[str] = None,
        ranking_group_id_column_name: Optional[str] = None,
        ranking_item_id_column_name: Optional[str] = None,
        score_type: Optional[str] = None,
    ):
        """Adds prediction data for the current model. Assumes predictions are calculated for the default score type of the project.

        Args:
            prediction_data: Prediction data to add.
            id_col_name: Column name for the unique row identifier in the provided `prediction_data`. Used to match predictions with corresponding split data. 
            prediction_col_name: Column name from which to pull prediction data. Only required if `prediction_data` is a Table or URI.
            data_split_name: Data split that predictions are associated with. If None, defaults to split set in the current context.
            ranking_group_id_column_name: Column name for group id for ranking projects.
            ranking_item_id_column_name: Column name for item id for ranking projects.
            score_type: Specifies the score type for prediction data, if provided. Defaults to None, in which case the score type of the project is used.
        """
        pass

    @abstractmethod
    def add_model_feature_influences(
        self,
        feature_influence_data: pd.DataFrame,
        *,
        id_col_name: str,
        data_split_name: Optional[str] = None,
        background_split_name: Optional[str] = None,
        timestamp_col_name: Optional[str] = None,
        influence_type: Optional[str] = None,
        score_type: Optional[str] = None,
    ):
        """Adds feature influence for the current model and split. Assumes influences are calculated for the default
        score type of the project.

        Args:
            feature_influence_data: Feature influence data to add. Must be aligned with the pre-processed data of the given split.
            id_col_name: Column name for the unique identifier of each data point.
            data_split_name: Data split that influences are associated with. If None, defaults to split set in the current context.
            background_split_name: Background data split that influences are computed against. If None, defaults to the base split of the data collection (if this is not explicitly set, it is an ingested split of type "all" or "train").
            timestamp_col_name: Column name for the timestamp of each data point. Must be a column of type string or pd.DateTime. Defaults to None.
            influence_type: Influence algorithm used to generate influences.
                If influence type of project is set to "truera-qii", assumes that explanations are generated using truera-qii. 
                If influence type of project is set to "shap", then `influence_type` must be passed in as one of ["tree-shap-tree-path-dependent", "tree-shap-interventional", "kernel-shap"].
            score_type: The score type to use when computing influences. If None, uses default score type of project. Defaults to None. For a list of valid score types, see `list_valid_score_types`.
        """
        pass

    def get_predictions(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None,
    ) -> pd.DataFrame:
        """Get the model predictions associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the total number of points for local projects and the setting for "Number of default influences" for remote projects.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
        Returns:
            The model predictions associated with the current data-split.
        """
        pass

    def get_error_influences(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        score_type: Optional[str] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None,
    ) -> pd.DataFrame:
        """Get the error QIIs/shapley-values associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the total number of points for local projects and the setting for "Number of default influences" for remote projects.
            score_type: The score type of error influences to retrieve. If None, infers error score type based on project configuration. Defaults to None.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
        Returns:
            The QIIs/shapley-values associated with the current data-split.
        """
        pass

    def add_model_error_influences(
        self,
        error_influence_data: pd.DataFrame,
        score_type: Optional[str] = None,
        *,
        id_col_name: str = None,
        data_split_name: Optional[str] = None,
        background_split_name: Optional[str] = None,
        timestamp_col_name: Optional[str] = None,
        influence_type: Optional[str] = None
    ):
        """Adds error influence of given score type for the current model and split.

        Args:
            error_influence_data: Feature influence data to add. Must be aligned with the pre-processed data of the given split.
            score_type: Score type of the influences, either `mean_absolute_error_for_classification` or `mean_absolute_error_for_regression`, depending on project type. Inferred if None. Defaults to None.
            id_col_name: Column name for the unique identifier of each data point.
            data_split_name: Data split that influences are associated with. If None, defaults to split set in the current context.
            background_split_name: Background data split that influences are computed against. If None, defaults to the base split of the data collection (if this is not explicitly set, it is an ingested split of type "all" or "train").
            influence_type: Influence algorithm used to generate influences.
                If influence type of project is set to "truera-qii", assumes that explanations are generated using truera-qii. 
                If influence type of project is set to "shap", then `influence_type` must be passed in as one of ["tree-shap-tree-path-dependent", "tree-shap-interventional", "kernel-shap"].
            timestamp_col_name: Column name for the timestamp of each data point. Must be a column of type string or pd.DateTime. Defaults to None.
        """
        pass

    @abstractmethod
    def attach_packaged_python_model_object(
        self, model_object_dir: str, verify_model: bool = True
    ):
        """Attaches a pre-serialized and packaged executable model object to the current model, which must be virtual.
        This effectively "converts" the virtual model to a non-virtual one, as the system can now call the model to generate predictions.
        Args:
            model_object_dir: Directory where packaged model object is located.
            verify_model: Locally verify the model is packaged properly and can operate on existing split data. Defaults to True.
        """
        pass

    @abstractmethod
    def attach_python_model_object(
        self,
        model_object: Any,
        additional_pip_dependencies: Optional[Sequence[str]] = None,
        verify_model: bool = True,
    ):
        """Attaches the provided executable model object to the current model, which must be virtual.
        This effectively "converts" the virtual model to a non-virtual one, as the system can now call the model to generate predictions.
            Supported Model Frameworks: sklearn, xgboost, catboost, lightgbm, pyspark (tree models only).
            If you cannot ingest your model object via this function due to custom logic, feature transforms, etc., see `attach_packaged_python_model_object()`.

            [ALPHA] For frameworks that are not yet supported, or for custom model implementations the prediction
            function for the model can be provided as the model.
            For binary classifiers, the prediction function should accept a pandas DataFrame as input and produce
            a pandas DataFrame as output with the class probabilities and [0, 1] as the column header.
            For regression models, the prediction function should accept a pandas DataFrame as input and produce
            the result as a pandas DataFrame with "Result" as the column header.
            All required dependencies to execute the prediction function should be provide as additional_pip_dependencies.
            For example:
            ```python
            def predict(df):
                return pd.DataFrame(my_model.predict_proba(df, validate_features=False), columns=[0, 1])
            tru.add_python_model("my_model", predict, additional_pip_dependencies=["xgboost==1.3.1", "pandas==1.1.1"])
            ```
        Args:
            model_object: The Python model object or the prediction function to attach.
                Supported frameworks are catboost, lightgbm, sklearn and xgboost, and tree-based PySpark models. For prediction function, please see the description above.
            additional_pip_dependencies: List of pip dependencies required to execute the model object. If the model object
                is from a supported framework, the pip dependency for that framework is automatically inferred. If a prediction function is provided as the model,
                additional pip dependencies are not automatically inferred and must be explicitly provided.
                Defaults to None. Example: ["pandas==1.1.1", "numpy==1.20.1"]
            verify_model: [Alpha] Locally verify the model is packaged properly and can operate on existing split data. Defaults to True.
        """
        pass

    @abstractmethod
    def add_feature_metadata(
        self,
        feature_description_map: Optional[Mapping[str, str]],
        group_to_feature_map: Optional[Mapping[str, Sequence[str]]] = None,
        missing_values: Optional[Sequence[str]] = None,
        force_update: bool = False
    ):
        """Upload metadata describing features and feature groupings to the server.
        Args:
            feature_description_map: Map from pre-processed feature name, as provided in the data, to the description of the feature.
            group_to_feature_map: Grouping of pre-features for analysis purposes. A key of the map will be a name for the collection of pre-features mapped to. If given, all pre-features must appear in exactly one of the map's value lists.
            missing_values: List of strings to be registered as missing values when reading split data.
            force_update: Overwrite any existing feature metadata.
        """
        pass

    @abstractmethod
    def _get_pre_to_post_feature_map(
        self
    ) -> Optional[Mapping[str, Sequence[str]]]:
        pass

    def get_feature_names(self) -> Sequence[str]:
        """Get the feature names associated with the current data-collection.
        Returns:
            Sequence[str]: Feature names.
        """
        return list(self.get_xs(0, 10).columns)

    def get_xs(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        extra_data: bool = False,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> pd.DataFrame:
        """Get the inputs/data/x-values associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the total number of points for local projects and the setting for "Number of default influences" for remote projects.
            extra_data: Include extra data columns in the response. Defaults to False.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
        Returns:
            The inputs/data/x-values associated with the current data-split.
        """
        pass

    def get_ys(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> pd.DataFrame:
        """Get the targets/y-values associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the total number of points for local projects and the setting for "Number of default influences" for remote projects.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
        Returns:
            The targets/y-values associated with the current data-split.
        """
        pass

    def get_ys_pred(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None,
        wait: bool = True
    ) -> pd.DataFrame:
        """Get the model predictions associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the total number of points for local projects and the setting for "Number of default influences" for remote projects.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
            wait: Whether to wait for the job to finish. Defaults to True.
        Returns:
            The model predictions associated with the current data-split.
        """
        self._ensure_base_data_split()
        return self.get_explainer(self.get_context()["data-split"]).get_ys_pred(
            start,
            stop,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group,
            wait=wait
        )

    @abstractmethod
    def get_feature_influences(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        score_type: Optional[str] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None,
    ) -> pd.DataFrame:
        """Get the QIIs/shapley-values associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the project setting for "Number of default influences".
            score_type: The score type to use when computing influences. If None, uses default score type of project. Defaults to None. For a list of valid score types, see `list_valid_score_types`.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
        Returns:
            The QIIs/shapley-values associated with the current data-split.
        """
        pass

    @abstractmethod
    def get_explainer(
        self,
        base_data_split: Optional[str] = None,
        comparison_data_splits: Optional[Sequence[str]] = None
    ) -> Explainer:
        """Get the explainer associated with the TruEra workspace.
        Args:
            base_data_split: The name of the data split to set as the base split for explainer operations.
            comparison_data_splits: The name(s) of the data splits to set as the comparison splits for explainer operations.

        Returns:
            Explainer: Explainer for current context of the TruEra workspace.
        """
        pass

    @abstractmethod
    def add_segment_group(
        self, name: str, segment_definitions: Mapping[str, str]
    ) -> None:
        """[Alpha] Create a segment group where each segments is defined by an SQL expression.
        Args:
            name: The name of the segment group.
            segment_definitions: A dictionary containing the name of the segment and an SQL expression that defines the segment. Supported expressions:
                    `=`  : filters for equality, ex: amount = 1000
                    `!=` : filters for inequality, ex: amount != 1000
                    `<`  : filters for less-than, ex: amount < 1000
                    `<=` : filters for less-than-or-equal, ex: amount <= 1000
                    `>`  : filters for greater-than, ex: amount > 1000
                    `>=` : filters for great-than-or-equal, ex: amount >= 1000
                    `NOT`: filters records if the inner condition is not true, ex: NOT(amount >= 1000)
                    `AND`: filters records if both the conditions are true, ex: (amount >= 1000) AND (state = 'WA')
                    `OR` : filters records if any of the two conditions is true, ex: (amount >= 1000) OR (state = 'WA')
                String literals should be within quotes (''), numeric literals should not have quotes('').
                Left side of a binary expression should be either column name (without quotes) or one of the special keywords (see below for the list of supported special keywords). Right side of an expression should be a literal.
                For example, (amount < salary) is not a valid expression, as both left and right side of the expression are column-names.
                Supported special keywords:
                    _DATA_GROUND_TRUTH : filters using the data label, ex: _DATA_GROUND_TRUTH == 1
                    _MODEL_<score_type>: filters using the <score_type> of the model where <score_type> is "REGRESSION" for regression models or one of ["PROBITS", "LOGITS", "CLASSIFICATION"] for classification models, ex: _MODEL_REGRESSION >= 5
                    _MODEL_<score_type>$<model_name>: filters using the <score_type> of the model with name <model_name> where <score_type> is "REGRESSION" for regression models or one of ["PROBITS", "LOGITS", "CLASSIFICATION"] for classification models, example to filter by "REGRESSION" score of "model_a": _MODEL_REGRESSION$model_a >= 5
                    _RANKING_GROUP_ID: filters using the ranking group id, ex: _RANKING_GROUP_ID = "group_id_1"
        
        Examples:
        ```python
        >>> tru.set_project("Project Name")
        >>> tru.set_data_collection("Data Collection Name")

        # Add a segment group for Sex
        >>> tru.add_segment_group(name = "Sex", segment_definitions = {"Male": "Sex == 'Male'", "Female": "Sex == 'Female'"})

        # Add a segment group for Language at Home
        >>> tru.add_segment_group("Language at Home", {"English": "LANX == 1", "Not English": "LANX == 2"})
        ```
        """
        pass

    @abstractmethod
    def set_as_protected_segment(
        self, segment_group_name: str, segment_name: str
    ):
        """Sets the provided segment as a "protected" segment. This enables fairness analysis for this segment.

        Args:
            segment_group_name : Name of segment group.
            segment_name: Name of segment in provided segment group.

        Examples:
        ```python
        >>> tru.set_project("Project Name")
        >>> tru.set_data_collection("Data Collection Name")

        # Add a segment group for Sex
        >>> tru.add_segment_group(name = "Sex", segment_definitions = {"Male": "Sex == 'Male'", "Female": "Sex == 'Female'"})

        # Set the Female Segment as a Protected Segment
        >>> tru.set_as_protected_segment(segment_group_name = "Sex", segment_name = "Female")
        ```
        """
        pass

    @abstractmethod
    def delete_segment_group(self, name: str) -> None:
        """[Alpha] Delete a segment group.
        Args:
            name: The name of the segment group.
        """
        pass

    @abstractmethod
    def get_segment_groups(self) -> Mapping[str, Mapping[str, str]]:
        """[Alpha] Get all segment groups associated with the current TruEra workspace, along with their respective segments.
        Returns:
            Mapping[str, Mapping[str, str]]: Mapping of segment group names to the corresponding segment group definition.
        """
        pass

    @abstractmethod
    def get_ingestion_client(self) -> IngestionClient:
        """[Alpha] Get the data ingestion client associated with the TruEra workspace. Valid only for "remote" workspace.
        The ingestion client can be used to pull data from different data sources into TruEra to perform analytics.
        Raises:
            ValueError: Raised if no project is associated with the current workspace. Use set_project
                to set the correct project.
            ValueError: Raised if no data collection is associated with the current workspace. Use set_data_collection
                to set the correct data collection.
            ValueError: Raised if the current project is a local project.
        Returns:
            IngestionClient: IngestionClient for current context of the TruEra workspace.
        """
        pass

    @abstractmethod
    def get_ingestion_operation_status(
        self,
        operation_id: Optional[str] = None,
        idempotency_id: Optional[str] = None
    ) -> dict:
        """Retrieve ingestion operation status by providing either the operation id or the idempotency id.
        In the case an idempotency id which is associated with no operation id is used, a `NotFoundError` is raised, 
        which means this idempotency id is not used before.
        Args:
            operation_id (Optional[str], optional): Defaults to None.
            idempotency_id (Optional[str], optional): Defaults to None.

        Returns:
            dict: Contains project_name, operation_started_time, operation_status, operation_id, split_id. 
        """
        pass

    def add_credential(
        self,
        name: str,
        secret: str,
        identity: Optional[str] = None
    ) -> Credential:
        """[Alpha] Add a new credential to TruEra product. The credential is saved in a secure manner and is used
        to authenticate with the data source to be able to perform various operations (read, filter, sample etc.).
        Args:
            name: Friendly name of the credential.
            secret: The secret to be stored.
            identity: Identity portion of the secret. Not needed in all cases. Defaults to None.
        Returns:
            Credential: Returns an object with the credential name and id. The secret is not stored in this object.
        """
        pass

    def get_credential_metadata(self, name: str) -> Credential:
        """[Alpha] Get metadata about a credential in the TruEra product. The credential details are not returned.
        Args:
            name: Friendly name of the credential.
        Returns:
            Credential: Returns an object with the credential name and id.
        """
        pass

    def delete_credential(self, name) -> None:
        """[Alpha] Removes a credential from the TruEra product.
        Args:
            name: Friendly name of the credential.
        """
        pass

    def add_data_source(
        self,
        name: str,
        uri: str,
        credential:
        Credential = None,  # TODO(AB#3679) take cred name as the input
        **kwargs
    ) -> Table:
        """Add a new data source in the system.
        Args:
            name (str): Friendly name of the data source.
            uri (str): URI describing the location of the data source.
                For local files this can be file:///path/to/my/file or /path/to/my/file
                For files stored in Azure Storage Blobs the expected path is wasb://container@account.blob.core.windows.net/blob
            credential (Credential, optional): Provide the credential object if the data source requires authentication to read from it. Defaults to None.
            **format (str):The format in which the file (local) or blob (AWS S3, Azure WASB etc.) are stored in.
            **first_row_is_header (bool): For text based delimited files (csv, tsv etc.), indicates if the first row provides header information. Defaults to True.
            **column_delimiter (str): For text based delimited files (csv, tsv etc.), provides the delimiter to separate column values. Defaults to ','.
            **quote_character (str): For text based delimited files (csv, tsv etc.), if quotes are used provide the quote character. Defaults to '"'.
            **null_value (str): For text based delimited files (csv, tsv etc.), the string that signifies null value. Defaults to 'null'.
            **empty_value (str): For text based delimited files (csv, tsv etc.), the string that signifies empty value. Defaults to '""'.
            **date_format (str): For text based delimited files (csv, tsv etc.), if any column has date time, provide the format string. Defaults to 'yyyy-MM-dd-HH:mm:ssZZ'.
            **account_key (str): For reading from Azure Storage Blob (WASB), provide the account_key to be used to read the blob. Not required if `credential` object is provided.
            **database_name (str): For reading from sql databases, provide the database name to use. Required for MySQL or Hive data source.
            **table_name (str): For reading from sql databases, provide the table name to use. Required for MySQL or Hive data source.
        Raises:
            ValueError: Raised if the current project is a local project.
        Returns:
            Table: Returns a Table object which allows interaction with the attached data.
        """
        pass

    def get_data_source(self, name) -> Table:
        """ Get a data source that was already created in the system.
        Args:
            name (str): The friendly name of the data source.
        Raises:
            ValueError: Raised if the current project is a local project.
        Returns:
            Table: Returns a Table object which allows interaction with the attached data.
        """
        pass

    def get_data_sources(self) -> Sequence[str]:
        """ Get list of data sources attached in the current project.
        Raises:
            ValueError: Raised if the current project is a local project.
        """
        pass

    def delete_data_source(self, name: str):
        """ Delete a data source that was already created in the system.
        Args:
            name (str): The friendly name of the data source.
        """
        pass

    @abstractmethod
    def set_influences_background_data_split(
        self,
        data_split_name: str,
        data_collection_name: Optional[str] = None
    ) -> None:
        """Set the background data split used for computing feature influences.
        Args:
            data_split_name: Name of the data split.
            data_collection_name: (Optional) Name of the data collection. Defaults to the current data collection in context.
        """
        pass

    @abstractmethod
    def get_influences_background_data_split(
        self, data_collection_name: Optional[str] = None
    ) -> str:
        """Get the background data split used for computing feature influences.
        Args:
            data_collection_name: (Optional) Name of the data collection. Defaults to the current data collection in context.
        Returns:
            str: Name of the background data split.
        """
        pass

    def _validate_get_model_threshold(self):
        self._ensure_project()
        self._ensure_model()
        if self._get_output_type() == "regression":
            raise ValueError("Regression models do not have model thresholds!")

    @abstractmethod
    def get_model_threshold(self) -> float:
        """Gets the model threshold for the currently set model and score type in the TruEra workspace.
        Returns:
            Optional[float]: The model threshold.
        """
        pass

    @abstractmethod
    def update_model_threshold(self, classification_threshold: float) -> None:
        """Update the classification threshold for the model associated with the TruEra workspace. A model score (probits, logits) that is greater than or equal to the threshold is assigned a positive classification outcome.
        Args:
            classification_threshold: New threshold to update. Ignored for regression models.
        """
        pass

    @abstractmethod
    def get_context(self) -> Mapping[str, str]:
        pass

    @abstractmethod
    def reset_context(self):
        pass

    def activate_client_setting(self, setting_name: str) -> None:
        """
        Activates a setting for client side behavior.
        Args:
            setting_name: Client setting to activate.
        """
        context = LocalContextStorage.get_workspace_env_context()
        context.set_feature_switch_value(setting_name, True)

    def deactivate_client_setting(self, setting_name: str) -> None:
        """
        Deactivates a setting for client side behavior.
        Args:
            setting_name: Client setting to deactivate.
        """
        context = LocalContextStorage.get_workspace_env_context()
        context.set_feature_switch_value(setting_name, False)

    def get_client_setting_value(self, setting_name: str) -> bool:
        """
        Gets current value of a setting for client side behavior.
        """
        context = LocalContextStorage.get_workspace_env_context()
        return context.get_feature_switch_value(setting_name)

    def _validate_score_type(self, score_type: str):
        if score_type is None:
            raise ValueError(
                "Must specify `score_type` when creating projects!"
            )
        if score_type not in self.list_valid_score_types():
            raise ValueError(
                f"Invalid `score_type` of {score_type} was provided."
            )

    def _validate_set_project(
        self,
        project: str,
    ):
        if not project in self.get_projects():
            raise ValueError(
                f"No such project \"{project}\"! See `add_project` to add it."
            )

    def _validate_add_project(
        self,
        project: str,
        score_type: str,
        input_type: Optional[str] = "tabular",
        num_default_influences: Optional[int] = None
    ):
        # Returns whether project already exists.
        if project in self.get_projects():
            raise AlreadyExistsError(f"Project \"{project}\" already exists!")
        workspace_validation_utils.ensure_valid_identifier(project)
        if not score_type:
            raise ValueError(
                "Must specify `score_type` when creating projects!"
            )
        if score_type not in _STRING_TO_QOI:
            raise ValueError(
                f"\"{score_type}\" is not a valid score type! Must be one of {list(filter(lambda type: _STRING_TO_QOI[type] != qoi_pb.GENERATIVE_TEXT,_STRING_TO_QOI.keys()))}."
            )
        if input_type not in _STRING_TO_INPUT_DATA_FORMAT:
            raise ValueError(
                f"\"{input_type}\" is not a valid input data type! Must be one of {list(_STRING_TO_INPUT_DATA_FORMAT.keys())}."
            )
        if num_default_influences is not None and num_default_influences <= 0:
            raise ValueError("`num_default_influences` must be positive!")

    def _validate_add_model(self, model_name: str):
        self._ensure_project()
        self._ensure_data_collection()
        if model_name in self.get_models():
            raise AlreadyExistsError(f"Model \"{model_name}\" already exists!")
        workspace_validation_utils.ensure_valid_identifier(model_name)
        input_type = self._get_input_type()
        if workspace_validation_utils.is_nontabular_project(input_type):
            raise ValueError(
                f"This function is not supported for `{input_type}` projects. Use `add_nn_model` instead."
            )

    def _validate_add_nn_model(self, model_name: str):
        self._ensure_project()
        self._ensure_data_collection()
        if model_name in self.get_models():
            raise AlreadyExistsError(f"Model \"{model_name}\" already exists!")
        workspace_validation_utils.ensure_valid_identifier(model_name)

    def _validate_add_data_split_generic(
        self,
        data_split_name: str,
        *,
        post_data: Optional[Union[pd.DataFrame, Table, str]] = None,
        label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
        prediction_data: Optional[pd.DataFrame] = None,
        feature_influence_data: Optional[pd.DataFrame] = None,
        label_col_name: Optional[str] = None,
        split_type: Optional[str] = "all",
        background_split_name: Optional[str] = None,
        score_type: Optional[str] = None,
    ):
        self._ensure_project()
        self._ensure_data_collection()
        if prediction_data is not None or feature_influence_data is not None:
            self._ensure_model()
            workspace_validation_utils.validate_score_type(
                self._get_score_type(), score_type
            )

        workspace_validation_utils.validate_add_data_split_generic(
            data_split_name,
            post_data=post_data,
            label_data=label_data,
            feature_influence_data=feature_influence_data,
            label_col_name=label_col_name,
            background_split_name=background_split_name,
            input_type=self._get_input_type(),
            data_splits=self.get_data_splits(),
            feature_transform_type=self.
            _get_feature_transform_type_for_data_collection(),
            infl_type=self.get_influence_type()
        )

    def _validate_schema_matches_score_type(self, schema: Schema):
        """Validate provided schema is compatible with the provided project score type."""
        self._ensure_project()
        project_score_type = self._get_score_type()
        if project_score_type == "classification" or project_score_type == "logits" or project_score_type == "probits":
            if isinstance(schema.score_columns, RegressionColumns):
                raise ValueError(
                    f"Schema contains regression score columns but the project score type is {project_score_type}."
                )
        elif project_score_type == "regression":
            if isinstance(schema.score_columns, BinaryClassificationColumns):
                raise ValueError(
                    f"Schema contains classification score columns but the project score type is {project_score_type}."
                )

    def _validate_add_data_split(
        self,
        data_split_name: str,
        pre_data: Union[pd.DataFrame, Table, str],
        post_data: Optional[pd.DataFrame] = None,
        label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
        prediction_data: Optional[pd.DataFrame] = None,
        feature_influence_data: Optional[pd.DataFrame] = None,
        background_split_name: Optional[str] = None,
        label_col_name: Optional[str] = None,
        id_col_name: Optional[str] = None,
        ranking_group_id_col_name: Optional[str] = None,
        ranking_item_id_col_name: Optional[str] = None,
        timestamp_col_name: Optional[str] = None,
        extra_data_df: Optional[pd.DataFrame] = None,
        split_type: Optional[str] = "all",
        split_mode: sm_pb.SplitMode = sm_pb.SplitMode.SPLIT_MODE_INVALID,
        score_type: Optional[str] = None,
        **kwargs
    ):

        self._validate_add_data_split_generic(
            data_split_name,
            post_data=post_data,
            label_data=label_data,
            prediction_data=prediction_data,
            feature_influence_data=feature_influence_data,
            label_col_name=label_col_name,
            split_type=split_type,
            background_split_name=background_split_name,
            score_type=score_type
        )
        if workspace_validation_utils.is_tabular_project(
            self._get_input_type()
        ):
            if split_mode != sm_pb.SplitMode.SPLIT_MODE_PREDS_REQUIRED and pre_data is None:
                raise ValueError(
                    f"`pre_data` must be provided for this configuration."
                )
            if split_mode != sm_pb.SplitMode.SPLIT_MODE_PREDS_REQUIRED and not isinstance(
                pre_data, pd.DataFrame
            ):
                raise ValueError(
                    f"`pre_data` must be of type `pandas.DataFrame`! Was {type(pre_data)}."
                )
        workspace_validation_utils.validate_split_for_dataframe(
            self.logger,
            pre_data=pre_data,
            post_data=post_data,
            label_data=label_data,
            label_col_name=label_col_name,
            extra_data_df=extra_data_df,
            pre_to_post_feature_map=self._get_pre_to_post_feature_map(),
            output_type=self._get_output_type(),
            id_column_name=id_col_name,
            ranking_group_id_col_name=ranking_group_id_col_name,
            ranking_item_id_col_name=ranking_item_id_col_name,
            timestamp_col_name=timestamp_col_name,
            prediction_col_name=kwargs.get("prediction_col_name"),
            input_type=self._get_input_type(),
            split_mode=split_mode,
            model_set_in_context=bool(self.get_context().get("model"))
        )

    def _validate_add_data_split_from_data_source(
        self,
        data_split_name: str,
        *,
        pre_data: Union[Table, str],
        post_data: Optional[Union[Table, str]] = None,
        label_col_name: Optional[str] = None,
        extra_data: Optional[Union[Table, str]] = None,
        split_type: Optional[str] = "all",
        split_mode: sm_pb.SplitMode = sm_pb.SplitMode.SPLIT_MODE_INVALID,
        **kwargs
    ):
        self._validate_add_data_split_generic(
            data_split_name,
            post_data=post_data,
            label_data=None,
            label_col_name=label_col_name,
            split_type=split_type
        )
        if split_mode == sm_pb.SplitMode.SPLIT_MODE_PREDS_REQUIRED:
            if pre_data is not None:
                raise ValueError(
                    "`pre_data` must be None if adding a split without feature data!"
                )
            return
        if split_mode != sm_pb.SplitMode.SPLIT_MODE_PREDS_REQUIRED and not isinstance(
            pre_data, (Table, str)
        ):
            raise ValueError(
                f"`pre_data` must be of type `Table` or `str`! Was {type(pre_data)}."
            )

        #TODO(AB#5195): Validate upload from data source given existing feature map on backend
        for arg, arg_name in [
            (extra_data, "extra_data"), (post_data, "post_data")
        ]:
            if arg is not None:
                #TODO(AB#5143): Support post/extra data for remote data sources.
                raise NotImplementedError(
                    f"Ingesting data split with `{arg_name}` is not yet supported for data sources!"
                )

        if kwargs.get("prediction_col_name"):
            self._ensure_model()

    def _validate_additional_modules(
        self, additional_modules: Optional[Sequence[Any]]
    ):
        if additional_modules is not None and not isinstance(
            additional_modules, (list, tuple)
        ):
            raise ValueError(
                f"`additional_modules` must be a sequence of modules!"
            )

    def _validate_add_nn_data_split(
        self,
        data_split_name: str,
        *,
        pre_data: Optional[pd.DataFrame] = None,
        label_data: Optional[pd.DataFrame] = None,
        id_col_name: Optional[str] = None,
        extra_data_df: Optional[pd.DataFrame] = None,
        split_type: Optional[str] = None
    ):
        if workspace_validation_utils.is_tabular_project(
            self._get_input_type()
        ):
            raise ValueError(
                "Adding split using `add_nn_data_split` is not supported for `tabular` project."
            )
        self._validate_add_data_split(
            data_split_name,
            pre_data=pre_data,
            label_data=label_data,
            id_col_name=id_col_name,
            extra_data_df=extra_data_df,
            split_type=split_type,
            score_type=self._get_score_type()
        )

    def _validate_set_data_collection(self, data_collection_name: str):
        # Returns whether data collection already exists.
        workspace_validation_utils.ensure_valid_identifier(data_collection_name)
        self._ensure_project()
        if data_collection_name not in self.get_data_collections():
            raise ValueError(
                f"No such data collection \"{data_collection_name}\"! See `add_data_collection` to add it."
            )

    def _validate_explainer_context(
        self, context: Mapping[str, Union[Sequence[str], str]]
    ):
        keys = ["project", "model", "data-collection", "data-split"]
        for key in keys:
            if key not in context:
                raise ValueError(f"Context does not contain {key} key!")
            if not context[key]:
                raise ValueError(
                    f"Provided {key} cannot be set to \"{context[key]}\"!"
                )

    def _create_base_context(
        self,
        project: Optional[str] = None,
        model: Optional[str] = None,
        data_collection: Optional[str] = None,
        data_split: Optional[str] = None
    ) -> Mapping[str, Union[Sequence[str], str]]:
        return {
            "project": project or "",
            "data-collection": data_collection or "",
            "data-split": data_split or "",
            "model": model or "",
        }

    def _verify_nn_wrappers(
        self, verify_helper: "VerifyHelper", logger: logging.Logger
    ) -> None:
        """ Passes the wrapper implementations to the validation step.
        Args:
            verify_helper (VerifyHelper): A verification helper object containing model data, wrappers, configurations, and test cases.
            logger (logging.Logger): The logger.
        """
        from truera.client.cli.verify_nn_ingestion import verify
        if verify_helper.attr_config is None:
            raise ValueError(
                f"Please pass in an `AttributionConfiguration` to the attr_config parameter"
            )
        verify.verify_run(verify_helper, logger=logger)

    @abstractmethod
    def _get_score_type(self):
        pass

    @abstractmethod
    def _get_input_type(self):
        pass

    def _get_output_type(self) -> str:
        return get_output_type_from_score_type(self._get_score_type())

    @abstractmethod
    def get_nn_user_configs(
        self
    ) -> Union['AttributionConfiguration', 'RNNUserInterfaceConfiguration']:
        """
        Get NN user configurations for project and model set in the current context.

        Example:
        ```python
        >>> from truera.client.nn.client_configs import NLPAttributionConfiguration
        >>> attr_config = NLPAttributionConfiguration(
        >>>     token_embeddings_layer=token_embeddings_layer_name,
        >>>     token_embeddings_anchor=token_embeddings_layer_tensor_anchor,
        >>>     n_output_neurons=n_output_neurons,
        >>>     n_metrics_records=n_metrics_records,
        >>>     rebatch_size=rebatch_size,)

        # View the ingested config after add_nn_model in NN Ingestion...
        >>> tru.get_nn_user_configs()
        ```

        Returns:
            Union[AttributionConfiguration, RNNUserInterfaceConfiguration]: NN user config.
        """
        pass

    @abstractmethod
    def update_nn_user_config(
        self, config: Union['AttributionConfiguration',
                            'RNNUserInterfaceConfiguration']
    ):
        """
        Update NN user configurations for project and model set in the current context.

        Example:
        ```python
        # If you need to make changes to the attributions config after you have run add_nn_model in NN Ingestion...
        >>> from truera.client.nn.client_configs import NLPAttributionConfiguration
        >>> updated_attr_config = NLPAttributionConfiguration(
        >>>     token_embeddings_layer=token_embeddings_layer_name,
        >>>     token_embeddings_anchor=token_embeddings_layer_tensor_anchor,
        >>>     n_output_neurons=n_output_neurons,
        >>>     n_metrics_records=n_metrics_records,
        >>>     rebatch_size=rebatch_size,
        >>> )

        >>> tru.update_nn_user_config(updated_attr_config)
        >>> tru.get_nn_user_configs() # Will return the updated attr_config
        ```

        Args:
            config: Config to set.
        """
        pass

    @abstractmethod
    def add_model_metadata(
        self,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        overwrite: bool = False
    ) -> None:
        """
        Add or update metadata for the current model in context.
        Args:
            train_split_name: The name of the train split of the model
            train_parameters: Train parameters of the model. Ex. {'n_estimators": 10}"}
            overwrite: Overwrite existing values (if exist).
        """
        pass

    @abstractmethod
    def delete_model_metadata(self) -> None:
        """ Unset `train_split_name` and `train_parameters` for the current model in context.
        """
        pass

    @abstractmethod
    def get_model_metadata(self) -> Mapping[str, Union[str, Mapping[str, str]]]:
        """ Get model metadata for the current model in context.
        """
        pass

    @abstractmethod
    def _get_model_metadata(
        self, model_name: str
    ) -> Mapping[str, Union[str, Mapping[str, str]]]:
        """ Get model metadata for the given `model_name`
        """
        pass

    @abstractmethod
    def _get_xs_postprocessed(
        self,
        start: int = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> pd.DataFrame:
        """Get the post-processed data associated with the current data-split.
        Note that, if you set the start and stop, the number of records returned will not be the exact number requested but in the neighborhood of the start and stop limit provided.
        Args:
            start: The lower bound (inclusive) of the index of points to include. Defaults to 0.
            stop: The upper bound (exclusive) of the index of points to include. Defaults to None which is interpreted as the total number of points for local projects and the setting for "Number of default influences" for remote projects.
            system_data: Include system data (e.g. timestamps) if available in response. Defaults to False.
            by_group: For ranking projects, whether to retrieve data by group or not. Ignored for non-ranking projects. Defaults to False.
            num_per_group: For ranking projects and when `by_group` is True, the number of points per group to return.
        Returns:
            The post-processed data associated with the current data-split.
        """
        pass

    def _get_current_active_project_name(self) -> str:
        return self.get_context()["project"]

    def _get_current_active_model_name(self) -> str:
        return self.get_context()["model"]

    def _get_current_active_data_collection_name(self) -> str:
        return self.get_context()["data-collection"]

    def _get_current_active_data_split_name(self) -> str:
        return self.get_context()["data-split"]

    def _ensure_project(self) -> str:
        project_name = self._get_current_active_project_name()
        if not project_name:
            raise ValueError("Set the current project using `set_project`")
        return project_name

    def _ensure_data_collection(self) -> str:
        data_collection_name = self._get_current_active_data_collection_name()
        if not data_collection_name:
            raise ValueError(
                "Set the current data_collection using `set_data_collection`"
            )
        return data_collection_name

    def _ensure_base_data_split(self) -> str:
        split_name = self._get_current_active_data_split_name()
        if not split_name:
            raise ValueError(
                "Set the current data_split using `set_data_split`"
            )
        return split_name

    def _ensure_model(self) -> str:
        model_name = self._get_current_active_model_name()
        if not model_name:
            raise ValueError("Set the current model using `set_model`")
        return model_name

    def _delete_empty_project(self):
        """Delete the currently set project non-recursively. This should only be called when all child models and data are deleted already.
        """
        pass

    def delete_project(self, project_name: Optional[str] = None):
        """Delete a project from the current TruEra workspace. This will only delete artifacts within the current location context (either local or remote).
        Args:
            project_name: Name of the project to be deleted. By default the currently set project will be deleted.
        """
        if project_name is None:
            raise ValueError("`project_name` must be set!")
        if project_name != self._get_current_active_project_name(
        ) and project_name not in self.get_projects():
            raise ValueError(f"Not a valid project: {project_name}!")
        with WorkspaceContextCleaner(self, delete_project=True):
            self.set_project(project_name)
            for model_name in self.get_models():
                self.delete_model(model_name, recursive=True)
            for data_collection_name in self.get_data_collections():
                self.delete_data_collection(
                    data_collection_name, recursive=True
                )
            self._delete_empty_project()

    def _validate_data_collection(self, data_collection_name: str) -> None:
        if data_collection_name not in self.get_data_collections():
            raise ValueError(
                f"Data collection \"{data_collection_name}\" does not exist!"
            )

    def _validate_add_segment_group(
        self, name: str, segment_definitions: Mapping[str, str]
    ) -> None:
        self._ensure_project()
        # Even though technically one can create a segment without data split, for safety we'll require data split
        # so that we can check that the features given in the segment_definitions are valid features
        self._ensure_data_collection()
        self._ensure_base_data_split()
        if not name:
            raise ValueError("Segment group name cannot be empty!")
        if not segment_definitions:
            raise ValueError("`segments_definitions` cannot be empty!")

    def _get_str_desc_of_segment_groups(
        self, segment_groups: Mapping[str, SegmentGroup]
    ) -> Mapping[str, Mapping[str, str]]:
        sg_description = {}
        for sg_name in segment_groups:
            sg_description[sg_name] = {}
            segments = segment_groups[sg_name].get_segments()
            for segment_name in segments:
                sg_description[sg_name][segment_name] = segments[
                    segment_name].ingestable_definition()
        return sg_description

    @abstractmethod
    def schedule_ingestion(self, raw_json: str, cron_schedule: str):
        """[Alpha] Schedule a new scheduled ingestion based off a JSON request tree.

        Templating:
            Templating is supported for uris, split names, and filter expessions for scheduled
            ingestion.  The scheduler passes in several variables and functions when evaluating the
            supported field, which can be accessed by using the syntax: ${<field>}.

            For example, to add the run date to the split name you can add the following suffix when
            submitting a split name to scheduled ingestion: "split_name_${formatDate("yyyy-MM-dd", now)}"

            Supported variables:
                - now: The Date of the run.
                - last: The Date of the last run.
                - lastSuccess: The Date of the last successful run.

            Supported functions:
                - uuid(): Generate a random v4 uuid.
                - formatDate(<format>, <date>): Format the given Date as a string.  Format follows
                    Java SimpleDateFormat (https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html).
                - epochMillis(<date>): The epoch millis of the given Date.

        Args:
            raw_json (str): The JSON string representation of the request tree.  To build a json
                string, you can use the serialize_split function.
            cron_schedule (str): The schedule for the periodic ingestion.  Follows cron unix format:
                ┌───────────── minute (0 - 59)
                │ ┌───────────── hour (0 - 23)
                │ │ ┌───────────── day of the month (1 - 31)
                │ │ │ ┌───────────── month (1 - 12)
                │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
                │ │ │ │ │                                   7 is also Sunday on some systems)
                │ │ │ │ │
                │ │ │ │ │
                * * * * *

                For example, to run a cron on the first of every month: "0 0 1 * *"


        Returns:
            str: A workflow_id for looking up the workflow.
        """
        pass

    @abstractmethod
    def get_scheduled_ingestion(
        self, workflow_id: str
    ) -> scheduled_pb.GetScheduleResponse:
        """[Alpha] Get the metadata about a scheduled ingestion from a workflow_id
        Args:
            workflow_id (str): The id of the scheduled ingestion workflow.
        Returns:
            GetScheduleResponse: Returns an object containing the request_template, schedule, and run_results of a workflow.
        """
        pass

    @abstractmethod
    def schedule_existing_data_split(
        self,
        split_name: str,
        cron_schedule: str,
        override_split_name: str = None,
        append: bool = True
    ):
        """[Alpha] Schedule a new scheduled ingestion based off an existing split.
        Args:
            split_name (str): The name of an already materialized split.
            cron_schedule (str): The schedule for the periodic ingestion.  Follows cron unix format:
                ┌───────────── minute (0 - 59)
                │ ┌───────────── hour (0 - 23)
                │ │ ┌───────────── day of the month (1 - 31)
                │ │ │ ┌───────────── month (1 - 12)
                │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
                │ │ │ │ │                                   7 is also Sunday on some systems)
                │ │ │ │ │
                │ │ │ │ │
                * * * * *

                For example, to run a cron on the first of every month: "0 0 1 * *"
            override_split_name (str): The name of the new splits to be created.  For information on
                templating, see the schedule_ingestion function.
        Returns:
            str: A workflow_id for looking up the workflow.
        """
        pass

    @abstractmethod
    def serialize_split(
        self,
        split_name: str,
        override_split_name: str = None,
    ) -> str:
        """[Alpha] Build a request tree represented as a JSON string.

        Templating:
            Templating is supported for uris, split names, and filter expressions for scheduled
            ingestion.  The scheduler passes in several variables and functions when evaluating the
            supported field, which can be accessed by using the syntax: ${<field>}.

            For example, to add the run date to the split name you can add the following suffix when
            submitting a split name to scheduled ingestion: "split_name_${formatDate("yyyy-MM-dd", now)}"

            Supported variables:
                - now: The Date of the run.
                - last: The Date of the last run.
                - lastSuccess: The Date of the last successful run.

            Supported functions:
                - uuid(): Generate a random v4 uuid.
                - formatDate(<format>, <date>): Format the given Date as a string.  Format follows
                    Java SimpleDateFormat (https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html).
                - epochMillis(<date>): The epoch millis of the given Date.

        Args:
            split_name (str): The name of an already materialized split.
            override_split_name (str): The optional name to replace the original split name.  For
                information on templating, see the schedule_ingestion function.
        Returns:
            str: A JSON string representing the request tree that can be used for scheduled ingestion.
        """
        pass

    @abstractmethod
    def cancel_scheduled_ingestion(self, workflow_id: str) -> str:
        """[Alpha] Cancel a scheduled ingestion.

        Args:
            workflow_id (str): The id of the scheduled ingestion workflow.
        Returns:
            Returns an object containing the canceled_on timestamp of a workflow.
        """
        pass

    @abstractmethod
    def list_scheduled_ingestions(
        self, last_key: str = None, limit: int = 50
    ) -> str:
        """[Alpha] List workflows.

        Args:
            last_key (str): The last id to fetch workflows after. Defaults to None.
            limit (int): The number of workflows to fetch. Defaults to 50.

        Returns:
            Returns a list of objects containing the workflow_id and active state of all workflows.
        """
        pass

    @abstractmethod
    def list_monitoring_tables(self) -> str:
        """lists monitoring tables relevant to current project

        Returns:
            Returns a json of objects containing the monitoring tables for a project
        """


class WorkspaceContextCleaner:
    """Utility to complete workspace operations but return to original context. 
    """

    def __init__(
        self,
        tru: BaseTrueraWorkspace,
        *,
        delete_project: bool = False,
        delete_data_collection: bool = False,
        delete_data_split: bool = False,
        delete_model: bool = False
    ):
        self.tru = tru
        self.context: Mapping[str, str] = {}
        self._delete_project = delete_project
        self._delete_data_collection = delete_data_collection
        self._delete_data_split = delete_data_split
        self._delete_model = delete_model

    def __enter__(self):
        self.context = self.tru.get_context()
        return self

    def _attempt_cleanup(self, *, raise_errors: bool):
        succeeded = True
        try:
            self.tru.set_project(self.context.get("project"))
        except:
            if raise_errors and not self._delete_project:
                raise ValueError(
                    f"Failed to reset project from temporary switch! Original project: {self.context['project']}"
                )
            succeeded = False
        if succeeded:
            succeeded_setting_data_collection = True
            try:
                self.tru.set_data_collection(
                    self.context.get("data-collection")
                )
            except:
                succeeded_setting_data_collection = False
                if raise_errors and not self._delete_data_collection:
                    raise ValueError(
                        f"Failed to reset data-collection from temporary switch! Original data-collection: {self.context['data-collection']}"
                    )
            if succeeded_setting_data_collection:
                try:
                    self.tru.set_data_split(self.context.get("data-split"))
                except:
                    if raise_errors and not self._delete_data_split:
                        raise ValueError(
                            f"Failed to reset data-split from temporary switch! Original data-split: {self.context['data-split']}"
                        )
            try:
                self.tru.set_model(self.context.get("model"))
            except:
                if raise_errors and not self._delete_model:
                    raise ValueError(
                        f"Failed to reset model from temporary switch! Original model: {self.context['model']}"
                    )

    def __exit__(self, exc_type, exc_val, exc_tb):
        # devnote: we could check that these projects, splits etc. still exist before setting them
        # but we do this validation in the setters anyways.
        # wrapping in try-catches to avoid duplicate calls to list/validate artifact names.

        # If there was an error try to reset the context as best we can and propagate the error.
        if exc_val:
            self._attempt_cleanup(raise_errors=False)
            raise exc_val
        # If there was no error to propagate reset the context.
        self.tru.reset_context()
        self._attempt_cleanup(raise_errors=True)
        return True
