from datetime import datetime
import importlib.util
import itertools
import logging
import os
import shutil
import tempfile
from typing import Any, Mapping, Optional, Sequence, Union
from urllib.parse import quote
from urllib.parse import urlparse
import uuid

import cloudpickle
from google.protobuf.json_format import MessageToJson
import numpy as np
import pandas as pd

from truera.client.base_truera_workspace import BaseTrueraWorkspace
from truera.client.base_truera_workspace import WorkspaceContextCleaner
# TODO: cli_utils needs to be refactored and this dependency should be removed
from truera.client.cli.cli_utils import _map_split_type
from truera.client.cli.cli_utils import format_remaining_list
from truera.client.cli.cli_utils import ModelType
from truera.client.client_utils import EXPLANATION_ALGORITHM_TYPE_TO_STR
from truera.client.client_utils import get_string_from_qoi_string
from truera.client.client_utils import InvalidArgumentCombinationException
from truera.client.client_utils import validate_model_metadata
from truera.client.data_source_utils import best_effort_remove_temp_files
from truera.client.errors import MetadataNotFoundException
from truera.client.errors import NotFoundError
from truera.client.feature_client import FeatureClient
from truera.client.ingestion import add_data
from truera.client.ingestion import ColumnSpec
from truera.client.ingestion import ModelOutputContext
from truera.client.ingestion.constants import PROD_DATA_SPLIT_NAME
from truera.client.ingestion.schema import Schema
from truera.client.ingestion.schema import schema_to_proto
from truera.client.ingestion.schema import schema_to_schemas_to_register
from truera.client.ingestion.sdk_model_packaging import CatBoostModelPackager
from truera.client.ingestion.sdk_model_packaging import LightGBMModelPackager
from truera.client.ingestion.sdk_model_packaging import ModelPredictPackager
from truera.client.ingestion.sdk_model_packaging import PySparkModelPackager
from truera.client.ingestion.sdk_model_packaging import SklearnModelPackager
from truera.client.ingestion.sdk_model_packaging import \
    SklearnPipelineModelPackager
from truera.client.ingestion.sdk_model_packaging import XgBoostModelPackager
from truera.client.ingestion.util import BaseColumnSpec
from truera.client.ingestion.util import column_spec_from_kwargs
from truera.client.ingestion.util import ColumnSpec
from truera.client.ingestion.util import infer_model_output_context
from truera.client.ingestion_client import IngestionClient
from truera.client.ingestion_client import Table
from truera.client.intelligence.remote_data_profiler import RemoteDataProfiler
from truera.client.intelligence.remote_explainer import RemoteExplainer
from truera.client.intelligence.remote_nlp_explainer import RemoteNLPExplainer
from truera.client.intelligence.remote_tester import RemoteTester
from truera.client.model_preprocessing import PipDependencyParser
from truera.client.model_preprocessing import prepare_template_model_folder
from truera.client.model_preprocessing import verify_python_model_folder
from truera.client.nn import wrappers as base
from truera.client.nn.client_configs import AttributionConfiguration
from truera.client.nn.client_configs import NLPAttributionConfiguration
from truera.client.nn.client_configs import RNNAttributionConfiguration
from truera.client.nn.client_configs import RNNUserInterfaceConfiguration
from truera.client.nn.wrappers import MODEL_LOAD_WRAPPER_SAVE_NAME
from truera.client.nn.wrappers import MODEL_RUN_WRAPPER_SAVE_NAME
from truera.client.nn.wrappers import nlp
from truera.client.nn.wrappers import SPLIT_LOAD_WRAPPER_SAVE_NAME
from truera.client.public.communicator.http_communicator import \
    AlreadyExistsError
from truera.client.public.communicator.http_communicator import \
    NotSupportedError
from truera.client.services.aiq_client import AiqClient
from truera.client.services.artifact_interaction_client import \
    ArtifactInteractionClient
from truera.client.services.artifact_interaction_client import DataCollection
from truera.client.services.artifact_interaction_client import \
    DataCollectionContainer
from truera.client.services.artifact_interaction_client import Model
from truera.client.services.artifact_interaction_client import Project
from truera.client.services.artifact_repo_client_factory import get_ar_client
from truera.client.services.artifactrepo_client import ArtifactType
from truera.client.services.configuration_service_client import \
    ConfigurationServiceClient
from truera.client.services.data_service_client import DataServiceClient
from truera.client.services.monitoring_control_plane_client import \
    MonitoringControlPlaneClient
from truera.client.services.mrc_client import MrcClient
from truera.client.services.query_service_client import QueryServiceClient
from truera.client.services.rbac_service_client import RbacServiceClient
from truera.client.services.scheduled_ingestion_client import \
    ScheduledIngestionClient
from truera.client.services.streaming_ingress_client import \
    StreamingIngressClient
from truera.client.services.user_analytics_service_client import \
    AnalyticsClientMode
from truera.client.services.user_analytics_service_client import \
    UserAnalyticsServiceClient
from truera.client.services.user_manager_service_client import \
    UserManagerServiceClient
from truera.client.truera_authentication import TrueraAuthentication
from truera.client.truera_workspace_utils import create_temp_file_path
from truera.client.truera_workspace_utils import format_connection_string
from truera.client.util import workspace_validation_utils
from truera.client.util.data_split.pd_data_split_path_container import \
    PandasDataSplitPathContainer
from truera.client.util.validate_model_packaging_sdk import \
    validate_packaged_python_model
from truera.protobuf.aiq.config_pb2 import \
    AnalyticsConfig  # pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.accuracy_pb2 import AccuracyType
from truera.protobuf.public.data_service.data_service_messages_pb2 import \
    MaterializeStatus  # pylint: disable=no-name-in-module
from truera.protobuf.public.metadata_message_types_pb2 import \
    FEATURE_TRANSFORM_TYPE_PRE_POST_DATA  # pylint: disable=no-name-in-module
from truera.protobuf.public.metadata_message_types_pb2 import \
    FeatureTransformationType  # pylint: disable=no-name-in-module
from truera.protobuf.public.qoi_pb2 import \
    ExplanationAlgorithmType  # pylint: disable=no-name-in-module
from truera.protobuf.public.util import split_mode_pb2 as sm_pb
from truera.protobuf.useranalytics import \
    analytics_event_schema_pb2 as analytics_event_schema_pb
from truera.public.feature_influence_constants import \
    get_output_type_from_score_type
import truera.public.feature_influence_constants as fi_constants
from truera.utils.package_requirement_utils import get_python_version_str
from truera.utils.pyspark_util import is_supported_pyspark_tree_model
from truera.utils.truera_status import TruEraInternalError

PREDICTION_COLUMN_NAME = "Result"
NAN_REP = "NaN"  # how to materialize np.nan in the csv

DEFAULT_INFLUENCE_ALGORITHM_TABULAR = "shap"
DEFAULT_INFLUENCE_ALGORITHM_NON_TABULAR = "integrated-gradients"


class RemoteTrueraWorkspace(BaseTrueraWorkspace):

    def __init__(
        self,
        connection_string: str,
        authentication: TrueraAuthentication,
        log_level: int = logging.INFO,
        workspace_name: str = "",
        **kwargs
    ) -> None:
        """Construct a new remote TrueraWorkspace.
        Args:
            connection_string: URL of the Truera deployment.
            authentication: Credentials to connect to Truera deployment.
            log_level: Log level (defaults to `logging.INFO`).
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        connection_string = format_connection_string(connection_string)
        self.logger.info(f"Connecting to '{connection_string}'")
        ignore_version_mismatch = kwargs.get("ignore_version_mismatch", False)
        verify_cert = kwargs.get("verify_cert", True)
        authentication.set_token_endpoint(connection_string)
        self.ar_client = get_ar_client(
            connection_string=connection_string,
            auth_details=authentication.get_auth_details(),
            logger=self.logger,
            use_http=True,
            ignore_version_mismatch=ignore_version_mismatch,
            verify_cert=verify_cert,
        )
        self.data_service_client = DataServiceClient.create(
            connection_string=connection_string,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.user_manager_client = UserManagerServiceClient.create(
            connection_string=connection_string,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.rbac_service_client = RbacServiceClient.create(
            connection_string=connection_string,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.scheduled_ingestion_client = ScheduledIngestionClient.create(
            connection_string=connection_string,
            data_service_client=self.data_service_client,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.streaming_ingress_client = StreamingIngressClient.create(
            connection_string=connection_string,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.artifact_interaction_client = ArtifactInteractionClient(
            self.ar_client, self.data_service_client, self.logger
        )
        self.aiq_client = AiqClient(
            connection_string=connection_string,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert,
            artifact_interaction_client=self.artifact_interaction_client
        )
        self.qs_client = QueryServiceClient(
            connection_string=connection_string,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.mrc_client = MrcClient(
            connection_string=connection_string.rstrip("/") + "/api/mrc",
            auth_details=authentication.get_auth_details(),
            logger=self.logger,
            verify_cert=verify_cert
        )
        self.cs_client = ConfigurationServiceClient(
            connection_string=connection_string,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.feature_client = FeatureClient(self.ar_client, self.logger)
        self.monitoring_control_plane_client = MonitoringControlPlaneClient.create(
            connection_string=connection_string,
            logger=self.logger,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert
        )
        self.data_profiler = RemoteDataProfiler(
            self, self.artifact_interaction_client, self.cs_client,
            connection_string, authentication.get_auth_details(), verify_cert
        )
        self.tester = RemoteTester(
            self, self.artifact_interaction_client, connection_string,
            authentication.get_auth_details(), verify_cert
        )
        self.useranalytics_client = UserAnalyticsServiceClient.create(
            connection_string=connection_string,
            auth_details=authentication.get_auth_details(),
            use_http=True,
            verify_cert=verify_cert,
            analytics_client_mode=AnalyticsClientMode.SDK
        )
        self.project: Optional[Project] = None
        self.model: Optional[Model] = None
        self.data_collection: Optional[DataCollectionContainer] = None
        self.data_split_name: str = None
        self.connection_string = connection_string
        self.authentication = authentication
        self.workspace_id = ""
        if workspace_name:
            workspace_info = self.user_manager_client.get_workspace_info_with_proto(
                name=workspace_name
            )
            self.workspace_id = workspace_info.workspace_id if workspace_info else ""

    def get_projects(self) -> Sequence[str]:
        return self.artifact_interaction_client.get_all_projects(
            self.workspace_id
        )

    def _get_project_settings(self,
                              project: str) -> Mapping[str, Union[str, int]]:
        project_metadata = self._fetch_and_parse_project_metadata(project)
        project_num_default_influences = self.cs_client.get_num_default_influences(
            project_metadata['id']
        )
        return {
            "input_type": project_metadata['input_type'],
            "num_default_influences": project_num_default_influences,
            "score_type": project_metadata['score_type']
        }

    def add_project(
        self,
        project: str,
        score_type: str,
        input_type: Optional[str] = "tabular",
        num_default_influences: Optional[int] = None,
        ranking_k: Optional[int] = None,
        project_type: Optional[str] = "model_project"
    ):
        is_success = False
        project_id = None
        try:
            self._validate_add_project(
                project, score_type, input_type, num_default_influences
            )
            if self._get_current_active_project_name():
                self.set_data_collection(None)
                self.set_model(None)
            self.project = self.artifact_interaction_client.create_project(
                project,
                score_type,
                input_data_format=input_type,
                project_type=project_type,
                workspace_id=self.workspace_id
            )

            if workspace_validation_utils.is_nontabular_project(input_type):
                self.set_influence_type(DEFAULT_INFLUENCE_ALGORITHM_NON_TABULAR)
            elif importlib.util.find_spec("truera_qii"):
                self.set_influence_type("truera-qii")
            else:
                self.set_influence_type(DEFAULT_INFLUENCE_ALGORITHM_TABULAR)

            if num_default_influences:
                self.set_num_default_influences(num_default_influences)
            if score_type in ["ranking_score", "rank"]:
                if ranking_k is None:
                    ranking_k = fi_constants.DEFAULT_RANKING_K
                self.set_ranking_k(ranking_k)
            project_id = self.project.id
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_project_event_properties=analytics_event_schema_pb.
                    AddProjectEventProperties(
                        workspace="remote",
                        project_name=project,
                        command="add_project"
                    )
                ),
                project_id=project_id,
                is_success=is_success
            )

    def set_project(self, project: str):
        if project == self._get_current_active_project_name():
            return
        if project:
            self._validate_set_project(project)
        if self._get_current_active_project_name():
            self.set_data_collection(None)
            self.set_model(None)
        project_metadata = self._fetch_and_parse_project_metadata(project)
        self.project = Project(
            project_name=project,
            artifact_interaction_client=self.artifact_interaction_client,
            project_id=project_metadata["id"]
        )

    def set_score_type(self, score_type: str):
        self._ensure_project()
        self._validate_score_type(score_type)
        self.cs_client.update_metric_configuration(
            self.project.id, score_type=score_type
        )

    def set_influence_type(self, algorithm: str):
        algorithm_to_enum = {
            "truera-qii":
                AnalyticsConfig.AlgorithmType.TRUERA_QII,
            "shap":
                AnalyticsConfig.AlgorithmType.SHAP,
            "integrated-gradients":
                AnalyticsConfig.AlgorithmType.INTEGRATED_GRADIENTS,
            "nlp-shap":
                AnalyticsConfig.AlgorithmType.NLP_SHAP
        }
        if algorithm not in algorithm_to_enum:
            raise ValueError(
                f"'{algorithm}' is not a valid influence algorithm. Influence algorithm must be one of: {algorithm_to_enum.keys()}."
            )
        if self.project:
            return self.cs_client.update_analytics_configuration(
                project_id=self.project.id,
                influence_algorithm_type=algorithm_to_enum.get(algorithm)
            )

    def get_influence_type(self) -> str:
        return self.cs_client.get_influence_algorithm_type(self.project.id)

    def set_maximum_model_runner_failure_rate(
        self, maximum_model_runner_failure_rate: float
    ):
        self._ensure_project()
        if maximum_model_runner_failure_rate < 0 or maximum_model_runner_failure_rate >= 1:
            raise ValueError(
                "`maximum_model_runner_failure_rate` must be in [0, 1)!"
            )
        self.cs_client.update_metric_configuration(
            self.project.id,
            maximum_model_runner_failure_rate=maximum_model_runner_failure_rate
        )

    def get_maximum_model_runner_failure_rate(self) -> float:
        self._ensure_project()
        return self.cs_client.get_metric_configuration(
            self.project.id
        ).metric_configuration.maximum_model_runner_failure_rate

    def set_ranking_k(self, ranking_k: int):
        self._ensure_project()
        self.cs_client.update_analytics_configuration(
            self.project.id, ranking_k=ranking_k
        )

    def get_ranking_k(self) -> int:
        self._ensure_project()
        return self.cs_client.get_ranking_k(self.project.id)

    def get_num_default_influences(self) -> int:
        self._ensure_project()
        return self.cs_client.get_num_default_influences(self.project.id)

    def set_num_default_influences(self, num_default_influences: int) -> None:
        self._validate_num_default_influences(num_default_influences)
        self.cs_client.update_analytics_configuration(
            self.project.id, num_default_influences=num_default_influences
        )

    def list_performance_metrics(self) -> Sequence[str]:
        # TODO(DC-74): This isn't correct!
        return self.aiq_client.list_performance_metrics()

    def get_default_performance_metrics(self) -> Sequence[str]:
        return [
            AccuracyType.Type.Name(curr) for curr in
            self.cs_client.get_default_performance_metrics(self.project.id)
        ]

    def set_default_performance_metrics(
        self, performance_metrics: Sequence[str]
    ):
        valid_performance_metrics = self.list_performance_metrics()
        performance_metrics_enumified = workspace_validation_utils.validate_performance_metrics(
            performance_metrics, valid_performance_metrics
        )
        self.cs_client.update_metric_configuration(
            self.project.id, performance_metrics=performance_metrics_enumified
        )

    def get_num_internal_qii_samples(self) -> int:
        self._ensure_project()
        return self.cs_client.get_num_internal_qii_samples(self.project.id)

    def set_num_internal_qii_samples(self, num_samples: int) -> None:
        self._validate_num_samples_for_influences(num_samples)
        self.cs_client.update_analytics_configuration(
            self.project.id, num_internal_qii_samples=num_samples
        )

    def get_models(self, project_name: str = None) -> Sequence[str]:
        if not project_name:
            self._ensure_project()
            return self.artifact_interaction_client.get_all_models_in_project(
                self.project.id
            )
        project_metadata = self._fetch_and_parse_project_metadata(project_name)
        if project_metadata:
            return self.artifact_interaction_client.get_all_models_in_project(
                project_metadata['id']
            )
        return []

    def set_model(self, model_name: str):
        if model_name == self._get_current_active_model_name():
            return
        if not model_name:
            self.model = None
            return
        self._ensure_project()
        if model_name not in self.get_models():
            raise ValueError(
                f"Could not find model {model_name} in project {self.project.name}"
            )
        model_meta = self.artifact_interaction_client.get_model_metadata(
            self.project.name, model_name
        )
        data_collection_id = model_meta["data_collection_id"]
        data_collection_name = None
        if data_collection_id:
            data_collection_name = self.artifact_interaction_client.get_data_collection_name(
                self.project.id, data_collection_id
            )
        current_data_collection_in_context = self.get_context(
        ).get("data-collection")
        if current_data_collection_in_context != data_collection_name:
            self.logger.warn(
                f"Model \"{model_name}\" is associated with a different data_collection "
                f"(\"{data_collection_name}\") than the one in context (\"{current_data_collection_in_context}\")."
            )
            self.set_data_collection(data_collection_name)
        self.logger.info(f"Setting model context to \"{model_name}\".")
        self.model = self.project.get_model(model_name, data_collection_name)

    def delete_model(
        self, model_name: Optional[str] = None, *, recursive: bool = False
    ):
        project_name = self._ensure_project()
        if not model_name:
            self._ensure_model()
        model_name = model_name if model_name else self.model.model_name
        with WorkspaceContextCleaner(self, delete_model=True):
            success, remaining_items = self.artifact_interaction_client.delete_model(
                project_name, model_name, recursive=recursive
            )
            if not success:
                if remaining_items:
                    raise ValueError(
                        "Deletion of model failed as there are model tests that are using the model as a reference. "
                        "Please delete these model tests or pass recursive=True. Affected test ids: {}"
                        .format(remaining_items)
                    )
                raise TruEraInternalError(
                    "Delete failed. Expected model deletion to succeed as there are no affected model tests."
                )

    def get_data_collections(self, project_name: str = None) -> Sequence[str]:
        if not project_name:
            self._ensure_project()
            return self.artifact_interaction_client.get_all_data_collections_in_project(
                self.project.id
            )
        project_metadata = self.artifact_interaction_client.get_project_metadata(
            project_name
        )
        return self.artifact_interaction_client.get_all_data_collections_in_project(
            project_metadata['id']
        )

    def _get_data_collections_with_metadata(self) -> Sequence[DataCollection]:
        self._ensure_project()
        return self.artifact_interaction_client.get_all_data_collections_with_transform_type_in_project(
            self.project.id
        )

    def get_data_splits(self) -> Sequence[str]:
        self._ensure_project()
        self._ensure_data_collection()
        return self.artifact_interaction_client.get_all_datasplits_in_data_collection(
            self._get_current_active_project_name(),
            self._get_current_active_data_collection_name(),
            exclude_prod=True
        )

    def get_data_sources(self, project_name: str = None) -> Sequence[str]:

        def rowset_has_name(rowset_metadata):
            return "rowset" in rowset_metadata and "root_data" in rowset_metadata[
                "rowset"] and len(
                    rowset_metadata["rowset"]["root_data"]
                ) > 0 and "name" in rowset_metadata["rowset"]["root_data"][0]

        if not project_name:
            self._ensure_project()
            return [
                rowset_metadata["rowset"]["root_data"][0]["name"]
                for rowset_metadata in self.artifact_interaction_client.
                get_all_data_sources_in_project(self.project.id)
                if rowset_has_name(rowset_metadata)
            ]
        project_metadata = self.artifact_interaction_client.get_project_metadata(
            project_name
        )
        return [
            rowset_metadata["rowset"]["root_data"][0]["name"]
            for rowset_metadata in self.artifact_interaction_client.
            get_all_data_sources_in_project(project_metadata["id"])
            if rowset_has_name(rowset_metadata)
        ]

    def delete_data_source(self, name: str):
        self._ensure_project()
        return self.artifact_interaction_client.delete_data_source(
            self.project.id, name
        )

    def add_data_collection(
        self,
        data_collection_name: str,
        pre_to_post_feature_map: Optional[Mapping[str, Sequence[str]]] = None,
        provide_transform_with_model: Optional[bool] = None,
        schema: Optional[Schema] = None
    ):
        is_success = False
        data_collection_id = None
        try:
            workspace_validation_utils.ensure_valid_identifier(
                data_collection_name
            )
            self._ensure_project()
            if pre_to_post_feature_map:
                FeatureClient.verify_feature_map_from_dict(
                    pre_to_post_feature_map, self.logger
                )
            project_name = self._get_current_active_project_name()
            self.set_data_split(None)
            self.set_model(None)

            preprocessed_cols = None
            postprocessed_cols = None
            if pre_to_post_feature_map:
                preprocessed_cols = list(pre_to_post_feature_map.keys())
                postprocessed_cols = list(
                    itertools.chain.from_iterable(
                        pre_to_post_feature_map.values()
                    )
                )
            if schema is None:
                self.logger.warning("Creating data collection without schema.")
                schema_pb = None
            else:
                self._validate_schema_matches_score_type(schema)
                schema_pb = schema_to_proto(schema)
            try:
                data_collection = self.project.create_data_collection(
                    data_collection_name,
                    workspace_validation_utils.
                    get_feature_transform_type_from_feature_map(
                        pre_to_post_feature_map, provide_transform_with_model
                    ),
                    schema=schema_pb
                )
                data_collection_id = data_collection.upload(
                    self.artifact_interaction_client, project_name
                )
            except AlreadyExistsError:
                raise AlreadyExistsError(
                    f"Data collection \"{data_collection_name}\" already exists!"
                )
            prod_split_id = self.data_service_client.create_empty_split(
                project_id=self.project.id,
                data_collection_id=data_collection_id,
                split_name="prod"
            )
            dc_md = self.ar_client.get_data_collection_metadata(
                project_id=self.project.id,
                data_collection_id=data_collection_id,
            )
            dc_md.prod_split_id = prod_split_id
            self.ar_client.update_data_collection(
                data_collection_metadata=dc_md
            )
            if schema is not None:
                self.data_service_client.register_schema(
                    project_id=self.project.id,
                    data_collection_id=data_collection_id,
                    schemas=schema_to_schemas_to_register(schema),
                    start_streaming=False
                )
            self.feature_client.upload_feature_description_and_group_metadata(
                project_name,
                data_collection_name,
                pre_features=preprocessed_cols,
                post_features=postprocessed_cols,
                pre_to_post_feature_map=pre_to_post_feature_map,
                only_update_metadata=False
            )
            self.data_collection = DataCollectionContainer(
                data_collection_name, data_collection_id
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_data_collection_event_properties=
                    analytics_event_schema_pb.AddDataCollectionEventProperties(
                        workspace="remote",
                        project_name="" if self.project is
                        None else self.project.name,
                        command="add_data_collection",
                        data_collection_name=data_collection_name
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=data_collection_id,
                is_success=is_success
            )

    def _validate_set_data_collection(self, data_collection_name: str) -> str:
        # Returns ID of data collection
        workspace_validation_utils.ensure_valid_identifier(data_collection_name)
        self._ensure_project()
        data_collection_name_to_ids = {
            pair["name"]: pair["id"]
            for pair in self.artifact_interaction_client.
            get_all_data_collections_with_ids_in_project(self.project.id
                                                        )["name_id_pairs"]
        }
        if data_collection_name not in data_collection_name_to_ids:
            raise ValueError(
                f"No such data collection \"{data_collection_name}\"! See `add_data_collection` to add it."
            )
        return data_collection_name_to_ids[data_collection_name]

    def set_data_collection(self, data_collection_name: str):
        current_data_collection_name = self._get_current_active_data_collection_name(
        )
        if data_collection_name == current_data_collection_name:
            return
        self.set_data_split(None)
        self.set_model(None)
        if not data_collection_name:
            self.data_collection = None
            return
        data_collection_id = self._validate_set_data_collection(
            data_collection_name
        )
        self.data_collection = DataCollectionContainer(
            name=data_collection_name, id=data_collection_id
        )
        self.logger.info(
            f"Data collection in workspace context set to \"{data_collection_name}\"."
        )

    def set_data_split(self, data_split_name: str):
        if not data_split_name:
            self.data_split_name = None
            return
        self._ensure_project()
        self._ensure_data_collection()
        if data_split_name not in self.get_data_splits():
            raise ValueError(f"No such data split \"{data_split_name}\"!")
        self.data_split_name = data_split_name

    def add_nn_model(
        self,
        model_name: str,
        model_load_wrapper: base.Wrappers.ModelLoadWrapper,
        model_run_wrapper: base.Wrappers.ModelRunWrapper,
        attribution_config: AttributionConfiguration,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        virtual_models: bool = False,
        **kwargs
    ) -> Model:
        self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        validate_model_metadata(
            train_split_name=train_split_name,
            existing_split_names=self.get_data_splits(),
            train_parameters=train_parameters,
            logger=self.logger
        )

        wrapper_tmp_dir = tempfile.TemporaryDirectory()
        wrapper_tmp_path = wrapper_tmp_dir.name
        model_dir = None
        is_success = False
        model_id = None
        try:
            if not virtual_models:
                if not isinstance(
                    model_load_wrapper, base.Wrappers.ModelLoadWrapper
                ):
                    raise ValueError(
                        f"Uploading an NN model to remote server is only supported for `ModelLoadWrapper`s. Provided `model_load_wrapper` is of type {type(model_load_wrapper)}. If this model is not intended to be loaded, try uploading with `virtual_models=True`"
                    )
                model_dir = model_load_wrapper.get_model_path()
                try:
                    self._save_object_file(
                        wrapper_tmp_path, MODEL_LOAD_WRAPPER_SAVE_NAME,
                        model_load_wrapper
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    raise ValueError(
                        f'Failed to upload model object. Make sure the model can be loaded from file, or try uploading with `virtual_models=True`'
                    )

            self._save_object_file(
                wrapper_tmp_path, MODEL_RUN_WRAPPER_SAVE_NAME, model_run_wrapper
            )

            model_dir = model_dir or wrapper_tmp_path

            if virtual_models:
                model_type = ModelType.Virtual
            else:
                model_type = ModelType.PyFunc
            #TODO: If MLFlow is the right implementation, enable an equivalent of  model_preprocessing.prepare_python_model_folder for nn
            # This would use backend and pip dependencies paraneters passed into this function
            # Tracked in AB#3556
            model = self.project.create_model(
                model_name=model_name,
                model_type=model_type,
                model_output_type=self._get_output_type(),
                local_model_path=model_dir,
                data_collection_name=data_collection_name,
                extra_data_path=wrapper_tmp_path,
                train_split_name=train_split_name,
                train_parameters=train_parameters
            )
            model_id = model.upload(self.artifact_interaction_client)
            self.model = model
            self.update_nn_user_config(attribution_config)
            self.logger.info(
                f"Model \"{model_name}\" added and associated with data collection \"{data_collection_name}\". \"{model_name}\" is set as the model in context."
            )
            print(
                f"Model uploaded to: {self.connection_string}/home/p/{quote(self.project.name)}/m/{quote(model.model_name)}/"
            )
            is_success = True
        finally:
            try:
                wrapper_tmp_dir.cleanup()
            except:
                pass
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_model_event_properties=analytics_event_schema_pb.
                    AddModelEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_nn_model",
                        data_collection_name=data_collection_name,
                        model_name=model_name
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=model_id,
                is_success=is_success
            )

    def add_model(
        self,
        model_name: str,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None
    ):
        model_id = None
        is_success = False
        try:
            self._ensure_project()
            self._ensure_data_collection()
            validate_model_metadata(
                train_split_name=train_split_name,
                existing_split_names=self.get_data_splits(),
                train_parameters=train_parameters,
                logger=self.logger
            )
            model = self.project.create_model(
                model_name=model_name,
                model_type=ModelType.Virtual,
                model_output_type=self._get_output_type(),
                local_model_path="",
                data_collection_name=self.
                _get_current_active_data_collection_name(),
                train_split_name=train_split_name,
                train_parameters=train_parameters
            )
            model.upload(self.artifact_interaction_client)
            self.set_model(model_name)
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_model_event_properties=analytics_event_schema_pb.
                    AddModelEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_model",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        model_name=model_name
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=model_id,
                is_success=is_success
            )

    def _trigger_computations_post_ingestion(
        self,
        model_name: str,
        compute_predictions: bool = False,
        compute_feature_influences: bool = False,
        compute_for_all_splits: bool = False
    ):
        if not (compute_predictions or compute_feature_influences):
            return
        with WorkspaceContextCleaner(self):
            self.set_model(model_name)
            all_data_splits = self.get_data_splits()
            if not all_data_splits:
                return  # nothing to trigger

            try:
                if compute_for_all_splits:
                    splits_to_trigger = all_data_splits
                else:
                    # Set background data split, and switch workspace context to use this split
                    self.get_explainer(
                    )._ensure_influences_background_data_split_is_set()
                    splits_to_trigger = [
                        self.get_influences_background_data_split()
                    ]

                for split_name in splits_to_trigger:
                    # Trigger
                    explainer = self.get_explainer(base_data_split=split_name)
                    if compute_predictions:
                        self.logger.info(
                            f"Triggering computations for model predictions on split {split_name}."
                        )
                        explainer.get_ys_pred(
                            include_all_points=True, wait=False
                        )
                    if compute_feature_influences:
                        self.logger.info(
                            f"Triggering computations for model feature influences on split {split_name}."
                        )
                        explainer.compute_feature_influences(wait=False)
            except Exception as e:
                self.logger.warning(
                    f"Failed to autotrigger computations. See error: {str(e)}"
                )

    def _validate_add_model_remote(
        self,
        model_name: str,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
    ):
        self._validate_add_model(model_name)
        validate_model_metadata(
            train_split_name=train_split_name,
            existing_split_names=self.get_data_splits(),
            train_parameters=train_parameters,
            logger=self.logger
        )

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
        is_success = False
        try:
            self._validate_add_model_remote(
                model_name,
                train_split_name=train_split_name,
                train_parameters=train_parameters
            )
            self._add_packaged_python_model(
                model_name,
                model_dir,
                data_collection_name=data_collection_name,
                train_split_name=train_split_name,
                train_parameters=train_parameters,
                verify_model=verify_model,
                compute_predictions=compute_predictions,
                compute_feature_influences=compute_feature_influences,
                compute_for_all_splits=compute_for_all_splits
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_model_event_properties=analytics_event_schema_pb.
                    AddModelEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_python_packaged_model",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        model_name=model_name
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if not is_success else self.model.model_id,
                is_success=is_success
            )

    def _add_packaged_python_model(
        self,
        model_name: str,
        model_dir: str,
        *,
        data_collection_name: Optional[str] = None,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        verify_model: bool = True,
        compute_predictions: bool = False,
        compute_feature_influences: bool = False,
        compute_for_all_splits: bool = False
    ):
        if data_collection_name:
            if data_collection_name not in self.get_data_collections():
                raise ValueError(
                    f"The data_collection: {data_collection_name} does not exist in the current project {self.project.name}"
                )
        else:
            data_collection_name = self._get_current_active_data_collection_name(
            )
        if verify_model:
            self.verify_packaged_model(
                model_dir
            )  # full validation using split data
        else:
            verify_python_model_folder(
                model_dir, logger=self.logger
            )  # basic checking on folder structure
        model = self.project.create_model(
            model_name=model_name,
            model_type=ModelType.PyFunc,
            model_output_type=self._get_output_type(),
            local_model_path=model_dir,
            data_collection_name=data_collection_name,
            train_split_name=train_split_name,
            train_parameters=train_parameters
        )
        model.upload(self.artifact_interaction_client)
        self.model = model
        self.logger.info(
            f"Model \"{model_name}\" added and associated with data collection \"{data_collection_name}\". \"{model_name}\" is set as the model in context."
        )
        self.logger.info(
            f"Model uploaded to: {self.connection_string}/home/p/{quote(self.project.name)}/m/{quote(model.model_name)}/"
        )
        if self.mrc_client.ping():
            self._trigger_computations_post_ingestion(
                model_name,
                compute_predictions=compute_predictions,
                compute_feature_influences=compute_feature_influences,
                compute_for_all_splits=compute_for_all_splits
            )

    def create_packaged_python_model(
        self,
        output_dir: str,
        model_obj: Optional[Any] = None,
        additional_pip_dependencies: Optional[Sequence[str]] = None,
        additional_modules: Optional[Sequence[Any]] = None,
        model_path: Optional[str] = None,
        model_code_files: Optional[Sequence[str]] = None,
        **kwargs
    ):
        if model_code_files is None:
            model_code_files = []
        if model_obj is not None:
            self.logger.debug("Packaging Python model from model object.")
            feature_transform_type = self._get_feature_transform_type_for_data_collection(
            )
            self.prepare_python_model_folder_from_model_object(
                output_dir,
                model_obj,
                None,
                feature_transform_type=feature_transform_type,
                additional_pip_dependencies=additional_pip_dependencies,
                additional_modules=additional_modules,
                **kwargs
            )
        else:
            prepare_template_model_folder(
                output_dir,
                self._get_output_type(),
                model_path,
                model_code_files,
                pip_dependencies=additional_pip_dependencies,
                python_version=kwargs.get(
                    "python_version", get_python_version_str()
                )
            )
        self.logger.info(
            f"Successfully generated template model package at path '{output_dir}'"
        )

    def verify_packaged_model(self, model_path: str):
        self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        dc_metadata = self.project.get_data_collection_metadata(
            data_collection_name, as_json=False
        )
        available_data_splits = self.get_data_splits()
        test_data = None if not available_data_splits else self._get_xs_for_split(
            available_data_splits[0], 0, 10, get_post_processed_data=True
        )
        validate_packaged_python_model(
            self.logger,
            model_path,
            test_data=test_data,
            model_output_type=self._get_output_type(),
            feature_transform_type=dc_metadata.feature_transform_type
        )

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
        self._validate_additional_modules(additional_modules)
        self._validate_add_model_remote(
            model_name,
            train_split_name=train_split_name,
            train_parameters=train_parameters
        )
        feature_transform_type = self._get_feature_transform_type_for_data_collection(
        )
        score_type = self._get_score_type()
        classification_threshold = workspace_validation_utils.validate_model_threshold(
            classification_threshold, score_type
        )
        temp_staging_dir = tempfile.mkdtemp()
        shutil.rmtree(temp_staging_dir, ignore_errors=True)
        is_success = False
        try:
            self.prepare_python_model_folder_from_model_object(
                temp_staging_dir,
                model,
                transformer,
                feature_transform_type=feature_transform_type,
                additional_pip_dependencies=additional_pip_dependencies,
                additional_modules=additional_modules,
                **kwargs
            )
            self._add_packaged_python_model(
                model_name,
                temp_staging_dir,
                train_split_name=train_split_name,
                train_parameters=train_parameters,
                verify_model=verify_model,
                compute_predictions=compute_predictions,
                compute_feature_influences=compute_feature_influences,
                compute_for_all_splits=compute_for_all_splits
            )
            if score_type in fi_constants.VALID_SCORE_TYPES_FOR_CLASSIFICATION:
                self.update_model_threshold(classification_threshold)
            is_success = True
        finally:
            shutil.rmtree(temp_staging_dir, ignore_errors=True)
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_model_event_properties=analytics_event_schema_pb.
                    AddModelEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_python_model",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        model_name=model_name
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if not is_success else self.model.model_id,
                is_success=is_success
            )

    def delete_data_split(
        self,
        data_split_name: Optional[str] = None,
        *,
        recursive: bool = False
    ):
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        if not data_split_name:
            data_split_name = self._ensure_base_data_split()
        with WorkspaceContextCleaner(self, delete_data_split=True):
            success, remaining_items = self.artifact_interaction_client.delete_data_split(
                project_name,
                data_collection_name,
                data_split_name,
                recursive=recursive
            )
            if not success:
                if remaining_items:
                    raise ValueError(
                        "Deletion of data split failed as there are model tests or child splits that are using the data split. "
                        "Please delete these entities or pass recursive=True. Affected entity ids: {}"
                        .format(remaining_items)
                    )
                raise TruEraInternalError(
                    "Delete failed. Expected split deletion to succeed as there are no affected model tests or child splits associated with this split."
                )

    def delete_data_collection(
        self,
        data_collection_name: Optional[str] = None,
        *,
        recursive: bool = True
    ):
        project_name = self._ensure_project()
        if not data_collection_name:
            data_collection_name = self._ensure_data_collection()
        with WorkspaceContextCleaner(self, delete_data_collection=True):
            success, remaining_items = self.artifact_interaction_client.delete_data_collection(
                project_name, data_collection_name, recursive=recursive
            )
            if not success:
                if remaining_items:
                    raise ValueError(
                        "Deletion of data collection failed as there are entities contained in the data collection. "
                        "Please delete these entites or pass recursive=True. Remaining entities:\n {}"
                        .format(format_remaining_list(remaining_items))
                    )
                raise TruEraInternalError(
                    "Delete failed. Expected data collection deletion to succeed as no remaining items returned."
                )

    def _use_data_layer_for_split_ingestion(
        self, pre_data: Union[str, pd.DataFrame], id_col_name: str
    ) -> bool:
        if not id_col_name:
            return False
        if not self.get_client_setting_value(
            "workspace_use_tables_for_split_ingestion"
        ):
            if id_col_name:
                raise ValueError(
                    "To ingest splits with an ID column, you must activate split ingestion from tables by default. Run `tru.activate_client_setting('workspace_use_tables_for_split_ingestion')`"
                )
            return False

        # We don't want to use this if already given a table.
        if isinstance(pre_data, Table):
            return False

        # We don't want to use this if data is remote anyway.
        if isinstance(pre_data, str):
            parsed = urlparse(pre_data)
            scheme = parsed.scheme.lower()
            if scheme and scheme != "file":
                return False

        return True

    def _infer_background_split(self, background_split_name):
        background_split_id = None
        if not background_split_name:
            background_split_id = self.cs_client.get_base_split(
                self.project.id,
                self.data_collection.id,
                infer_base_split_if_not_set=True
            )
            background_split_name = self.artifact_interaction_client.get_split_metadata_by_id(
                self.project.id, background_split_id
            )["name"]
        else:
            background_split_id = self.artifact_interaction_client.get_split_metadata(
                self.project.name, self.data_collection.name,
                background_split_name
            )["id"]
        if not background_split_name or not background_split_id:
            raise ValueError(
                "Background split cannot be inferred. Please make sure Background split is present in "
                "data collection."
            )
        return background_split_name, background_split_id

    def _validate_train_baseline(self, train_baseline_model: bool) -> None:
        if train_baseline_model and not self.mrc_client.ping():
            raise ValueError(
                "This remote deployment does not support training of baseline model. You can set workspace to `local` to train the baseline model and upload the model to the `remote` workspace."
            )

    def add_data_split(
        self,
        data_split_name: str,
        pre_data: pd.DataFrame,
        *,
        post_data: Optional[pd.DataFrame] = None,
        label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
        prediction_data: Optional[pd.DataFrame] = None,
        feature_influence_data: Optional[pd.DataFrame] = None,
        label_col_name: Optional[str] = None,
        id_col_name: Optional[str] = None,
        extra_data_df: Optional[pd.DataFrame] = None,
        split_type: Optional[str] = "all",
        timestamp_col_name: Optional[str] = None,
        split_mode: sm_pb.SplitMode = sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED,
        sample_count: int = 50000,
        background_split_name: Optional[str] = None,
        influence_type: Optional[str] = None,
        score_type: Optional[str] = None,
        train_baseline_model: Optional[bool] = False,
        **kwargs
    ):
        is_success = False
        use_legacy_ingestion = False
        try:
            if id_col_name and id_col_name in self._get_pre_to_post_feature_map(
            ):
                raise ValueError(
                    "`id_col_name` present in feature map. Remove it from `feature_map` before trying to upload split data."
                )
            self._validate_train_baseline(train_baseline_model)
            upload_via_data_layer = self._use_data_layer_for_split_ingestion(
                pre_data, id_col_name
            )

            background_split_id = None
            if feature_influence_data is not None:
                background_split_name, background_split_id = self._infer_background_split(
                    background_split_name
                )
                influence_type = EXPLANATION_ALGORITHM_TYPE_TO_STR[
                    workspace_validation_utils.
                    validate_influence_type_str_for_virtual_model_upload(
                        influence_type, self.get_influence_type()
                    )]
            if upload_via_data_layer and len(pre_data) > sample_count:
                self.logger.warning(
                    f"Number of rows in the data split ({len(pre_data)}) is larger than {sample_count}. Will downsample the rows to {sample_count}. Pass `sample_count=x` to override the default max number of samples."
                )

            self._validate_add_data_split(
                data_split_name,
                pre_data=pre_data,
                post_data=post_data,
                label_data=label_data,
                prediction_data=prediction_data,
                feature_influence_data=feature_influence_data,
                label_col_name=label_col_name,
                id_col_name=id_col_name,
                extra_data_df=extra_data_df,
                split_type=split_type,
                timestamp_col_name=timestamp_col_name,
                split_mode=split_mode,
                background_split_name=background_split_name,
                score_type=score_type,
                **kwargs
            )
            model_id = None
            if self._get_current_active_model_name():
                model_id = self.model.model_id
            # If we have an Id column and experimental feature is on, use data layer for all split
            # ingestion.

            # note how here we pass in "prediction_data" (as a separate dataframe)
            if upload_via_data_layer:
                self._add_data_split_from_local_data_via_data_layer(
                    data_split_name,
                    pre_data,
                    post_data=post_data,
                    label_data=label_data,
                    prediction_data=prediction_data,
                    feature_influence_data=feature_influence_data,
                    id_col_name=id_col_name,
                    label_col_name=label_col_name,
                    prediction_col_name=kwargs.get("prediction_col_name"),
                    extra_data_df=extra_data_df,
                    split_type=split_type,
                    timestamp_col_name=timestamp_col_name,
                    split_mode=split_mode,
                    materialize_approx_max_rows=sample_count,
                    background_split_id=background_split_id,
                    model_id=model_id,
                    score_type=score_type or self._get_score_type(),
                    influence_type=influence_type,
                    train_baseline_model=train_baseline_model
                )
            else:
                use_legacy_ingestion = True
                self.logger.info(
                    "Upload of `prediction_data` and `feature_influence_data` is not supported."
                )

                # except here we pass in "prediction_col_name" as a kwarg (NOT prediction data).
                # no idea why this is inconsistent / why we only support one flow.
                self.create_data_split_via_upload_files(
                    data_split_name,
                    pre_data=pre_data,
                    post_data=post_data,
                    label_data=label_data,
                    label_col_name=label_col_name,
                    extra_data_df=extra_data_df,
                    split_type=split_type,
                    split_mode=split_mode,
                    score_type=score_type,
                    train_baseline_model=train_baseline_model,
                    **kwargs
                )
            self._auto_create_model_tests(data_split_name)
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_data_split_event_properties=analytics_event_schema_pb.
                    AddDataSplitEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_split",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                        predictions_ingested=str(
                            (not use_legacy_ingestion) and
                            prediction_data is not None
                        ),
                        labels_ingested=str(label_data is not None),
                        extra_data_ingested=str(extra_data_df is not None),
                    )
                ),
                experimentation_flags={
                    "use_legacy_ingestion": str(use_legacy_ingestion)
                },
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                is_success=is_success
            )

    def add_data(
        self,
        data: Union[pd.DataFrame, 'Table'],
        *,
        data_split_name: str,
        column_spec: Union[BaseColumnSpec, Mapping[str, Union[str,
                                                              Sequence[str]]]],
        model_output_context: Optional[Union[ModelOutputContext,
                                             Mapping[str, str]]] = None,
        idempotency_id: Optional[str] = None,
        **kwargs
    ):
        is_success = False
        if "prediction_col_names" in column_spec and column_spec[
            "prediction_col_names"]:
            workspace_validation_utils.validate_ranking_ids(
                self._get_score_type(),
                column_spec["ranking_group_id_column_name"],
                column_spec["ranking_item_id_column_name"]
            )
        if not isinstance(column_spec, BaseColumnSpec):
            column_spec = column_spec_from_kwargs(**column_spec)
        if isinstance(model_output_context, Mapping):
            model_output_context = ModelOutputContext(**model_output_context)
        try:
            model_output_context = infer_model_output_context(
                self,
                column_spec=column_spec,
                model_output_context=model_output_context,
                is_production_data=False
            )
            add_data(
                self,
                data=data,
                split_name=data_split_name,
                column_spec=column_spec,
                model_output_context=model_output_context,
                is_production_data=False,
                sample_count=kwargs.get("sample_count", None),
                idempotency_id=idempotency_id,
                timeout_seconds=kwargs.get("timeout_seconds", None)
            )
            is_success = True
        finally:
            column_info = column_spec.to_column_info()
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_data_event_properties=analytics_event_schema_pb.
                    AddDataEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_data",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                        pre_data_ingested=str(
                            column_info.pre is not None and
                            len(column_info.pre) > 0
                        ),
                        post_data_ingested=str(
                            column_info.post is not None and
                            len(column_info.post) > 0
                        ),
                        predictions_ingested=str(
                            column_info.prediction is not None and
                            len(column_info.prediction) > 0
                        ),
                        feature_influences_ingested=str(
                            column_info.feature_influences is not None and
                            len(column_info.feature_influences) > 0
                        ),
                        labels_ingested=str(
                            column_info.label is not None and
                            len(column_info.label) > 0
                        ),
                        extra_data_ingested=str(
                            column_info.extra is not None and
                            len(column_info.extra) > 0
                        ),
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                is_success=is_success
            )
            if is_success:
                self._auto_create_model_tests(data_split_name)

    def add_production_data(
        self,
        data: Union[pd.DataFrame, 'Table'],
        *,
        column_spec: Union[BaseColumnSpec, Mapping[str, Union[str,
                                                              Sequence[str]]]],
        model_output_context: Optional[Union[ModelOutputContext,
                                             Mapping[str, str]]] = None,
        idempotency_id: Optional[str] = None,
        **kwargs
    ):
        is_success = False
        if not isinstance(column_spec, BaseColumnSpec):
            column_spec = column_spec_from_kwargs(**column_spec)
        if isinstance(model_output_context, Mapping):
            model_output_context = ModelOutputContext(**model_output_context)
        try:
            model_output_context = infer_model_output_context(
                self,
                column_spec=column_spec,
                model_output_context=model_output_context,
                is_production_data=True
            )
            add_data(
                self,
                data=data,
                split_name=PROD_DATA_SPLIT_NAME,
                column_spec=column_spec,
                model_output_context=model_output_context,
                is_production_data=True,
                sample_count=kwargs.get("sample_count", None),
                idempotency_id=idempotency_id
            )
            is_success = True
        finally:
            column_info = column_spec.to_column_info()
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_data_event_properties=analytics_event_schema_pb.
                    AddDataEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_production_data",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=PROD_DATA_SPLIT_NAME,
                        pre_data_ingested=str(
                            column_info.pre is not None and
                            len(column_info.pre) > 0
                        ),
                        post_data_ingested=str(
                            column_info.post is not None and
                            len(column_info.post) > 0
                        ),
                        predictions_ingested=str(
                            column_info.prediction is not None and
                            len(column_info.prediction) > 0
                        ),
                        feature_influences_ingested=str(
                            column_info.feature_influences is not None and
                            len(column_info.feature_influences) > 0
                        ),
                        labels_ingested=str(
                            column_info.label is not None and
                            len(column_info.label) > 0
                        ),
                        extra_data_ingested=str(
                            column_info.extra is not None and
                            len(column_info.extra) > 0
                        ),
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                is_success=is_success
            )

    def add_data_split_from_data_source(
        self,
        data_split_name: str,
        pre_data: Union[Table, str],
        *,
        post_data: Optional[Union[Table, str]] = None,
        label_col_name: Optional[str] = None,
        id_col_name: Optional[str] = None,
        extra_data: Optional[Union[Table, str]] = None,
        split_type: Optional[str] = "all",
        split_mode: sm_pb.SplitMode = sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED,
        train_baseline_model: Optional[bool] = False,
        **kwargs
    ):
        is_success = False
        try:
            self._validate_train_baseline(train_baseline_model)
            self._validate_add_data_split_from_data_source(
                data_split_name,
                pre_data=pre_data,
                post_data=post_data,
                label_col_name=label_col_name,
                id_col_name=id_col_name,
                extra_data=extra_data,
                split_type=split_type,
                split_mode=split_mode,
                **kwargs
            )
            # If the user has just given us a uri and we're going to add a data source then attach
            # and create a split, we don't want that rowset showing up in queries unprompted. This
            # will set the creation reason to SYSTEM and we will filter in get rowsets calls by
            # default - for example on the data page.
            if isinstance(pre_data, str):
                if not kwargs:
                    kwargs = {}
                kwargs["user_requested"] = False
            #TODO support post data + extra data here
            result = self._add_split_from_data_source(
                data_split_name,
                pre_data,
                label_col_name,
                id_col_name,
                split_type,
                kwargs.pop("timestamp_col_name", None),
                split_mode,
                train_baseline_model=train_baseline_model,
                **kwargs
            )
            if result["status"] == "OK":
                self._auto_create_model_tests(data_split_name)
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_data_split_event_properties=analytics_event_schema_pb.
                    AddDataSplitEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_data_split_from_data_source",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                        labels_ingested=str(label_col_name is not None),
                        extra_data_ingested=str(extra_data is not None),
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                is_success=is_success
            )

    def _auto_create_model_tests(self, data_split_name: str):
        # TODO(AB #6997): (move call to auto create tests to the backend)
        if self.get_client_setting_value(
            "create_model_tests_on_split_ingestion"
        ):
            split_metadata = self.artifact_interaction_client.get_split_metadata(
                self._get_current_active_project_name(),
                self._get_current_active_data_collection_name(), data_split_name
            )
            self.tester.model_test_client.create_tests_from_split(
                self.project.id, split_metadata["id"]
            )

    def _add_data_split_from_local_data_via_data_layer(
        self,
        data_split_name: str,
        pre_data: Union[pd.DataFrame, Table, str],
        *,
        post_data: Optional[pd.DataFrame] = None,
        label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
        prediction_data: Optional[pd.DataFrame] = None,
        feature_influence_data: Optional[pd.DataFrame] = None,
        id_col_name: Optional[str] = None,
        label_col_name: Optional[str] = None,
        prediction_col_name: Optional[str] = None,
        extra_data_df: Optional[pd.DataFrame] = None,
        split_type: Optional[str] = "all",
        timestamp_col_name: Optional[str] = None,
        split_mode: sm_pb.SplitMode = sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED,
        materialize_approx_max_rows: Optional[int] = 50000,
        background_split_id: Optional[str] = None,
        model_id: Optional[str] = None,
        score_type: Optional[str] = None,
        influence_type: Optional[str] = None,
        train_baseline_model: bool = False
    ):
        self._validate_train_baseline(train_baseline_model)
        label_df = self.get_df_from_args(
            column_names=[id_col_name, label_col_name]
            if label_col_name else None,
            source_df=pre_data,
            raw_data=label_data
        )
        prediction_df = self.get_df_from_args(
            column_names=[id_col_name, prediction_col_name]
            if prediction_col_name else None,
            source_df=pre_data,
            raw_data=prediction_data
        )
        pre_data_df = self.drop_other_columns(
            pre_data, other_columns=[label_col_name, prediction_col_name]
        )
        post_data_df = self.drop_other_columns(
            post_data, other_columns=[label_col_name, prediction_col_name]
        )
        try:
            data_split_params = PandasDataSplitPathContainer(
                pre_data_df,
                post_data_df,
                extra_data_df,
                label_df,
                prediction_df,
                feature_influence_data,
                logger=self.logger
            )
            self.artifact_interaction_client.create_data_split_via_data_service(
                self.project.id,
                self.data_collection.id,
                data_split_name,
                split_type,
                data_split_params,
                id_col_name,
                split_mode=split_mode,
                timestamp_col=timestamp_col_name,
                materialize_approx_max_rows=materialize_approx_max_rows,
                background_split_id=background_split_id,
                model_id=model_id,
                score_type=score_type,
                influence_type=influence_type,
                train_baseline_model=train_baseline_model
            )
        finally:
            data_split_params.clean_up_temp_files()
        self.data_split_name = data_split_name
        return

    def _get_rowset(
        self, rowset: Union[Table, str], data_split_name: str, **kwargs
    ):
        if isinstance(rowset, str):
            temp_data_source_name = data_split_name + str(uuid.uuid4())
            return self.get_ingestion_client().add_data_source(
                temp_data_source_name, rowset, **kwargs
            )
        else:
            return rowset

    def _add_check_status_lambda(self, result):
        result[
            "check_status_lambda"
        ] = lambda: self.artifact_interaction_client.get_materialize_operation_status(
            self.project.id, result["operation_id"]
        )
        return result

    def add_labels(
        self, label_data: Union[Table, pd.DataFrame],
        label_col_name: Union[str, Sequence[str]], id_col_name: str
    ):
        data_split_name = self._get_current_active_data_split_name()
        is_success = False
        try:
            self.add_data(
                data=label_data,
                data_split_name=data_split_name,
                column_spec=ColumnSpec(
                    id_col_name=id_col_name, label_col_names=label_col_name
                )
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    ingest_labels_event_properties=analytics_event_schema_pb.
                    IngestLabelsEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                is_success=is_success
            )

    def add_extra_data(
        self, extra_data: Union[Table, pd.DataFrame],
        extras_col_names: Union[str, Sequence[str]], id_col_name: str
    ):
        data_split_name = self._get_current_active_data_split_name()
        is_success = False
        try:
            self.add_data(
                data=extra_data,
                data_split_name=data_split_name,
                column_spec=ColumnSpec(
                    id_col_name=id_col_name,
                    extra_data_col_names=extras_col_names
                )
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    ingest_extra_data_event_properties=analytics_event_schema_pb
                    .IngestExtraDataEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                is_success=is_success
            )

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
        extra_data_df: Optional[pd.DataFrame] = None,
    ):
        if workspace_validation_utils.is_nlp_project(self._get_input_type()):
            self.logger.warning(
                "`add_nn_data_split` will soon be deprecated. Please migrate to `truera.client.ingestion.add_data` to ingest NLP split data."
            )
        self._validate_add_nn_data_split(
            data_split_name,
            pre_data=pre_data,
            label_data=label_data,
            id_col_name=id_col_name,
            extra_data_df=extra_data_df,
            split_type=split_type
        )
        is_success = False
        try:
            wrapper_tmp_dir = tempfile.TemporaryDirectory()
            wrapper_tmp_path = wrapper_tmp_dir.name
            self._save_object_file(
                wrapper_tmp_path, SPLIT_LOAD_WRAPPER_SAVE_NAME,
                truera_wrappers.split_load_wrapper
            )
            local_file_location = truera_wrappers.split_load_wrapper.get_data_path(
            )
            data_collection_name = self._get_current_active_data_collection_name(
            )
            dc_metadata = self.project.get_data_collection_metadata(
                data_collection_name, as_json=False
            )
            data_collection = self.project.create_data_collection(
                data_collection_name, dc_metadata.feature_transform_type
            )
            label_file_name = self._write_input_file(
                label_data, "label", header=False, extension="csv"
            )
            extra_data_file_name = self._write_input_file(
                extra_data_df, "extra", extension="csv"
            )
            if pre_data is not None and isinstance(pre_data, pd.DataFrame):
                pre_data_file_name = self._write_input_file(
                    pre_data, "pre", extension="csv"
                )
            else:
                # TODO: this only works if there are labels which we can assume for the time being.
                pre_data_file_name = self._write_input_file(
                    pd.DataFrame(data=list(range(len(label_data)))),
                    "pre",
                    extension="csv"
                )

            data_collection.create_data_split(
                data_split_name,
                _map_split_type(split_type),
                pre_transform_path=pre_data_file_name,
                labels_path=label_file_name,
                extra_data_path=extra_data_file_name,
                split_dir=local_file_location,
                data_split_loader_wrapper_path=wrapper_tmp_path,
                split_mode=sm_pb.SplitMode.SPLIT_MODE_NON_TABULAR,
                train_baseline_model=False
            )

            data_collection.upload_new_split(
                self.artifact_interaction_client, self.project.name
            )
            is_success = True
        finally:
            try:
                wrapper_tmp_dir.cleanup()
            except:
                pass
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_data_split_event_properties=analytics_event_schema_pb.
                    AddDataSplitEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_nn_data_split",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                        labels_ingested=str(label_data is not None),
                        extra_data_ingested=str(extra_data_df is not None),
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                is_success=is_success
            )

        self.data_split_name = data_split_name

    def create_data_split_via_upload_files(
        self,
        data_split_name: str,
        *,
        pre_data: pd.DataFrame,
        post_data: Optional[pd.DataFrame] = None,
        label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
        label_col_name: Optional[str] = None,
        extra_data_df: Optional[pd.DataFrame] = None,
        split_type: Optional[str] = "all",
        split_mode: sm_pb.SplitMode = sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED,
        score_type: Optional[str] = None,
        train_baseline_model: Optional[bool] = False,
        **kwargs
    ):
        label_df = self.get_df_from_args(
            column_names=[label_col_name] if label_col_name else None,
            source_df=pre_data,
            raw_data=label_data
        )

        prediction_col_name = kwargs.pop("prediction_col_name", None)
        prediction_df = self.get_df_from_args(
            column_names=[prediction_col_name] if prediction_col_name else None,
            source_df=pre_data,
            raw_data=None
        )

        pre_data_df = self.drop_other_columns(
            pre_data, other_columns=[label_col_name, prediction_col_name]
        )
        post_data_df = self.drop_other_columns(
            post_data, other_columns=[label_col_name, prediction_col_name]
        )

        try:
            if not kwargs:
                kwargs = {}
            label_file_name = self._write_input_file(
                label_df, "label", header=False, extension="csv"
            )
            extra_data_file_name = self._write_input_file(
                extra_data_df, "extra", extension="csv"
            )
            prediction_file_name = self._write_input_file(
                prediction_df, "prediction", extension="csv"
            )
            pre_data_file_name = self._write_input_file(
                pre_data_df, "pre", extension="csv"
            )
            post_data_file_name = self._write_input_file(
                post_data_df,
                "post",
                info_log=
                "Separate pre/post-transform data has been ingested. This should adhere to the feature mapping you specified while adding the data collection.",
                extension="csv"
            )
            prediction_cache = None

            if prediction_df is not None:
                import truera
                prediction_cache = self.project.create_prediction_cache(
                    self._get_current_active_model_name(),
                    self._get_current_active_data_collection_name(),
                    split_name=data_split_name,
                    cache_location=prediction_file_name,
                    score_type=score_type or self._get_score_type(),
                    model_output_type=self._get_output_type(),
                    client_name="notebook_client",
                    client_version=f"{truera.__version__}",
                    row_count=len(prediction_df)
                )
            data_collection_name = self._get_current_active_data_collection_name(
            )
            dc_metadata = self.project.get_data_collection_metadata(
                data_collection_name, as_json=False
            )
            data_collection = self.project.create_data_collection(
                data_collection_name, dc_metadata.feature_transform_type
            )

            if split_mode == sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED:
                pre_transform_path = pre_data_file_name
                if post_data is not None:
                    post_transform_path = post_data_file_name
                else:
                    post_transform_path = pre_data_file_name
            else:
                pre_transform_path = None
                post_transform_path = None

            data_collection.create_data_split(
                data_split_name,
                _map_split_type(split_type),
                pre_transform_path=pre_transform_path,
                post_transform_path=post_transform_path,
                labels_path=label_file_name,
                extra_data_path=extra_data_file_name,
                split_mode=split_mode,
                train_baseline_model=train_baseline_model
            )

            data_collection.upload_new_split(
                self.artifact_interaction_client, self.project.name
            )
            if prediction_cache:
                prediction_cache.upload(
                    self.artifact_interaction_client,
                    create_model=False,
                    overwrite=False
                )

        finally:
            best_effort_remove_temp_files(
                [
                    label_file_name, extra_data_file_name, pre_data_file_name,
                    post_data_file_name, prediction_file_name
                ]
            )
        self.data_split_name = data_split_name

    def get_df_from_args(
        self, column_names: Optional[Sequence[str]], source_df: pd.DataFrame,
        raw_data: Optional[Union[np.ndarray, pd.Series, pd.DataFrame]]
    ) -> pd.DataFrame:
        if column_names:
            return source_df[column_names]
        elif isinstance(raw_data, np.ndarray):
            return pd.DataFrame(raw_data)
        elif isinstance(raw_data, pd.Series):
            return raw_data.to_frame()
        else:
            return raw_data

    def drop_other_columns(self, input_data, other_columns):
        if input_data is not None:
            return input_data.drop(
                columns=other_columns, inplace=False, errors="ignore"
            )
        return None

    def _write_input_file(
        self,
        df,
        file_name_for_log,
        *,
        info_log=None,
        header=True,
        extension=None
    ):
        if df is not None:
            output_path = create_temp_file_path(extension=extension)
            df.to_csv(output_path, index=False, header=header, na_rep=NAN_REP)

            self.logger.debug(
                f"Saved {file_name_for_log} data file to {output_path}. Size of file: {os.path.getsize(output_path)}"
            )
            if info_log:
                self.logger.info(info_log)

            return output_path

        return None

    def _is_virtual_model(self) -> bool:
        model_meta = self.artifact_interaction_client.get_model_metadata(
            project_name=self._get_current_active_project_name(),
            model_name=self._get_current_active_model_name()
        )
        return model_meta["model_type"].lower() == "virtual"

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
        workspace_validation_utils.validate_score_type(
            self._get_score_type(), score_type
        )
        score_type = score_type or self._get_score_type()
        workspace_validation_utils.validate_ranking_ids(
            score_type, ranking_group_id_column_name,
            ranking_item_id_column_name
        )
        data_split_name = data_split_name or self._get_current_active_data_split_name(
        )
        prediction_col_name = prediction_col_name if prediction_col_name else [
            c for c in prediction_data.columns if c != id_col_name
        ]
        is_success = False
        try:
            self.add_data(
                data=prediction_data,
                data_split_name=data_split_name,
                column_spec=ColumnSpec(
                    id_col_name=id_col_name,
                    prediction_col_names=prediction_col_name,
                    ranking_group_id_column_name=ranking_group_id_column_name,
                    ranking_item_id_column_name=ranking_item_id_column_name,
                ),
                model_output_context=ModelOutputContext(
                    model_name=self._get_current_active_model_name(),
                    score_type=score_type,
                )
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    ingest_predictions_data_event_properties=
                    analytics_event_schema_pb.
                    IngestPredictionsDataEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_model_predictions",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                is_success=is_success
            )

    def add_model_feature_influences(
        self,
        feature_influence_data: pd.DataFrame,
        *,
        id_col_name: str,
        data_split_name: Optional[str] = None,
        background_split_name: Optional[str] = None,
        timestamp_col_name: Optional[str] = None,
        influence_type: Optional[str] = None,
        score_type: Optional[str] = None
    ):
        data_split_name = data_split_name or self._get_current_active_data_split_name(
        )
        background_split_name, _ = self._infer_background_split(
            background_split_name
        )
        system_col_names = (id_col_name, timestamp_col_name)
        feature_influence_col_names = [
            c for c in feature_influence_data.columns
            if c not in system_col_names
        ]
        is_success = False
        try:
            self.add_data(
                data=feature_influence_data,
                data_split_name=data_split_name,
                column_spec=ColumnSpec(
                    id_col_name=id_col_name,
                    timestamp_col_name=timestamp_col_name,
                    feature_influence_col_names=feature_influence_col_names
                ),
                model_output_context=ModelOutputContext(
                    model_name=self._get_current_active_model_name(),
                    score_type=score_type or self._get_score_type(),
                    background_split_name=background_split_name,
                    influence_type=influence_type or self.get_influence_type()
                )
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_feature_influences_event_properties=
                    analytics_event_schema_pb.
                    AddFeatureInfluencesEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_model_predictions",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=data_split_name,
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                is_success=is_success
            )

    def _validate_attach_model_object(self):
        self._ensure_project()
        self._ensure_data_collection()
        self._ensure_model()
        if not self._is_virtual_model():
            raise ValueError(
                "Attaching executable model objects is only supported for virtual model! This model is already executable."
            )

    def attach_packaged_python_model_object(
        self, model_object_dir: str, verify_model: bool = True
    ):
        self._validate_attach_model_object()
        if verify_model:
            self.verify_packaged_model(
                model_object_dir
            )  # full validation using split data
        else:
            verify_python_model_folder(
                model_object_dir, logger=self.logger
            )  # basic checking on folder structure

        model = self.project.get_model(
            self._get_current_active_model_name(),
            self._get_current_active_data_collection_name()
        )
        model.upgrade_virtual(
            self.artifact_interaction_client, ModelType.PyFunc, model_object_dir
        )

    def attach_python_model_object(
        self,
        model_object: Any,
        additional_pip_dependencies: Optional[Sequence[str]] = None,
        verify_model: bool = True,
    ):
        self._validate_attach_model_object()
        feature_transform_type = self._get_feature_transform_type_for_data_collection(
        )
        temp_staging_dir = tempfile.mkdtemp()
        shutil.rmtree(temp_staging_dir, ignore_errors=True)
        try:
            self.prepare_python_model_folder_from_model_object(
                temp_staging_dir,
                model_object,
                None,
                feature_transform_type=feature_transform_type,
                additional_pip_dependencies=additional_pip_dependencies,
            )
            self.attach_packaged_python_model_object(
                temp_staging_dir, verify_model=verify_model
            )
        finally:
            shutil.rmtree(temp_staging_dir, ignore_errors=True)

    def add_feature_metadata(
        self,
        feature_description_map: Optional[Mapping[str, str]] = None,
        group_to_feature_map: Optional[Mapping[str, Sequence[str]]] = None,
        missing_values: Optional[Sequence[str]] = None,
        force_update: bool = False
    ):
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        is_success = False
        try:
            self.logger.info(
                f"Uploading feature description for project: {project_name} and data_collection: {data_collection_name}"
            )
            preprocessed_cols = None
            postprocessed_cols = None
            if feature_description_map or group_to_feature_map:
                if self.get_data_splits():
                    with WorkspaceContextCleaner(self):
                        self.set_data_split(self.get_data_splits()[0])
                        preprocessed_cols = set(self.get_xs(0, 10).columns)
                        postprocessed_cols = set(
                            self._get_xs_postprocessed(0, 10).columns
                        )
            if feature_description_map:
                candidate_preprocessed_cols = list(
                    feature_description_map.keys()
                )
                if preprocessed_cols is not None and sorted(
                    preprocessed_cols
                ) != sorted(candidate_preprocessed_cols):
                    raise ValueError(
                        "Pre-features of data-collection do not agree with pre-features of `feature_description_map`!"
                    )
                preprocessed_cols = candidate_preprocessed_cols
            if group_to_feature_map:
                candidate_preprocessed_cols = [
                    feature for group in group_to_feature_map.values()
                    for feature in group
                ]
                if preprocessed_cols is not None and sorted(
                    preprocessed_cols
                ) != sorted(candidate_preprocessed_cols):
                    raise ValueError(
                        "Pre-features of data-collection or those of `feature_description_map` do not agree with those of `group_to_feature_map`!"
                    )
                preprocessed_cols = candidate_preprocessed_cols
            self.feature_client.upload_feature_description_and_group_metadata(
                project_name,
                data_collection_name,
                pre_features=preprocessed_cols,
                post_features=postprocessed_cols,
                feature_description_map=feature_description_map,
                missing_values=missing_values,
                group_to_feature_map=group_to_feature_map,
                force=force_update,
                only_update_metadata=True
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_feature_metadata_event_properties=
                    analytics_event_schema_pb.AddFeatureMetadataEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_feature_metadata",
                        data_collection_name=self.
                        _get_current_active_data_collection_name()
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                is_success=is_success
            )

    def _get_pre_to_post_feature_map(
        self
    ) -> Optional[Mapping[str, Sequence[str]]]:
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        return self.feature_client.get_pre_to_post_feature_map(
            project_name, data_collection_name
        )

    def _get_feature_description_map(
        self
    ) -> Optional[Mapping[str, Sequence[str]]]:
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        return self.feature_client.get_feature_description_map(
            project_name, data_collection_name
        )

    def _get_extra_data(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        self._ensure_project()
        self._ensure_data_collection()
        self._ensure_base_data_split()
        ret = self._get_xs_for_split(
            self._get_current_active_data_split_name(),
            start,
            stop,
            pre_data=False,
            extra_data=True,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group
        )
        if ret is None or ret.shape[0] == 0:
            return None
        return ret

    def get_xs(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        extra_data: bool = False,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> pd.DataFrame:
        self._ensure_project()
        self._ensure_data_collection()
        self._ensure_base_data_split()
        return self._get_xs_for_split(
            self._get_current_active_data_split_name(),
            start,
            stop,
            extra_data=extra_data,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group
        )

    def _get_xs_for_split(
        self,
        data_split_name: str,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        pre_data: bool = True,
        extra_data: bool = False,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None,
        get_post_processed_data: bool = False
    ):
        split_metadata = self.artifact_interaction_client.get_split_metadata(
            self._get_current_active_project_name(),
            self._get_current_active_data_collection_name(), data_split_name
        )
        model_id = self.model.model_id if self.model is not None else None
        return self.aiq_client.get_xs(
            self.project.id,
            split_metadata["id"],
            split_metadata["data_collection_id"],
            start,
            stop,
            exclude_feature_values=not pre_data and not get_post_processed_data,
            extra_data=extra_data,
            model_id=model_id,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group,
            get_post_processed_data=get_post_processed_data
        ).response

    def _get_xs_postprocessed(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> pd.DataFrame:
        self._ensure_project()
        self._ensure_data_collection()
        self._ensure_base_data_split()
        return self._get_xs_for_split(
            self._get_current_active_data_split_name(),
            start,
            stop,
            get_post_processed_data=True,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group
        )

    def get_ys(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None
    ) -> pd.DataFrame:
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        split_name = self._ensure_base_data_split()
        split_metadata = self.artifact_interaction_client.get_split_metadata(
            project_name, data_collection_name, split_name
        )
        model_id = self.model.model_id if self.model is not None else None
        return self.aiq_client.get_ys(
            self.project.id,
            split_metadata["id"],
            split_metadata["data_collection_id"],
            start,
            stop,
            model_id=model_id,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group
        ).response

    def get_feature_influences(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        score_type: Optional[str] = None,
        system_data: bool = False,
        by_group: bool = False,
        num_per_group: Optional[int] = None,
    ) -> pd.DataFrame:
        return self.get_explainer(self.data_split_name).get_feature_influences(
            start=start,
            stop=stop,
            score_type=score_type,
            system_data=system_data,
            by_group=by_group,
            num_per_group=num_per_group
        )

    def get_tokens(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False
    ) -> Union[pd.Series, pd.DataFrame]:
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        split_name = self._ensure_base_data_split()
        split_metadata = self.artifact_interaction_client.get_split_metadata(
            project_name, data_collection_name, split_name
        )
        return self.aiq_client.get_tokens(
            self.project.id,
            self.model.model_id,
            split_metadata["id"],
            start,
            stop,
            include_system_data=system_data,
        ).response

    def get_embeddings(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False
    ) -> Union[pd.Series, pd.DataFrame]:
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        split_name = self._ensure_base_data_split()
        split_metadata = self.artifact_interaction_client.get_split_metadata(
            project_name, data_collection_name, split_name
        )
        return self.aiq_client.get_embeddings(
            self.project.id,
            self.model.model_id,
            split_metadata["id"],
            start,
            stop,
            include_system_data=system_data,
        ).response

    def get_model_threshold(self) -> float:
        self._validate_get_model_threshold()
        return self.cs_client.get_classification_threshold(
            self.project.id, self.model.model_id, self._get_score_type()
        )[0]

    def update_model_threshold(self, classification_threshold: float) -> None:
        self._ensure_project()
        self._ensure_model()
        if self._get_output_type() == "regression":
            self.logger.warning(
                "Regression models do not use a threshold. Ignoring request to update."
            )
            return
        score_type = self._get_score_type()
        classification_threshold = workspace_validation_utils.validate_model_threshold(
            classification_threshold, score_type
        )
        self.cs_client.update_classification_threshold_configuration(
            self.project.id,
            self.model.model_id,
            classification_threshold=classification_threshold,
            score_type=score_type
        )

    def set_influences_background_data_split(
        self,
        data_split_name: str,
        data_collection_name: Optional[str] = None
    ) -> None:
        self._ensure_project()
        if data_collection_name:
            self._validate_data_collection(data_collection_name)
        else:
            data_collection_name = self._ensure_data_collection()
        self._validate_data_split(data_split_name, data_collection_name)
        background_split_id = self.artifact_interaction_client.get_split_metadata(
            self._get_current_active_project_name(),
            data_collection_name,
            split_name=data_split_name
        )["id"]
        self.cs_client.set_base_split(
            self.project.id, self.data_collection.id, background_split_id
        )

    def get_influences_background_data_split(
        self, data_collection_name: Optional[str] = None
    ) -> str:
        self._ensure_project()
        if not data_collection_name:
            data_collection_name = self._ensure_data_collection()
            data_collection_id = self.data_collection.id
        else:
            self._validate_data_collection(data_collection_name)
            data_collection_id = self.artifact_interaction_client.get_data_collection_id(
                self.project.id, data_collection_name
            )

        background_split_id = self.cs_client.get_base_split(
            self.project.id,
            data_collection_id,
        )
        if not background_split_id:
            raise ValueError(
                f"Background data split has not been set for data collection \"{data_collection_name}\"! Please set it using `set_influences_background_data_split`"
            )
        return self.artifact_interaction_client.get_split_metadata_by_id(
            self.project.id, split_id=background_split_id
        )["name"]

    def add_segment_group(
        self, name: str, segment_definitions: Mapping[str, str]
    ) -> None:
        self._validate_add_segment_group(name, segment_definitions)
        split_metadata = self.artifact_interaction_client.get_split_metadata(
            self._get_current_active_project_name(),
            self._get_current_active_data_collection_name(),
            self._get_current_active_data_split_name()
        )
        is_success = False
        try:
            self.aiq_client.add_segment_group(
                self.project.id, name, segment_definitions,
                split_metadata["data_collection_id"], split_metadata["id"],
                self._get_score_type()
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_segment_group_event_properties=analytics_event_schema_pb
                    .AddSegmentGroupEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_segment_group",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        data_split_name=split_metadata["name"]
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                data_split_id=split_metadata["id"],
                is_success=is_success
            )

    def set_as_protected_segment(
        self, segment_group_name: str, segment_name: str
    ):
        segment_groups = self.aiq_client.get_wrapped_segmentations(
            self.project.id
        ).response
        if segment_group_name not in segment_groups:
            raise NotFoundError(
                f"Segment group \"{segment_group_name}\" does not exist!"
            )
        if segment_name not in segment_groups[segment_group_name].get_segments(
        ):
            raise NotFoundError(
                f"Segment \"{segment_name}\" does not exist in segment group \"{segment_group_name}\"!"
            )
        self.aiq_client.set_as_protected_segment(
            self.project.id, segment_groups[segment_group_name].id, segment_name
        )

    def delete_segment_group(self, name: str) -> None:
        self._ensure_project()
        self.aiq_client.delete_segment_group(self.project.id, name)

    def get_segment_groups(self) -> Mapping[str, Mapping[str, str]]:
        self._ensure_project()
        segment_groups = self.aiq_client.get_wrapped_segmentations(
            self.project.id, convert_model_ids_to_model_names=True
        ).response
        return self._get_str_desc_of_segment_groups(segment_groups)

    def get_explainer(
        self,
        base_data_split: Optional[str] = None,
        comparison_data_splits: Optional[Sequence[str]] = None
    ) -> Union[RemoteExplainer, RemoteNLPExplainer]:
        self._ensure_project()
        self._ensure_model()
        base_data_split = base_data_split or self._get_current_active_data_split_name(
        )
        if self._get_input_type() == "tabular":
            return RemoteExplainer(
                self, self.project, self.model,
                self._get_current_active_data_collection_name(),
                base_data_split, comparison_data_splits
            )
        elif workspace_validation_utils.is_nlp_project(self._get_input_type()):
            return RemoteNLPExplainer(
                self, self.project, self.model,
                self._get_current_active_data_collection_name(), base_data_split
            )
        else:
            raise ValueError(
                f"Unsupported input type {self.project.input_type}"
            )

    def get_ingestion_client(self) -> IngestionClient:
        project_name = self._ensure_project()
        data_collection_name = self._ensure_data_collection()
        return IngestionClient(
            project=project_name,
            default_score_type=self._get_score_type(),
            data_collection=data_collection_name,
            artifact_interaction_client=self.artifact_interaction_client,
            data_service_client=self.data_service_client,
            configuration_service_client=self.cs_client,
            logger=self.logger
        )

    def get_ingestion_operation_status(
        self,
        operation_id: Optional[str] = None,
        idempotency_id: Optional[str] = None
    ) -> dict:
        project_name = self._ensure_project()
        project_id = self.project.id
        if operation_id:
            status_resp = self.data_service_client.get_materialize_data_status(
                project_id=project_id,
                materialize_operation_id=operation_id,
                throw_on_error=True
            )
        elif idempotency_id:
            status_resp = self.data_service_client.get_materialize_data_status_by_idempotency(
                project_id=project_id,
                idempotency_id=idempotency_id,
                throw_on_error=True
            )
        else:
            raise ValueError(
                "Operation id and idempotency id are both empty, please specify at least one of them"
            )
        return {
            "project_name":
                project_name,
            "operation_started_time":
                datetime.fromtimestamp(
                    status_resp.operation_started_time.seconds
                ).strftime("%Y-%m-%d %H:%M:%S"),
            "operation_status":
                MaterializeStatus.Name(status_resp.status),
            "operation_id":
                status_resp.materialize_operation_id,
            "split_id":
                status_resp.output_split_id,
        }

    def get_context(self) -> Mapping[str, str]:
        return {
            "project":
                self.project.name if self.project else "",
            "data-collection":
                self.data_collection.name if self.data_collection else "",
            "data-split":
                self.data_split_name or "",
            "model":
                self.model.model_name if self.model else "",
            "connection-string":
                self.connection_string
        }

    def add_model_metadata(
        self,
        train_split_name: Optional[str] = None,
        train_parameters: Optional[Mapping[str, Any]] = None,
        overwrite: bool = False
    ) -> None:
        self._ensure_project()
        self._ensure_model()
        is_success = False
        try:
            validate_model_metadata(
                train_split_name=train_split_name,
                existing_split_names=self.get_data_splits(),
                train_parameters=train_parameters,
                logger=self.logger
            )
            self.artifact_interaction_client.add_train_split_to_model(
                project_name=self._get_current_active_project_name(),
                model_name=self._get_current_active_model_name(),
                train_split_name=train_split_name,
                overwrite=overwrite
            )
            self.artifact_interaction_client.add_train_parameters_to_model(
                project_name=self._get_current_active_project_name(),
                model_name=self._get_current_active_model_name(),
                train_parameters=train_parameters,
                overwrite=overwrite
            )
            is_success = True
        finally:
            self.useranalytics_client.track_event(
                structured_event_properties=analytics_event_schema_pb.
                StructuredEventProperties(
                    add_model_metadata_event_properties=analytics_event_schema_pb
                    .AddModelMetadataEventProperties(
                        workspace="remote",
                        project_name=self._get_current_active_project_name(),
                        command="add_model_metadata",
                        data_collection_name=self.
                        _get_current_active_data_collection_name(),
                        model_name=self._get_current_active_model_name(),
                    )
                ),
                project_id=None if self.project is None else self.project.id,
                data_collection_id=None
                if self.data_collection is None else self.data_collection.id,
                model_id=None if self.model is None else self.model.model_id,
                is_success=is_success
            )

    def delete_model_metadata(self) -> None:
        self._ensure_project()
        self._ensure_model()
        self.ar_client.update_model_metadata(
            self.project.id, self._get_current_active_model_name(), {
                "train_split_id": "",
                "train_parameters": {}
            }
        )

    def get_model_metadata(self) -> Mapping[str, Union[str, Mapping[str, str]]]:
        self._ensure_project()
        self._ensure_model()
        return self._get_model_metadata(self._get_current_active_model_name())

    def _get_model_metadata(
        self, model_name: str
    ) -> Mapping[str, Union[str, Mapping[str, str]]]:
        model_metadata = self.artifact_interaction_client.get_model_metadata(
            self.project.id, model_name=model_name, as_json=True
        )
        train_split_name = None
        if model_metadata["training_metadata"]["train_split_id"]:
            train_split_name = self.artifact_interaction_client.get_split_metadata_by_id(
                self.project.id,
                model_metadata["training_metadata"]["train_split_id"]
            )["name"]
        if not model_metadata["training_metadata"].get("parameters"):
            model_metadata["training_metadata"]["parameters"] = None
        return {
            "train_split_name":
                train_split_name,
            "train_parameters":
                model_metadata["training_metadata"]["parameters"],
            "model_provenance":
                model_metadata["model_provenance"]
        }

    def _data_split_has_ids(self) -> bool:
        metadata = self.artifact_interaction_client.get_split_metadata(
            self._get_current_active_project_name(),
            self._get_current_active_data_collection_name(),
            self._get_current_active_data_split_name()
        )
        return "unique_id_column_name" in metadata

    def _get_score_type(self) -> str:
        self._ensure_project()
        return self._get_score_type_for_project(self.project.id)

    def _get_score_type_for_project(self, project_id: str) -> str:
        project_metadata = self.artifact_interaction_client.get_project_metadata(
            project_id
        )
        return get_string_from_qoi_string(
            project_metadata["settings"]["score_type"]
        )

    def _get_input_type(self):
        self._ensure_project()
        return self._fetch_and_parse_project_metadata(
            self._get_current_active_project_name()
        )["input_type"]

    def _save_object_file(self, path: str, name: str, obj: Any):
        path_to_file = os.path.join(path, name)
        with open(path_to_file, 'wb+') as handle:
            cloudpickle.dump(obj, handle)
        return path_to_file

    def verify_nn_wrappers(
        self,
        clf,
        model_run_wrapper: base.Wrappers.ModelRunWrapper,
        split_load_wrapper: base.Wrappers.SplitLoadWrapper,
        model_load_wrapper: base.Wrappers.ModelLoadWrapper,
        tokenizer_wrapper: Optional[nlp.Wrappers.TokenizerWrapper] = None,
        attr_config: AttributionConfiguration = None
    ):
        from truera.client.cli.verify_nn_ingestion import verify
        from truera.client.cli.verify_nn_ingestion import VerifyHelper

        self._ensure_project()
        if model_load_wrapper is None:
            raise ValueError(
                f"The current project: {self.get_context()['project']} is a remote project. pass a ModelLoadWrapper using `model_load_wrapper`"
            )
        project_input_type = self.project.input_type
        score_type = self._get_score_type()
        output_type = get_output_type_from_score_type(score_type)

        verify_helper: VerifyHelper = verify.get_helper(
            model_input_type=project_input_type,
            model_output_type=output_type,
            attr_config=attr_config,
            model=clf,
            split_load_wrapper=split_load_wrapper,
            model_run_wrapper=model_run_wrapper,
            model_load_wrapper=model_load_wrapper,
            tokenizer_wrapper=tokenizer_wrapper,
        )

        verify.verify_model(verify_helper)
        super(RemoteTrueraWorkspace,
              self)._verify_nn_wrappers(verify_helper, logger=self.logger)

    def get_nn_user_configs(
        self
    ) -> Union[AttributionConfiguration, RNNUserInterfaceConfiguration]:
        self._ensure_model()
        model_metadata = self.artifact_interaction_client.get_model_metadata(
            self.project.id, model_name=self.model.model_name, as_json=False
        )
        if model_metadata.HasField("rnn_attribution_config"):
            nn_attribution_config = model_metadata.rnn_attribution_config
        elif model_metadata.HasField("nlp_attribution_config"):
            nn_attribution_config = model_metadata.nlp_attribution_config
        return (model_metadata.rnn_ui_config, nn_attribution_config)

    def update_nn_user_config(
        self, config: Union[AttributionConfiguration,
                            RNNUserInterfaceConfiguration]
    ):
        self._ensure_model()
        if not isinstance(
            config, (AttributionConfiguration, RNNUserInterfaceConfiguration)
        ):
            raise ValueError(
                f"Trying to add an unsupported NN config: {config}. Supported NN config types: [`AttributionConfiguration`, `RNNUserInterfaceConfiguration`]"
            )
        if isinstance(config, RNNUserInterfaceConfiguration):
            param_name = "rnn_ui_config"
        elif isinstance(config, RNNAttributionConfiguration):
            param_name = "rnn_attribution_config"
        elif isinstance(config, NLPAttributionConfiguration):
            param_name = "nlp_attribution_config"

        self.ar_client.update_model_metadata(
            self.project.id, self.model.model_name, {param_name: config}
        )

    def _add_split_from_data_source(
        self,
        data_split_name: str,
        data: Union[Table, str],
        label_col_name: str,
        id_col_name: str,
        split_type: str,
        timestamp_col_name: str,
        split_mode: sm_pb.SplitMode,
        train_baseline_model: Optional[bool] = False,
        **kwargs
    ):
        if isinstance(data, str):
            temp_data_source_name = data_split_name + str(uuid.uuid4())
            rowset = self.get_ingestion_client().add_data_source(
                temp_data_source_name, data, **kwargs
            )
        elif isinstance(data, Table):
            rowset = data
        else:
            raise ValueError("Expected data to either `Table` or `str` (URI).")

        # Presence of model is verified in _validate_add_data_split()
        prediction_col_name = kwargs.pop("prediction_col_name", None)
        if prediction_col_name:
            kwargs["model_name"] = self._get_current_active_model_name()
            kwargs["score_type"] = self._get_score_type()

        result = rowset.add_data_split(
            data_split_name=data_split_name,
            data_split_type=split_type,
            label_col_name=label_col_name,
            id_col_name=id_col_name,
            prediction_col_name=prediction_col_name,
            timestamp_col_name=timestamp_col_name,
            split_mode=split_mode,
            train_baseline_model=train_baseline_model,
            **kwargs
        )
        if result["status"] == "OK":
            self.data_split_name = data_split_name
            return result
        result[
            "check_status_lambda"
        ] = lambda: self.artifact_interaction_client.get_materialize_operation_status(
            self.project.id, result["operation_id"]
        )
        self.logger.warning(
            "Split is being created, you can check the status of the operation by using `check_status_lambda`. "
            "To work on this split, use set_data_split once the operation is successful."
        )
        return result

    def _fetch_and_parse_project_metadata(self, project_name: str) -> dict:
        try:
            project_metadata = self.artifact_interaction_client.get_project_metadata(
                project_name
            )
            input_type = project_metadata["settings"]["input_data_format"
                                                     ].lower()
            score_type = get_string_from_qoi_string(
                project_metadata["settings"]["score_type"]
            )
            return {
                'id': project_metadata['id'],
                'created_at': project_metadata['created_at'],
                'input_type': input_type,
                'score_type': score_type
            }
        except MetadataNotFoundException:
            return {}

    def _delete_empty_project(self):
        for data_source_name in self.get_data_sources():
            if len(data_source_name) > 0:
                self.delete_data_source(data_source_name)
        self.artifact_interaction_client.delete_project(self.project.id)

    def download_nn_artifact(
        self, artifact_type: ArtifactType, download_basepath: str
    ) -> str:
        """ Downloads NN artifacts from the TruEra deployment to a local path.
        This differs from current tabular implementation where data management is taken care of by TruEra's AIQ service.
        The NN non-remote aiq `truera.nlp/rnn.general.aiq.py` are stand-ins that try to best recreate aiq services. It accesses file paths with 
        special naming that mimics metarepo project/model/split conventions. All cache items end in a file folder of files
        in the form of memmaps, pickle, or txt files.

        Args:
            artifact_type: A datasplit, model, or cache designation. Determines what is being downloaded.
            download_basepath: The path to which files are to be downloaded. NN Artifacts are in memmap, pickle, or text files.

        Returns:
            The path of the downloaded files.
        """
        download_project_path = os.path.join(download_basepath, self.project.id)
        if artifact_type == ArtifactType.datasplit:
            artifact_id = self.data_split_name
            scoping_artifact_ids = [
                self._get_current_active_data_collection_name()
            ]
            download_path = os.path.join(
                download_project_path, "datasplits",
                self._get_current_active_data_collection_name(), artifact_id
            )
        elif artifact_type == ArtifactType.model:
            artifact_id = self.model.model_name
            scoping_artifact_ids = []
            download_path = os.path.join(
                download_project_path, "models", artifact_id
            )
        elif artifact_type == ArtifactType.cache:
            artifact_id = f"{self.model.model_name}__{self.data_split_name}___explanation_cache_INTEGRATED_GRADIENTS"
            scoping_artifact_ids = [
                "explanation_caches", self.model.model_id,
                self._get_current_active_data_collection_name(),
                self.data_split_name,
                self._get_score_type(),
                self.get_influences_background_data_split(),
                ExplanationAlgorithmType.Name(
                    ExplanationAlgorithmType.INTEGRATED_GRADIENTS
                )
            ]
            download_path = os.path.join(
                download_project_path, "caches", *scoping_artifact_ids,
                artifact_id
            )
        else:
            raise ValueError(
                f"Unsupported artifact_type for download: {artifact_type}"
            )
        self.ar_client.download_artifact(
            src_project_id=self.project.name,
            src_artifact_type=artifact_type,
            src_artifact_id=artifact_id,
            src_intra_artifact_path='',
            scoping_artifact_ids=scoping_artifact_ids,
            dest=download_path
        )
        return download_path

    def _validate_data_split(
        self, data_split_name: str, data_collection_name: str
    ) -> None:
        available_splits = self.artifact_interaction_client.get_all_datasplits_in_data_collection(
            self.project.id, data_collection_name
        )
        if data_split_name not in available_splits:
            raise ValueError(
                f"No such data split \"{data_split_name}\" in data collection \"{data_collection_name}\"!"
            )

    def reset_context(self):
        self.set_model(None)
        self.set_data_collection(None)
        self.project = None

    def prepare_python_model_folder_from_model_object(
        self,
        output_dir: str,
        model: Any,
        transformer: Optional[Any],
        feature_transform_type: FeatureTransformationType,
        additional_pip_dependencies: Optional[Sequence[str]] = None,
        additional_modules: Optional[Sequence[Any]] = None,
        **kwargs
    ) -> str:
        self._validate_additional_modules(additional_modules)
        additional_pip_dependencies = PipDependencyParser(
            additional_pip_dependencies
        )
        additional_pip_dependencies.add_default_model_runner_dependencies()
        # devnote: the `python_version` kwarg is undocumented; should be used as an override only if absolutely necessary
        python_version = kwargs.get("python_version", get_python_version_str())
        output_type = self._get_output_type()
        if callable(model):
            ModelPredictPackager(
                model, transformer, output_type, python_version,
                additional_pip_dependencies
            ).save_model(
                self.logger, output_dir, additional_modules=additional_modules
            )
        else:
            (name,
             module) = (model.__class__.__name__, model.__class__.__module__)
            if module.startswith("xgboost"):
                self.logger.info("Uploading xgboost model: %s", name)
                XgBoostModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif module.startswith("sklearn.pipeline"):
                self.logger.info(f"Uploading sklearn.pipeline model: {name}")
                if feature_transform_type == FEATURE_TRANSFORM_TYPE_PRE_POST_DATA:
                    raise ValueError(
                        "Pre-/post-data transform is not supported for sklearn pipeline object."
                    )

                SklearnPipelineModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies, feature_transform_type
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif module.startswith("sklearn"):
                self.logger.info("Uploading sklearn model: %s", name)
                SklearnModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif module == "catboost.core":
                self.logger.info("Uploading catboost model")
                CatBoostModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(self.logger, output_dir)
            elif module == "lightgbm.basic" and name == "Booster":
                self.logger.info("Uploading lightgbm booster.")
                LightGBMModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif module == "lightgbm.sklearn" and name == "LGBMClassifier":
                self.logger.info("Uploading lightgbm classifier.")
                if output_type != "classification":
                    raise ValueError(
                        f"LGBMClassifier expected for classification model, found {output_type}."
                    )
                LightGBMModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif module == "lightgbm.sklearn" and name == "LGBMRegressor":
                self.logger.info("Uploading lightgbm regressor.")
                if output_type != "regression":
                    raise ValueError(
                        f"LGBMRegressor expected for regression model, found {output_type}."
                    )
                LightGBMModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif module == "lightgbm.sklearn" and name == "LGBMRanker":
                self.logger.info("Uploading lightgbm ranker.")
                if output_type != "ranking":
                    raise ValueError(
                        f"LGBMRanker expected for ranking model, found {output_type}."
                    )
                LightGBMModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(
                    self.logger,
                    output_dir,
                    additional_modules=additional_modules
                )
            elif is_supported_pyspark_tree_model(model):
                self.logger.info("Uploading pyspark tree model.")
                if output_type not in name.lower():
                    raise ValueError(
                        f"Expected a {output_type} model, but provided a model of class {name}!"
                    )
                PySparkModelPackager(
                    model, transformer, output_type, python_version,
                    additional_pip_dependencies
                ).save_model(self.logger, output_dir)
            else:
                raise NotSupportedError(
                    f"Model of type: {module}.{name} is not supported. Serialize the model and use `add_packaged_python_model` to upload "
                )

    def schedule_ingestion(self, raw_json: str, cron_schedule: str):
        return self.scheduled_ingestion_client.schedule_new(
            json=raw_json,
            schedule=self.scheduled_ingestion_client.
            serialize_schedule(cron_schedule),
        )

    def get_scheduled_ingestion(self, workflow_id: str):
        return self.scheduled_ingestion_client.get(workflow_id)

    def _builds_scheduled_ingestion_request_tree_from_split(
        self,
        split_name,
        override_split_name: str = None,
        append: bool = False
    ):
        split_metadata = self.artifact_interaction_client.get_split_metadata(
            self._get_current_active_project_name(),
            self._get_current_active_data_collection_name(), split_name
        )
        materialize_operation_id = split_metadata["provenance"][
            "materialized_by_operation"]
        materialize_response = self.data_service_client.get_materialize_data_status(
            project_id=self.project.id,
            materialize_operation_id=materialize_operation_id,
            throw_on_error=True
        )
        return self.scheduled_ingestion_client.build_request_tree(
            materialize_status_response=materialize_response,
            project_id=self.project.id,
            override_split_name=override_split_name,
            existing_split_id=split_metadata['id']
            if append and not override_split_name else None
        )

    def schedule_existing_data_split(
        self,
        split_name: str,
        cron_schedule: str,
        override_split_name: str = None,
        append: bool = True
    ):
        return self.scheduled_ingestion_client.schedule_new(
            tree=self._builds_scheduled_ingestion_request_tree_from_split(
                split_name, override_split_name, append=append
            ),
            schedule=self.scheduled_ingestion_client.
            serialize_schedule(cron_schedule),
        )

    def serialize_split(
        self,
        split_name: str,
        override_split_name: str = None,
        append: bool = True
    ) -> str:
        return MessageToJson(
            self._builds_scheduled_ingestion_request_tree_from_split(
                split_name, override_split_name, append=append
            )
        )

    def cancel_scheduled_ingestion(self, workflow_id: str) -> str:
        return self.scheduled_ingestion_client.cancel(workflow_id)

    def list_scheduled_ingestions(
        self, last_key: Optional[str] = None, limit: int = 50
    ) -> str:
        self._ensure_project()
        self._ensure_data_collection()
        return self.scheduled_ingestion_client.get_workflows(
            self.project.id,
            self.data_collection.id,
            last_key=last_key,
            limit=limit,
        )

    def register_schema(
        self,
        schemas,
    ):
        self.data_service_client.register_schema(
            self.project.id,
            self.data_collection.id,
            schemas,
            request_context=None,
            start_streaming=True
        )

    def _get_feature_transform_type_for_data_collection(
        self, data_collection_name: Optional[str] = None
    ):
        if not data_collection_name:
            data_collection_name = self.data_collection.name
        dc_metadata = self.project.get_data_collection_metadata(
            data_collection_name, as_json=False
        )
        return dc_metadata.feature_transform_type

    def list_monitoring_tables(self) -> str:
        return MessageToJson(
            self.monitoring_control_plane_client.list_druid_tables(
                project_id=self.project.id
            )
        )

    def _get_context_ids(self) -> Mapping[str, str]:
        data_split_id = ""
        if self.data_split_name:
            data_split_metadata = self.artifact_interaction_client.get_split_metadata(
                self._get_current_active_project_name(),
                self._get_current_active_data_collection_name(),
                self._get_current_active_data_split_name()
            )
            data_split_id = data_split_metadata["id"]
        return {
            "project":
                self.project.id if self.project is not None else "",
            "data-collection":
                self.data_collection.id
                if self.data_collection is not None else "",
            "data-split":
                data_split_id,
            "model":
                self.model.model_id if self.model is not None else "",
        }
