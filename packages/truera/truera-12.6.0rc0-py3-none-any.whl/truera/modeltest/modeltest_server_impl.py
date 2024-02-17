from __future__ import annotations

import asyncio
import dataclasses
import logging
import re
import traceback
from typing import (
    Any, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING, Union
)
import uuid

from cachetools import cached
from cachetools import TTLCache
import grpc
import numpy as np
from temporalio.client import Client as temporalio_client
import temporalio.converter

from truera.aiq.artifact_metadata_client import AIQArtifactMetadataClient
from truera.artifactrepo.utils.proto_utils import transform_split_to_public
from truera.client.errors import NotFoundError
from truera.client.intelligence.segment import Segment
from truera.client.private.metarepo import DatasetDao
from truera.client.private.metarepo import DataSplitDao
from truera.client.private.metarepo import ModelDao
from truera.client.private.metarepo import ModelTestDao
from truera.client.private.metarepo import ProjectDao
from truera.client.private.metarepo import Segmentation as SegmentationDao
from truera.client.public.auth_details import AuthDetails
from truera.client.services.aiq_client import AiqClient
from truera.client.services.aiq_client import AiqClientResponse
from truera.client.services.aiq_client import ModelBiasRequest
from truera.client.services.aiq_client import ModelOutputSpec
from truera.client.services.artifactrepo_client import ArtifactRepoClient
from truera.modeltest.baseline_model_creation_workflow import \
    BaselineModelCreationRequest
from truera.modeltest.baseline_model_creation_workflow import \
    BaselineModelCreationWorkflow
from truera.modeltest.baseline_model_data_converter import \
    BaselineModelPayloadConverter
from truera.modeltest.modeltest_cache_utils import feature_importance_cache_key
from truera.modeltest.modeltest_cache_utils import performance_metric_cache_key
# pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyResult as _PBAccuracyResult
from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyType as _PBAccuracyType
from truera.protobuf.public.aiq.distance_pb2 import \
    DistanceType as _PBDistanceType
from truera.protobuf.public.aiq.intelligence_service_pb2 import \
    BatchCompareModelOutputResponse as _PBBatchCompareModelOutputResponse
from truera.protobuf.public.aiq.intelligence_service_pb2 import \
    BiasResult as _PBBiasResult
from truera.protobuf.public.aiq.intelligence_service_pb2 import \
    BiasType as _PBBiasType
from truera.protobuf.public.aiq.intelligence_service_pb2 import ModelInputSpec
from truera.protobuf.public.data.segment_pb2 import SegmentID as _PBSegmentID
# pylint: enable=no-name-in-module
from truera.protobuf.public.modeltest import modeltest_pb2
from truera.protobuf.public.modeltest import modeltest_service_pb2
from truera.protobuf.public.modeltest import modeltest_service_pb2_grpc
# pylint: disable=no-name-in-module
from truera.protobuf.public.modeltest.modeltest_pb2 import \
    FairnessTest as _PBFairnessTest
from truera.protobuf.public.modeltest.modeltest_pb2 import \
    FeatureImportanceTest as _PBFeatureImportanceTest
from truera.protobuf.public.modeltest.modeltest_pb2 import \
    ModelTest as _PBModelTest
from truera.protobuf.public.modeltest.modeltest_pb2 import \
    ModelTestType as _PBModelTestType
from truera.protobuf.public.modeltest.modeltest_pb2 import \
    StabilityTest as _PBStabilityTest
from truera.protobuf.public.modeltest.modeltest_pb2 import \
    TestThreshold as _PBTestThreshold
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFairnessTestGroupRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFairnessTestGroupResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFairnessTestRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFairnessTestResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFeatureImportanceTestGroupRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFeatureImportanceTestGroupResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFeatureImportanceTestRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateFeatureImportanceTestResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreatePerformanceTestGroupRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreatePerformanceTestGroupResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreatePerformanceTestRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreatePerformanceTestResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateStabilityTestGroupRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateStabilityTestGroupResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateStabilityTestRequest
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateStabilityTestResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    CreateTestsFromSplitResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    GetModelTestGroupsResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    GetModelTestsResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    GetTestResultsForModelResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    ModelTestGroup
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    StartBaselineModelWorkflowResponse
from truera.protobuf.public.modeltest.modeltest_service_pb2 import \
    TestResultType as _PBTestResultType
# pylint: enable=no-name-in-module
from truera.public.artifact_repo_lib import ensure_valid_identifier
import truera.public.feature_influence_constants as fi_constants
from truera.public.model_test_constants import DEFAULT_PERFORMANCE_TEST_METRICS
from truera.utils import aiq_proto
from truera.utils import config_util
from truera.utils.aiq_raw_metarepo_use_utils import _filter_to_active_splits
from truera.utils.aiq_raw_metarepo_use_utils import \
    check_if_split_not_prod_split
from truera.utils.aiq_raw_metarepo_use_utils import filter_to_non_prod_splits
from truera.utils.check_permission_helper import REQUEST_CTX_TMP_TENANT
import truera.utils.check_permission_helper as check_permission_helper
from truera.utils.filter_utils import FilterProcessor
from truera.utils.logging_context.grpc_servicer_context import \
    initialize_grpc_servicer_context
from truera.utils.truera_status import TruEraAlreadyExistsError
from truera.utils.truera_status import TruEraInternalError
from truera.utils.truera_status import TruEraInvalidArgumentError
from truera.utils.truera_status import TruEraNotFoundError
from truera.utils.truera_status import TruEraUnsupportedError

if TYPE_CHECKING:
    from truera.analytics.loader.metarepo_client import MetarepoClient
    from truera.authn.usercontext import RequestContext
    from truera.authn.usercontext import RequestContextHelper
    from truera.client.private.rbac import Rbac
    from truera.protobuf.model_pb2 import Model as _PBModel
    from truera.protobuf.public.data.data_split_pb2 import \
        DataSplit as _PBDataSplit
    from truera.protobuf.public.data.segment_pb2 import Segment as _PBSegment

_DEFAULT_PERFORMANCE_TEST_NAME = "Default Performance Test"
_DEFAULT_FAIRNESS_TEST_NAME = "Default Fairness Test"
_DEFAULT_STABILITY_TEST_NAME = "Default Stability Test"

_BASE_ERROR_MESSAGE = "Error in determining test result"


class ModelTestServiceServicer(
    modeltest_service_pb2_grpc.ModelTestServiceServicer
):

    def __init__(
        self,
        client_config: Any,
        server_config: Any,
        metarepo_client: MetarepoClient,
        request_ctx_helper: RequestContextHelper,
        *,
        rbac_client: Optional[Rbac] = None,
        use_temporal: bool = False
    ):
        self.logger = logging.getLogger(__name__)
        self.metarepo_client = metarepo_client
        self.rbac_client = rbac_client
        self.artifact_metadata_client = AIQArtifactMetadataClient(client_config)
        self.request_ctx_helper = request_ctx_helper
        self.datasplit_dao = DataSplitDao(self.metarepo_client)
        self.dataset_dao = DatasetDao(self.metarepo_client)
        self.model_dao = ModelDao(self.metarepo_client)
        self.project_dao = ProjectDao(self.metarepo_client)
        self.segmentation_dao = SegmentationDao(self.metarepo_client)
        self.modeltest_dao = ModelTestDao(self.metarepo_client)
        self.aiq_connection_string = config_util.get_config_value(
            client_config, 'aiq', 'url', None
        )
        self.mrc_connection_string = config_util.get_config_value(
            client_config, 'remote-model', 'url', None
        )
        self.ar_connection_string = config_util.get_config_value(
            client_config, 'artifactrepo', 'url', None
        )

        self.ds_connection_string = config_util.get_config_value(
            client_config, 'dataservice', 'url', None
        )
        # TODO: Pass valid request context, deprecate mock context (TTV-326)
        try:
            self._assign_test_group_for_legacy_tests(REQUEST_CTX_TMP_TENANT)
        except Exception as exc:
            self.logger.error(
                f"{exc}. Failed to handle conversion of legacy tests (if any)."
            )
            self.logger.error(traceback.format_exc())
        self.logger.info("Started model test service")
        self.client_config = client_config
        self.use_temporal = use_temporal
        self.temporal_namespace = config_util.get_config_value(
            server_config, "temporalNamespace", None, ""
        )

    def _check_if_project_exists(
        self, project_id: str, context: grpc.ServicerContext
    ):
        request_ctx = self.request_ctx_helper.create_request_context_grpc(
            context
        )
        project_metadata = self.project_dao.get_by_id(
            obj_id=project_id, request_ctx=request_ctx
        )
        if not project_metadata:
            raise TruEraNotFoundError(
                f"Provided project_id does not exist: {project_id}"
            )

    def _check_if_model_exists(
        self, request_ctx: RequestContext, model_id: str
    ) -> _PBModel:
        model_metadata = self.model_dao.get_by_id(
            obj_id=model_id, request_ctx=request_ctx
        )
        if not model_metadata:
            raise TruEraNotFoundError(
                f"Provided model_id does not exist: {model_id}"
            )
        return model_metadata

    def _check_if_split_exists(
        self, request_ctx: RequestContext, split_id: str
    ) -> _PBDataSplit:
        split_metadata = self.datasplit_dao.get_by_id(
            obj_id=split_id, request_ctx=request_ctx
        )
        if not split_metadata:
            raise TruEraNotFoundError(
                f"Provided split_id does not exist: {split_id}"
            )
        return split_metadata

    def _check_if_model_and_split_in_the_same_dc(
        self,
        request_ctx: RequestContext,
        model_id: str,
        split_id: str,
        test_data_collection_id: str = None
    ):
        if split_id:
            split_metadata = self._check_if_split_exists(request_ctx, split_id)
        if model_id:
            model_metadata = self._check_if_model_exists(request_ctx, model_id)
        if split_id and model_id:
            if split_metadata.dataset_id != model_metadata.dataset_id:
                raise TruEraInvalidArgumentError(
                    f"Provided split_id and model_id are not in the same data collection! Split data collection: {split_metadata.dataset_id}, model data collection: {model_metadata.dataset_id}."
                )
        elif model_id and test_data_collection_id:
            if model_metadata.dataset_id != test_data_collection_id:
                raise TruEraInvalidArgumentError(
                    f"Test and reference model are not in the same data collection! Test data collection: {test_data_collection_id}, reference model data collection: {model_metadata.dataset_id}."
                )
        elif split_id and test_data_collection_id:
            if split_metadata.dataset_id != test_data_collection_id:
                raise TruEraInvalidArgumentError(
                    f"Test and reference split are not in the same data collection! Test data collection: {test_data_collection_id}, reference split data collection: {split_metadata.dataset_id}."
                )

    def _validate_create_generic_test_request_and_get_split_metadata(
        self, request, context: grpc.ServicerContext, caller_name: str
    ) -> Tuple[Sequence[_PBDataSplit], RequestContext]:
        project_id = request.project_id
        if not project_id:
            raise TruEraInvalidArgumentError(
                f"project_id missing in request {request}"
            )
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_updateable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name=caller_name,
            project_id=project_id
        )
        if hasattr(request, "split_id"):
            split_ids = [request.split_id]
        elif hasattr(request, "split_ids"):
            if not (request.split_ids or request.split_name_regex):
                raise TruEraInvalidArgumentError(
                    f"Please provide either `split_ids` or `split_name_regex` in request: {request}"
                )
            if not (
                request.split_ids or (
                    request.data_collection_name_regex or
                    request.data_collection_ids
                )
            ):
                raise TruEraInvalidArgumentError(
                    f"Please provide either `data_collection_name_regex` or `data_collection_ids` if `split_ids` are not explicitly given. Request: {request}"
                )
            split_ids = request.split_ids
        else:
            raise TruEraInvalidArgumentError(
                f"Split id(s) is missing in create test request; {request}"
            )
        split_metadata = []
        for split_id in split_ids:
            split = self._check_if_split_exists(request_ctx, split_id)
            if not check_if_split_not_prod_split(split):
                raise TruEraUnsupportedError(
                    'Split {} is a production split from monitoring and we cannot create tests for it.'
                    .format(split.name)
                )
            split_metadata.append(split)
        for attr_name in [
            "split_name_regex", "data_collection_name_regex",
            "protected_segment_name_regex"
        ]:
            self._validate_regex_in_request(attr_name, request)
        return split_metadata, request_ctx

    def _validate_regex_in_request(self, attr_name: str, request):
        if hasattr(request, attr_name):
            regex = getattr(request, attr_name)
            try:
                re.compile(regex)
            except re.error as e:
                raise TruEraInvalidArgumentError(
                    f"Error when compiling regex from attr `{attr_name}` in request: {e}. Request:{request}"
                )

    def _validate_split_id(
        self, request_ctx: RequestContext, split_id: str
    ) -> _PBDataSplit:
        if not split_id:
            raise TruEraInvalidArgumentError("split_id cannot be empty")
        split_metadata = self.datasplit_dao.get_by_id(
            obj_id=split_id, request_ctx=request_ctx
        )
        if not split_metadata:
            raise TruEraNotFoundError(
                f"Provided split_id does not exist: {split_id}"
            )
        return split_metadata

    def _validate_create_performance_test_request_and_get_split_metadata(
        self, request: Union[CreatePerformanceTestRequest, ModelTestGroup],
        context: grpc.ServicerContext, caller_name: str
    ) -> Tuple[Sequence[_PBDataSplit], RequestContext]:
        splits_metadata, request_ctx = self._validate_create_generic_test_request_and_get_split_metadata(
            request, context, caller_name=caller_name
        )
        if hasattr(request, "test_definition"):
            test_definition = request.test_definition
        else:
            test_definition = request.performance_test
        for split_metadata in splits_metadata:
            self._check_if_model_and_split_in_the_same_dc(
                request_ctx=request_ctx,
                model_id=test_definition.performance_metric_and_threshold.
                threshold_warning.reference_model_id,
                split_id=test_definition.performance_metric_and_threshold.
                threshold_warning.reference_split_id,
                test_data_collection_id=split_metadata.dataset_id
            )

            self._check_if_model_and_split_in_the_same_dc(
                request_ctx=request_ctx,
                model_id=test_definition.performance_metric_and_threshold.
                threshold_fail.reference_model_id,
                split_id=test_definition.performance_metric_and_threshold.
                threshold_fail.reference_split_id,
                test_data_collection_id=split_metadata.dataset_id
            )
        if not test_definition.performance_metric_and_threshold.accuracy_type:
            raise TruEraInvalidArgumentError(
                f"performance_metric_and_threshold.accuracy_type missing in request {request}"
            )
        return splits_metadata, request_ctx

    def _validate_create_stability_test_request_and_get_split_metadata(
        self, request: Union[CreateStabilityTestRequest, ModelTestGroup],
        context: grpc.ServicerContext, caller_name: str
    ) -> Tuple[Sequence[_PBDataSplit], RequestContext]:
        splits_metadata, request_ctx = self._validate_create_generic_test_request_and_get_split_metadata(
            request, context, caller_name=caller_name
        )
        if hasattr(request, "test_definition"):
            test_definition = request.test_definition
        else:
            test_definition = request.stability_test
        if not test_definition.stability_metric_and_threshold.distance_type:
            raise TruEraInvalidArgumentError(
                f"stability_metric_and_threshold.distance_type missing in request {request}"
            )
        if hasattr(request, "data_collection_id_to_base_split_id"):
            self._validate_data_collection_id_to_base_split_id_in_request(
                request_ctx, request
            )
        if test_definition.base_split_id:
            base_split_metadata = self._check_if_split_exists(
                request_ctx, test_definition.base_split_id
            )
            for comparison_split_metadata in splits_metadata:
                if base_split_metadata.dataset_id != comparison_split_metadata.dataset_id:
                    raise TruEraInvalidArgumentError(
                        f"Comparison and base data split in stability test have to be in the same data collection! Comparison split id/data collection: {comparison_split_metadata.id}/{comparison_split_metadata.dataset_id}. Base split id/data collection: {base_split_metadata.id}/{base_split_metadata.dataset_id}"
                    )

        return splits_metadata, request_ctx

    def _validate_create_fairness_test_request_and_get_split_metadata(
        self, request: Union[CreateFairnessTestRequest, ModelTestGroup],
        context: grpc.ServicerContext, caller_name: str
    ) -> Tuple[Sequence[_PBDataSplit], RequestContext]:
        splits_metadata, request_ctx = self._validate_create_generic_test_request_and_get_split_metadata(
            request, context, caller_name=caller_name
        )
        if hasattr(request, "test_definition"):
            test_definition = request.test_definition
        else:
            test_definition = request.fairness_test
            if test_definition.protected_segment_name_regex:
                if request.protected_segment_ids:
                    raise TruEraInvalidArgumentError(
                        f"Conflicts: both `protected_segment_ids` and `protected_segment_name_regex` are provided in request! {request}"
                    )
                self._validate_regex_in_request(
                    "protected_segment_name_regex", test_definition
                )

        if not test_definition.fairness_metric_and_threshold.bias_type:
            raise TruEraInvalidArgumentError(
                f"fairness_metric_and_threshold.bias_type missing in request {request}"
            )
        return splits_metadata, request_ctx

    def _validate_create_feature_importance_test_request_and_get_split_metadata(
        self, request: Union[CreateFeatureImportanceTestRequest,
                             ModelTestGroup], context: grpc.ServicerContext,
        caller_name: str
    ) -> Tuple[Sequence[_PBDataSplit], RequestContext]:
        splits_metadata, request_ctx = self._validate_create_generic_test_request_and_get_split_metadata(
            request, context, caller_name=caller_name
        )
        if hasattr(request, "test_definition"):
            test_definition = request.test_definition
        else:
            test_definition = request.feature_importance_test
        if hasattr(request, "data_collection_id_to_base_split_id"):
            self._validate_data_collection_id_to_base_split_id_in_request(
                request_ctx, request
            )
            for split_metadata in splits_metadata:
                if not request.data_collection_id_to_base_split_id.get(
                    split_metadata.dataset_id
                ):
                    raise TruEraInvalidArgumentError(
                        f"Background split definition missing for split: {split_metadata.id}. Request: {request}"
                    )
            for data_collection_id in request.data_collection_ids:
                if not request.data_collection_id_to_base_split_id.get(
                    data_collection_id
                ):
                    raise TruEraInvalidArgumentError(
                        f"Background split definition missing for data collection: {data_collection_id}. Request: {request}"
                    )

        else:
            if not test_definition.background_split_id:
                raise TruEraInvalidArgumentError(
                    f"`background_split_id` missing in request {request}"
                )
            background_split_metadata = self._check_if_split_exists(
                request_ctx, test_definition.background_split_id
            )
            for split_metadata in splits_metadata:
                if background_split_metadata.dataset_id != split_metadata.dataset_id:
                    raise TruEraInvalidArgumentError(
                        f"Background split and test split in feature importance test have to be in the same data collection! Background split id/data collection: {background_split_metadata.id}/{background_split_metadata.dataset_id}. Test split id/data collection: {split_metadata.id}/{split_metadata.dataset_id}"
                    )
        if hasattr(request, "data_collection_name_regex"):
            if request.data_collection_name_regex:
                raise TruEraInvalidArgumentError(
                    f"Cannot use `data_collection_name_regex` when creating feature importance test! Request: {request}"
                )

        if not test_definition.options_and_threshold.qoi:
            raise TruEraInvalidArgumentError(
                f"options_and_threshold.qoi missing in request {request}"
            )
        ar_client = self._get_ar_client(request_ctx)
        project_metadata = ar_client.get_project_metadata(request.project_id)
        project_score_type = fi_constants.QOI_TO_SCORE_TYPE[
            project_metadata.settings.score_type]
        test_score_type = fi_constants.QOI_TO_SCORE_TYPE[
            test_definition.options_and_threshold.qoi]
        if project_score_type in fi_constants.VALID_SCORE_TYPES_FOR_REGRESSION:
            if test_score_type and test_score_type not in fi_constants.VALID_SCORE_TYPES_FOR_REGRESSION:
                raise TruEraInvalidArgumentError(
                    f"{test_definition.options_and_threshold.qoi} is not a valid qoi for regression project"
                )
        elif project_score_type in fi_constants.VALID_SCORE_TYPES_FOR_CLASSIFICATION:
            if test_score_type and test_score_type not in fi_constants.VALID_SCORE_TYPES_FOR_CLASSIFICATION:
                raise TruEraInvalidArgumentError(
                    f"{test_definition.options_and_threshold.qoi} is not a valid qoi for classification project"
                )
        if not test_definition.options_and_threshold.threshold_warning.value.value.is_integer(
        ):
            raise TruEraInvalidArgumentError(
                f"Warning threshold needs to be whole number in request {request}"
            )
        if not test_definition.options_and_threshold.threshold_fail.value.value.is_integer(
        ):
            raise TruEraInvalidArgumentError(
                f"Fail threshold needs to be whole number in request {request}"
            )

        if test_definition.options_and_threshold.min_importance_value <= 0 or test_definition.options_and_threshold.min_importance_value >= 1:
            raise TruEraInvalidArgumentError(
                "options_and_threshold.min_importance_value needs to be between 0 and 1."
            )
        return splits_metadata, request_ctx

    def _validate_data_collection_id_to_base_split_id_in_request(
        self, request_ctx, request
    ):
        if request.data_collection_id_to_base_split_id:
            for dc_id, base_split_id in request.data_collection_id_to_base_split_id.items(
            ):
                if base_split_id:
                    base_split_metadata = self._check_if_split_exists(
                        request_ctx, base_split_id
                    )
                    if base_split_metadata.dataset_id != dc_id:
                        raise TruEraInvalidArgumentError(
                            f"Base split {base_split_id} does not belong in data collection {dc_id}! Given `data_collection_id_to_base_split_id`: {request.data_collection_id_to_base_split_id}"
                        )

    def StartBaselineModelWorkflow(
        self, request, context
    ) -> StartBaselineModelWorkflowResponse:
        workflow_id = ""
        if self.use_temporal:
            request_ctx = check_permission_helper.authenticate_and_audit_request_updateable(
                logger=self.logger,
                request_ctx_helper=self.request_ctx_helper,
                rbac_client=self.rbac_client,
                context=context,
                caller_name="CREATE_TESTS_FROM_SPLIT",
                project_id=request.project_id
            )

            async def execute_workflow():
                client = await temporalio_client.connect(
                    self.client_config['temporal']['url'],
                    namespace=self.temporal_namespace,
                    data_converter=dataclasses.replace(
                        temporalio.converter.default(),
                        payload_converter_class=BaselineModelPayloadConverter,
                    ),
                )

                return await client.start_workflow(
                    BaselineModelCreationWorkflow.run,
                    BaselineModelCreationRequest(
                        request_ctx, self.aiq_connection_string,
                        self.mrc_connection_string, self.ar_connection_string,
                        self.ds_connection_string, request.project_id,
                        request.project_name, request.data_collection_id,
                        request.data_collection_name, request.split_id,
                        request.split_name, request.output_type
                    ),
                    id=f"test_creation_workflow_{uuid.uuid4()}",
                    task_queue="model-test-creation-queue"
                )

            workflow_handle = asyncio.run(execute_workflow())
            workflow_id = workflow_handle.id
        return StartBaselineModelWorkflowResponse(workflow_id=workflow_id)

    @initialize_grpc_servicer_context
    def CreateTestsFromSplit(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_updateable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="CREATE_TESTS_FROM_SPLIT",
            project_id=project_id
        )
        split_id = request.split_id
        split_metadata = self._check_if_split_exists(request_ctx, split_id)
        if not check_if_split_not_prod_split(split_metadata):
            self.logger.error(
                "Split {} is a production split from monitoring and we cannot create tests for it."
                .format(split_metadata.name)
            )
            raise TruEraUnsupportedError(
                "Split {} is a production split from monitoring and we cannot create tests for it."
                .format(split_metadata.name)
            )

        ar_client = self._get_ar_client(request_ctx)
        model_tests = []
        if not self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE,
            name=_DEFAULT_PERFORMANCE_TEST_NAME
        ):
            model_tests.append(
                self._create_default_performance_test_for_split(
                    request_ctx, project_id, split_id, ar_client
                )
            )
        else:
            self.logger.info("Default performance test already exists.")
        aiq_client = self._get_aiq_client(request_ctx)
        if not self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_FAIRNESS,
            name=_DEFAULT_FAIRNESS_TEST_NAME
        ):
            bias_configs = self.artifact_metadata_client.get_bias_configs(
                request_ctx, project_id
            )
            for bias_config in bias_configs:
                model_tests.append(
                    self._create_default_fairness_test(
                        request_ctx, project_id, split_id,
                        bias_config.bias_type, bias_config.acceptable_min,
                        bias_config.acceptable_max
                    )
                )
        else:
            self.logger.info("Default fairness test already exists.")
        if not self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_STABILITY,
            name=_DEFAULT_STABILITY_TEST_NAME
        ):
            model_tests.append(
                self._create_default_stability_test_for_split(
                    request_ctx, project_id, split_id, ar_client
                )
            )
        else:
            self.logger.info("Default stability test already exists.")
        for model_test in model_tests:
            if model_test:
                self.modeltest_dao.add(
                    model_test=model_test,
                    insert_only=True,
                    request_ctx=request_ctx
                )
        return CreateTestsFromSplitResponse(model_tests=model_tests)

    def _create_default_performance_test_for_split(
        self, request_ctx: RequestContext, project_id: str, split_id: str,
        ar_client: ArtifactRepoClient
    ) -> _PBModelTest:
        if self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE,
            name=_DEFAULT_PERFORMANCE_TEST_NAME
        ):
            return
        model_test = _PBModelTest(
            test_name=_DEFAULT_PERFORMANCE_TEST_NAME,
            id=str(uuid.uuid4()),
            test_type=_PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE,
            project_id=project_id,
            split_name_regex=".*",
            data_collection_name_regex=".*",
            segment_id=_PBSegmentID(),
            performance_test=modeltest_pb2.PerformanceTest(),
            autorun=True,
            test_group_id=str(uuid.uuid4())
        )
        threshold_warning = _PBTestThreshold()
        threshold_warning.threshold_type = _PBTestThreshold.ThresholdType.RELATIVE_SINGLE_VALUE
        threshold_warning.value.value = 0
        test_definition = modeltest_pb2.PerformanceTest(
            performance_metric_and_threshold=modeltest_pb2.PerformanceTest.
            PerformanceMetricAndThreshold(threshold_fail=_PBTestThreshold())
        )
        project_metadata = ar_client.get_project_metadata(project_id)
        score_type = fi_constants.QOI_TO_SCORE_TYPE[
            project_metadata.settings.score_type]
        if score_type in fi_constants.VALID_SCORE_TYPES_FOR_CLASSIFICATION:
            threshold_warning.value.condition = _PBTestThreshold.ThresholdValue.WARN_OR_FAIL_IF_LESS_THAN
            test_definition.performance_metric_and_threshold.accuracy_type = _PBAccuracyType.Type.Value(
                DEFAULT_PERFORMANCE_TEST_METRICS["classification"]
            )
        elif score_type in fi_constants.VALID_SCORE_TYPES_FOR_REGRESSION:
            threshold_warning.value.condition = _PBTestThreshold.ThresholdValue.WARN_OR_FAIL_IF_GREATER_THAN
            test_definition.performance_metric_and_threshold.accuracy_type = _PBAccuracyType.Type.Value(
                DEFAULT_PERFORMANCE_TEST_METRICS["regression"]
            )
        elif score_type in fi_constants.VALID_SCORE_TYPES_FOR_RANKING:
            threshold_warning.value.condition = _PBTestThreshold.ThresholdValue.WARN_OR_FAIL_IF_LESS_THAN
            test_definition.performance_metric_and_threshold.accuracy_type = _PBAccuracyType.Type.Value(
                DEFAULT_PERFORMANCE_TEST_METRICS["ranking"]
            )
        else:
            raise TruEraInternalError(f"Unexpected score type: {score_type}.")
        test_definition.performance_metric_and_threshold.threshold_warning.CopyFrom(
            threshold_warning
        )
        model_test.performance_test.CopyFrom(test_definition)
        return model_test

    def _create_default_stability_test_for_split(
        self, request_ctx: RequestContext, project_id: str, split_id: str,
        ar_client: ArtifactRepoClient
    ) -> _PBModelTest:
        if self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_STABILITY,
            name=_DEFAULT_STABILITY_TEST_NAME
        ):
            return
        model_test = _PBModelTest(
            test_name=_DEFAULT_STABILITY_TEST_NAME,
            id=str(uuid.uuid4()),
            project_id=project_id,
            data_collection_name_regex=".*",
            split_name_regex=".*",
            segment_id=_PBSegmentID(),
            test_type=_PBModelTestType.MODEL_TEST_TYPE_STABILITY,
            autorun=True,
            test_group_id=str(uuid.uuid4())
        )
        model_test.stability_test.stability_metric_and_threshold.CopyFrom(
            modeltest_pb2.StabilityTest.StabilityMetricAndThreshold(
                distance_type=_PBDistanceType.NUMERICAL_WASSERSTEIN,
                threshold_warning=_PBTestThreshold(),
                threshold_fail=_PBTestThreshold()
            )
        )
        return model_test

    def _create_default_fairness_test(
        self, request_ctx: RequestContext, project_id: str, split_id: str,
        bias_type: _PBBiasType.Type, bias_metric_lower_bound: float,
        bias_metric_upper_bound: float
    ) -> _PBModelTest:
        if self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_FAIRNESS,
            name=_DEFAULT_FAIRNESS_TEST_NAME
        ):
            return
        model_test = _PBModelTest(
            test_name=_DEFAULT_FAIRNESS_TEST_NAME,
            id=str(uuid.uuid4()),
            project_id=project_id,
            data_collection_name_regex=".*",
            split_name_regex=".*",
            segment_id=_PBSegmentID(),
            test_type=_PBModelTestType.MODEL_TEST_TYPE_FAIRNESS,
            fairness_test=modeltest_pb2.FairnessTest(),
            autorun=True,
            test_group_id=str(uuid.uuid4())
        )
        threshold_warning = _PBTestThreshold()
        threshold_warning.threshold_type = _PBTestThreshold.ThresholdType.ABSOLUTE_VALUE_RANGE
        threshold_warning.value_range.lower_bound = bias_metric_lower_bound
        threshold_warning.value_range.upper_bound = bias_metric_upper_bound
        threshold_warning.value_range.condition = _PBTestThreshold.ThresholdValueRange.ThresholdCondition.WARN_OR_FAIL_IF_OUTSIDE
        test_definition = modeltest_pb2.FairnessTest(
            protected_segment_name_regex=".*",
            fairness_metric_and_threshold=modeltest_pb2.FairnessTest.
            FairnessMetricAndThreshold(
                threshold_warning=threshold_warning,
                threshold_fail=_PBTestThreshold()
            ),
        )
        test_definition.fairness_metric_and_threshold.bias_type = bias_type
        model_test.fairness_test.CopyFrom(test_definition)
        return model_test

    @cached(
        cache=TTLCache(maxsize=128, ttl=30), key=performance_metric_cache_key
    )
    def _get_performance(
        self,
        request_ctx: RequestContext,
        project_id: str,
        model_id: str,
        data_split_id: str,
        metric_type: str,
        segment_id_proto: _PBSegmentID,
    ) -> AiqClientResponse:
        aiq_client = self._get_aiq_client(request_ctx)
        segment = None
        if segment_id_proto.segmentation_id:
            segment_proto = self._get_segment_proto(
                request_ctx, segment_id_proto.segmentation_id,
                segment_id_proto.segment_name
            )
            segment = Segment(segment_proto.name, project_id, segment_proto)
        return aiq_client.compute_performance(
            project_id=project_id,
            model_id=model_id,
            data_split_id=data_split_id,
            metric_types=[metric_type],
            segment=segment,
            wait=False,
            as_proto=True
        )

    @cached(
        cache=TTLCache(maxsize=128, ttl=30), key=feature_importance_cache_key
    )
    def _get_feature_importances(
        self, request_ctx: RequestContext, project_id: str, model_id: str,
        data_split_id: str, score_type: str, segment_id_proto: _PBSegmentID,
        background_split_id: str
    ) -> AiqClientResponse:
        aiq_client = self._get_aiq_client(request_ctx)
        segment = None
        if segment_id_proto.segmentation_id:
            segment_proto = self._get_segment_proto(
                request_ctx, segment_id_proto.segmentation_id,
                segment_id_proto.segment_name
            )
            segment = Segment(segment_proto.name, project_id, segment_proto)
        return aiq_client.get_global_feature_importances(
            project_id=project_id,
            model_id=model_id,
            data_split_id=data_split_id,
            score_type=score_type,
            segment=segment,
            background_split_id=background_split_id,
            wait=False
        )

    def CreatePerformanceTest(
        self, request: CreatePerformanceTestRequest,
        context: grpc.ServicerContext
    ) -> CreatePerformanceTestResponse:
        splits_metadata, request_ctx = self._validate_create_performance_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_PERFORMANCE_TEST"
        )
        split_metadata = splits_metadata[0]
        test_group_id = None
        model_test_id = str(uuid.uuid4())
        if request.overwrite:
            search_params = {
                "project_id":
                    request.project_id,
                "test_type":
                    _PBModelTestType.Name(
                        _PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE
                    ),
                "split_id":
                    request.split_id,
                "segment_id.segmentation_id":
                    request.segment_id.segmentation_id or "",
                "segment_id.segment_name":
                    request.segment_id.segment_name or "",
                "performance_test.performance_metric_and_threshold.accuracy_type":
                    _PBAccuracyType.Type.Name(
                        request.test_definition.
                        performance_metric_and_threshold.accuracy_type
                    )
            }
            model_tests = self.modeltest_dao.get_all(
                request_ctx=request_ctx, params=search_params, as_proto=True
            )
            if len(model_tests) > 1:
                raise TruEraInternalError(
                    f"Unexpected state: found more than one tests that match the overwrite request: {model_tests}. Request aborted."
                )
            if len(model_tests) > 0:
                model_test_id = model_tests[0].id
                test_group_id = model_tests[0].test_group_id
        self._validate_name_and_description_in_request(
            request, context, test_group_id=test_group_id
        )
        if not test_group_id:
            test_group_id = str(
                uuid.uuid4()
            )  # a test needs to belong to a group
        model_test = _PBModelTest(
            id=model_test_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE,
            project_id=request.project_id,
            data_collection_id=split_metadata.dataset_id,
            split_id=request.split_id,
            segment_id=request.segment_id,
            performance_test=request.test_definition,
            test_name=request.test_name,
            description=request.description,
            autorun=request.autorun,
            test_group_id=test_group_id
        )

        self.modeltest_dao.add(
            model_test=model_test,
            insert_only=not request.overwrite,
            request_ctx=request_ctx
        )
        return CreatePerformanceTestResponse(
            test_id=model_test.id, test_group_id=model_test.test_group_id
        )

    def CreatePerformanceTestGroup(
        self, request: CreatePerformanceTestGroupRequest,
        context: grpc.ServicerContext
    ) -> CreatePerformanceTestGroupResponse:
        request = request.model_test_group
        request_ctx = self._validate_name_and_description_in_request(
            request,
            context,
            test_group_id=request.test_group_id,
            test_name_required=True
        )
        model_tests_to_delete = []
        if request.test_group_id:
            model_tests_to_delete = self._get_model_tests_by_group_id(
                request_ctx=request_ctx,
                project_id=request.project_id,
                test_group_id=request.test_group_id,
                test_type=_PBModelTestType.Name(
                    _PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE
                )
            )
            test_group_id = request.test_group_id
        else:
            test_group_id = str(uuid.uuid4())

        splits_metadata, request_ctx = self._validate_create_performance_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_PERFORMANCE_TEST_GROUP"
        )
        test_ids = []
        if request.split_ids:
            for split_metadata in splits_metadata:
                segment_ids = request.segment_ids or [_PBSegmentID()]
                for segment_id in segment_ids:
                    model_test_id = str(uuid.uuid4())
                    model_test = _PBModelTest(
                        id=model_test_id,
                        test_type=_PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE,
                        project_id=request.project_id,
                        data_collection_id=split_metadata.dataset_id,
                        split_id=split_metadata.id,
                        segment_id=segment_id,
                        performance_test=request.performance_test,
                        test_name=request.test_name,
                        description=request.description,
                        autorun=True,
                        test_group_id=test_group_id
                    )
                    self.modeltest_dao.add(
                        model_test=model_test,
                        insert_only=True,
                        request_ctx=request_ctx
                    )
                    test_ids.append(model_test_id)
        else:
            test_templates = []
            segment_ids = request.segment_ids or [_PBSegmentID()]
            for segment_id in segment_ids:
                test_template = _PBModelTest(
                    test_type=_PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE,
                    project_id=request.project_id,
                    split_name_regex=request.split_name_regex,
                    segment_id=segment_id,
                    performance_test=request.performance_test,
                    test_name=request.test_name,
                    description=request.description,
                    autorun=True,
                    test_group_id=test_group_id
                )
                test_templates.append(test_template)
            test_ids = self._create_tests_from_templates(
                request_ctx, test_templates, request
            )

        for test_to_delete in model_tests_to_delete:
            self.modeltest_dao.delete(
                obj_id=test_to_delete.id, request_ctx=request_ctx
            )

        return CreatePerformanceTestGroupResponse(
            test_group_id=test_group_id, test_ids=test_ids
        )

    def CreateStabilityTest(
        self, request: CreateStabilityTestRequest, context: grpc.ServicerContext
    ) -> CreateStabilityTestResponse:
        splits_metadata, request_ctx = self._validate_create_stability_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_STABILITY_TEST"
        )
        split_metadata = splits_metadata[0]
        test_group_id = None
        model_test_id = str(uuid.uuid4())
        if request.overwrite:
            search_params = {
                "project_id":
                    request.project_id,
                "test_type":
                    _PBModelTestType.Name(
                        _PBModelTestType.MODEL_TEST_TYPE_STABILITY
                    ),
                "split_id":
                    request.split_id,
                "segment_id.segmentation_id":
                    request.segment_id.segmentation_id or "",
                "segment_id.segment_name":
                    request.segment_id.segment_name or "",
                "stability_test.base_split_id":
                    request.test_definition.base_split_id,
                "stability_test.stability_metric_and_threshold.distance_type":
                    _PBDistanceType.Name(
                        request.test_definition.stability_metric_and_threshold.
                        distance_type
                    )
            }
            model_tests = self.modeltest_dao.get_all(
                request_ctx=request_ctx, params=search_params, as_proto=True
            )
            if len(model_tests) > 1:
                raise TruEraInternalError(
                    f"Unexpected state: found more than one tests that match the overwrite request: {model_tests}. Request aborted."
                )
            if len(model_tests) > 0:
                model_test_id = model_tests[0].id
                test_group_id = model_tests[0].test_group_id
        self._validate_name_and_description_in_request(
            request, context, test_group_id=test_group_id
        )
        if not test_group_id:
            test_group_id = str(
                uuid.uuid4()
            )  # a test needs to belong to a group

        model_test = _PBModelTest(
            id=model_test_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_STABILITY,
            project_id=request.project_id,
            data_collection_id=split_metadata.dataset_id,
            split_id=request.split_id,
            segment_id=request.segment_id,
            stability_test=request.test_definition,
            test_name=request.test_name,
            description=request.description,
            autorun=request.autorun,
            test_group_id=test_group_id
        )
        self.modeltest_dao.add(
            model_test=model_test,
            insert_only=not request.overwrite,
            request_ctx=request_ctx
        )
        return CreateStabilityTestResponse(
            test_id=model_test_id, test_group_id=test_group_id
        )

    def CreateStabilityTestGroup(
        self, request: CreateStabilityTestGroupRequest,
        context: grpc.ServicerContext
    ) -> CreateStabilityTestGroupResponse:
        request = request.model_test_group
        request_ctx = self._validate_name_and_description_in_request(
            request,
            context,
            test_group_id=request.test_group_id,
            test_name_required=True
        )
        model_tests_to_delete = []
        if request.test_group_id:
            model_tests_to_delete = self._get_model_tests_by_group_id(
                request_ctx=request_ctx,
                project_id=request.project_id,
                test_group_id=request.test_group_id,
                test_type=_PBModelTestType.Name(
                    _PBModelTestType.MODEL_TEST_TYPE_STABILITY
                )
            )
            test_group_id = request.test_group_id
        else:
            test_group_id = str(uuid.uuid4())

        splits_metadata, request_ctx = self._validate_create_stability_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_STABILITY_TEST_GROUP"
        )
        test_ids = []
        if request.split_ids:
            for split_metadata in splits_metadata:
                segment_ids = request.segment_ids or [_PBSegmentID()]
                for segment_id in segment_ids:
                    model_test_id = str(uuid.uuid4())
                    test_definition = _PBStabilityTest()
                    test_definition.CopyFrom(request.stability_test)
                    base_split_id = request.data_collection_id_to_base_split_id.get(
                        split_metadata.dataset_id
                    )
                    if base_split_id:
                        test_definition.base_split_id = base_split_id
                    model_test = _PBModelTest(
                        id=model_test_id,
                        test_type=_PBModelTestType.MODEL_TEST_TYPE_STABILITY,
                        project_id=request.project_id,
                        data_collection_id=split_metadata.dataset_id,
                        split_id=split_metadata.id,
                        segment_id=segment_id,
                        stability_test=test_definition,
                        test_name=request.test_name,
                        description=request.description,
                        autorun=True,
                        test_group_id=test_group_id
                    )
                    self.modeltest_dao.add(
                        model_test=model_test,
                        insert_only=True,
                        request_ctx=request_ctx
                    )
                    test_ids.append(model_test_id)
        else:
            test_templates = []
            segment_ids = request.segment_ids or [_PBSegmentID()]
            for segment_id in segment_ids:
                test_template = _PBModelTest(
                    test_type=_PBModelTestType.MODEL_TEST_TYPE_STABILITY,
                    project_id=request.project_id,
                    split_name_regex=request.split_name_regex,
                    segment_id=segment_id,
                    stability_test=request.stability_test,
                    test_name=request.test_name,
                    description=request.description,
                    autorun=True,
                    test_group_id=test_group_id
                )
                test_templates.append(test_template)
            test_ids = self._create_tests_from_templates(
                request_ctx, test_templates, request
            )

        for test_to_delete in model_tests_to_delete:
            self.modeltest_dao.delete(
                obj_id=test_to_delete.id, request_ctx=request_ctx
            )

        return CreateStabilityTestGroupResponse(
            test_group_id=test_group_id, test_ids=test_ids
        )

    def CreateFairnessTest(
        self, request: modeltest_service_pb2.CreateFairnessTestRequest,
        context: grpc.ServicerContext
    ) -> CreateFairnessTestResponse:
        splits_metadata, request_ctx = self._validate_create_fairness_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_FAIRNESS_TEST"
        )
        split_metadata = splits_metadata[0]
        test_group_id = None
        model_test_id = str(uuid.uuid4())
        if request.overwrite:
            search_params = {
                "project_id":
                    request.project_id,
                "test_type":
                    _PBModelTestType.Name(
                        _PBModelTestType.MODEL_TEST_TYPE_FAIRNESS
                    ),
                "split_id":
                    request.split_id,
                "segment_id.segmentation_id":
                    request.segment_id.segmentation_id or "",
                "segment_id.segment_name":
                    request.segment_id.segment_name or "",
                "fairness_test.fairness_metric_and_threshold.bias_type":
                    _PBBiasType.Type.Name(
                        request.test_definition.fairness_metric_and_threshold.
                        bias_type
                    ),
                "fairness_test.segment_id_protected.segmentation_id":
                    request.test_definition.segment_id_protected.segmentation_id
                    or "",
                "fairness_test.segment_id_protected.segment_name":
                    request.test_definition.segment_id_protected.segment_name
                    or "",
                "fairness_test.segment_id_comparison.segmentation_id":
                    request.test_definition.segment_id_comparison.
                    segmentation_id or "",
                "fairness_test.segment_id_comparison.segment_name":
                    request.test_definition.segment_id_comparison.segment_name
                    or "",
            }
            model_tests = self.modeltest_dao.get_all(
                request_ctx=request_ctx, params=search_params, as_proto=True
            )
            if len(model_tests) > 1:
                raise TruEraInternalError(
                    f"Unexpected state: found more than one tests that match the overwrite request: {model_tests}. Request aborted."
                )
            if len(model_tests) > 0:
                model_test_id = model_tests[0].id
                test_group_id = model_tests[0].test_group_id
        self._validate_name_and_description_in_request(
            request, context, test_group_id=test_group_id
        )
        if not test_group_id:
            test_group_id = str(
                uuid.uuid4()
            )  # a test needs to belong to a group

        model_test = _PBModelTest(
            id=model_test_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_FAIRNESS,
            project_id=request.project_id,
            data_collection_id=split_metadata.dataset_id,
            split_id=request.split_id,
            segment_id=request.segment_id,
            fairness_test=request.test_definition,
            test_name=request.test_name,
            description=request.description,
            autorun=request.autorun,
            test_group_id=test_group_id
        )
        self.modeltest_dao.add(
            model_test=model_test,
            insert_only=not request.overwrite,
            request_ctx=request_ctx
        )
        return CreateFairnessTestResponse(
            test_id=model_test_id, test_group_id=test_group_id
        )

    def CreateFairnessTestGroup(
        self, request: CreateFairnessTestGroupRequest,
        context: grpc.ServicerContext
    ) -> CreateFairnessTestResponse:
        request = request.model_test_group
        request_ctx = self._validate_name_and_description_in_request(
            request,
            context,
            test_group_id=request.test_group_id,
            test_name_required=True
        )
        model_tests_to_delete = []
        if request.test_group_id:
            model_tests_to_delete = self._get_model_tests_by_group_id(
                request_ctx=request_ctx,
                project_id=request.project_id,
                test_group_id=request.test_group_id,
                test_type=_PBModelTestType.Name(
                    _PBModelTestType.MODEL_TEST_TYPE_FAIRNESS
                )
            )
            test_group_id = request.test_group_id
        else:
            test_group_id = str(uuid.uuid4())

        splits_metadata, request_ctx = self._validate_create_fairness_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_FAIRNESS_TEST_GROUP"
        )
        if not (
            request.protected_segment_ids or
            request.fairness_test.protected_segment_name_regex
        ):
            raise TruEraInvalidArgumentError(
                f"Need to provide protected segment to create fairness test! {request}"
            )
        if len(request.protected_segment_ids
              ) != len(request.comparison_segment_ids):
            if len(request.comparison_segment_ids) == 0:
                request.comparison_segment_ids.extend(
                    [
                        _PBSegmentID(segmentation_id=i.segmentation_id)
                        for i in request.protected_segment_ids
                    ]
                )
            else:
                raise TruEraInvalidArgumentError(
                    f"Number of protected segments and comparison segments need to be the same when definition fairness test group!  {request}"
                )
        test_definitions = []
        if request.fairness_test.protected_segment_name_regex:
            test_definitions.append(request.fairness_test)
        else:
            for i, _ in enumerate(request.protected_segment_ids):
                test_definition = modeltest_pb2.FairnessTest()
                test_definition.CopyFrom(request.fairness_test)
                test_definition.segment_id_protected.CopyFrom(
                    request.protected_segment_ids[i]
                )
                test_definition.segment_id_comparison.CopyFrom(
                    request.comparison_segment_ids[i]
                )
                test_definitions.append(test_definition)
        test_ids = []
        if request.split_ids:
            for split_metadata in splits_metadata:
                for test_definition in test_definitions:
                    model_test_id = str(uuid.uuid4())
                    model_test = _PBModelTest(
                        id=model_test_id,
                        test_type=_PBModelTestType.MODEL_TEST_TYPE_FAIRNESS,
                        project_id=request.project_id,
                        data_collection_id=split_metadata.dataset_id,
                        split_id=split_metadata.id,
                        segment_id=_PBSegmentID(),
                        fairness_test=test_definition,
                        test_name=request.test_name,
                        description=request.description,
                        autorun=True,
                        test_group_id=test_group_id
                    )
                    self.modeltest_dao.add(
                        model_test=model_test,
                        insert_only=True,
                        request_ctx=request_ctx
                    )
                    test_ids.append(model_test_id)
        else:
            test_templates = []
            for test_definition in test_definitions:
                test_template = _PBModelTest(
                    test_type=_PBModelTestType.MODEL_TEST_TYPE_FAIRNESS,
                    project_id=request.project_id,
                    split_name_regex=request.split_name_regex,
                    segment_id=_PBSegmentID(),
                    fairness_test=test_definition,
                    test_name=request.test_name,
                    description=request.description,
                    autorun=True,
                    test_group_id=test_group_id
                )
                test_templates.append(test_template)
            test_ids = self._create_tests_from_templates(
                request_ctx, test_templates, request
            )

        for test_to_delete in model_tests_to_delete:
            self.modeltest_dao.delete(
                obj_id=test_to_delete.id, request_ctx=request_ctx
            )
        return CreateFairnessTestGroupResponse(
            test_group_id=test_group_id, test_ids=test_ids
        )

    def CreateFeatureImportanceTest(
        self, request: CreateFeatureImportanceTestRequest,
        context: grpc.ServicerContext
    ) -> CreateFeatureImportanceTestResponse:
        splits_metadata, request_ctx = self._validate_create_feature_importance_test_request_and_get_split_metadata(
            request, context, caller_name="CREATE_FEATURE_IMPORTANCE_TEST"
        )
        split_metadata = splits_metadata[0]
        test_group_id = None
        model_test_id = str(uuid.uuid4())
        if request.overwrite:
            search_params = {
                "project_id":
                    request.project_id,
                "test_type":
                    _PBModelTestType.Name(
                        _PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE
                    ),
                "split_id":
                    request.split_id,
                "segment_id.segmentation_id":
                    request.segment_id.segmentation_id or "",
                "segment_id.segment_name":
                    request.segment_id.segment_name or ""
            }
            model_tests = self.modeltest_dao.get_all(
                request_ctx=request_ctx, params=search_params, as_proto=True
            )
            if len(model_tests) > 1:
                raise TruEraInternalError(
                    f"Unexpected state: found more than one tests that match the overwrite request: {model_tests}. Request aborted."
                )
            if len(model_tests) > 0:
                model_test_id = model_tests[0].id
                test_group_id = model_tests[0].test_group_id
        self._validate_name_and_description_in_request(
            request, context, test_group_id=test_group_id
        )
        if not test_group_id:
            test_group_id = str(
                uuid.uuid4()
            )  # a test needs to belong to a group

        model_test = _PBModelTest(
            id=model_test_id,
            test_type=_PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE,
            project_id=request.project_id,
            data_collection_id=split_metadata.dataset_id,
            split_id=request.split_id,
            segment_id=request.segment_id,
            feature_importance_test=request.test_definition,
            test_name=request.test_name,
            description=request.description,
            autorun=request.autorun,
            test_group_id=test_group_id
        )
        self.modeltest_dao.add(
            model_test=model_test,
            insert_only=not request.overwrite,
            request_ctx=request_ctx
        )
        return CreateFeatureImportanceTestResponse(
            test_id=model_test_id, test_group_id=test_group_id
        )

    def CreateFeatureImportanceTestGroup(
        self, request: CreateFeatureImportanceTestGroupRequest,
        context: grpc.ServicerContext
    ) -> CreateFeatureImportanceTestGroupResponse:
        request = request.model_test_group
        request_ctx = self._validate_name_and_description_in_request(
            request,
            context,
            test_group_id=request.test_group_id,
            test_name_required=True
        )
        model_tests_to_delete = []
        if request.test_group_id:
            model_tests_to_delete = self._get_model_tests_by_group_id(
                request_ctx=request_ctx,
                project_id=request.project_id,
                test_group_id=request.test_group_id,
                test_type=_PBModelTestType.Name(
                    _PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE
                )
            )
            test_group_id = request.test_group_id
        else:
            test_group_id = str(uuid.uuid4())

        splits_metadata, request_ctx = self._validate_create_feature_importance_test_request_and_get_split_metadata(
            request,
            context,
            caller_name="CREATE_FEATURE_IMPORTANCE_TEST_GROUP"
        )
        test_ids = []
        if request.split_ids:
            for split_metadata in splits_metadata:
                segment_ids = request.segment_ids or [_PBSegmentID()]
                for segment_id in segment_ids:
                    model_test_id = str(uuid.uuid4())
                    test_definition = _PBFeatureImportanceTest()
                    test_definition.CopyFrom(request.feature_importance_test)
                    background_split_id = request.data_collection_id_to_base_split_id.get(
                        split_metadata.dataset_id
                    )
                    if background_split_id:
                        test_definition.background_split_id = background_split_id
                    model_test = _PBModelTest(
                        id=model_test_id,
                        test_type=_PBModelTestType.
                        MODEL_TEST_TYPE_FEATURE_IMPORTANCE,
                        project_id=request.project_id,
                        data_collection_id=split_metadata.dataset_id,
                        split_id=split_metadata.id,
                        segment_id=segment_id,
                        feature_importance_test=test_definition,
                        test_name=request.test_name,
                        description=request.description,
                        autorun=True,
                        test_group_id=test_group_id
                    )
                    self.modeltest_dao.add(
                        model_test=model_test,
                        insert_only=True,
                        request_ctx=request_ctx
                    )
                    test_ids.append(model_test_id)
        else:
            test_templates = []
            segment_ids = request.segment_ids or [_PBSegmentID()]
            for segment_id in segment_ids:
                test_template = _PBModelTest(
                    test_type=_PBModelTestType.
                    MODEL_TEST_TYPE_FEATURE_IMPORTANCE,
                    project_id=request.project_id,
                    split_name_regex=request.split_name_regex,
                    segment_id=segment_id,
                    feature_importance_test=request.feature_importance_test,
                    test_name=request.test_name,
                    description=request.description,
                    autorun=True,
                    test_group_id=test_group_id
                )
                test_templates.append(test_template)
            test_ids = self._create_tests_from_templates(
                request_ctx, test_templates, request
            )
        for test_to_delete in model_tests_to_delete:
            self.modeltest_dao.delete(
                obj_id=test_to_delete.id, request_ctx=request_ctx
            )
        return CreateFeatureImportanceTestGroupResponse(
            test_group_id=test_group_id, test_ids=test_ids
        )

    @initialize_grpc_servicer_context
    def DeleteModelTest(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_updateable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="DELETE_MODEL_TEST",
            project_id=project_id
        )
        if not request.test_id:
            raise TruEraInvalidArgumentError(
                f"test_id missing in request {request}"
            )
        tests_to_delete = self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_id=request.test_id
        )
        if len(tests_to_delete) == 0:
            raise TruEraNotFoundError(
                f"Provided test_id does not exist: {request.test_id}"
            )
        elif len(tests_to_delete) > 1:
            raise TruEraInternalError(
                f"Unexpected state: found more than one tests that match the delete request: {tests_to_delete}. Canceling request."
            )
        self.modeltest_dao.delete(
            obj_id=tests_to_delete[0].id, request_ctx=request_ctx
        )
        resp = modeltest_service_pb2.DeleteModelTestResponse()
        resp.deleted_test.CopyFrom(tests_to_delete[0])
        return resp

    @initialize_grpc_servicer_context
    def DeleteModelTestGroup(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_updateable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="DELETE_MODEL_TEST_GROUP",
            project_id=project_id
        )
        if not request.test_group_id:
            raise TruEraInvalidArgumentError(
                f"test_group_id missing in request {request}"
            )
        tests_to_delete = self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_group_id=request.test_group_id
        )
        if len(tests_to_delete) == 0:
            raise TruEraNotFoundError(
                f"Provided test_group_id does not exist: {request.test_group_id}"
            )
        deleted_test_ids = []
        for model_test in tests_to_delete:
            self.modeltest_dao.delete(
                obj_id=model_test.id, request_ctx=request_ctx
            )
            deleted_test_ids.append(model_test.id)
        resp = modeltest_service_pb2.DeleteModelTestGroupResponse(
            deleted_test_ids=deleted_test_ids
        )
        return resp

    @initialize_grpc_servicer_context
    def DeleteModelTestsForSplit(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_updateable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="DELETE_MODEL_TESTS_FOR_SPLIT",
            project_id=project_id
        )
        self._check_if_split_exists(request_ctx, request.split_id)
        tests_to_delete = self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            split_id=request.split_id
        )
        for model_test in tests_to_delete:
            self.modeltest_dao.delete(
                obj_id=model_test.id, request_ctx=request_ctx
            )
        resp = modeltest_service_pb2.DeleteModelTestsForSplitResponse()
        resp.deleted_tests.extend(tests_to_delete)
        return resp

    @initialize_grpc_servicer_context
    def GetModelTests(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_viewable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="GET_MODEL_TESTS",
            project_id=project_id
        )
        model_tests = self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=request.test_type,
            data_collection_id=request.data_collection_id,
            split_id=request.split_id,
            test_id=request.test_id,
            name=request.test_name
        )
        resp = GetModelTestsResponse()
        resp.model_tests.extend(model_tests)
        return resp

    def get_model_tests(
        self,
        request_ctx: RequestContext,
        project_id: str,
        test_type: Optional[_PBModelTestType] = None,
        data_collection_id: Optional[str] = None,
        split_id: Optional[str] = None,
        segmentation_id: Optional[str] = None,
        segment_name: Optional[str] = None,
        test_id: Optional[str] = None,
        test_group_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> Sequence[_PBModelTest]:
        data_collection_name = None
        split_name = None
        query = f"project_id='{project_id}'"
        if test_type:
            # pylint: disable=protobuf-enum-value
            test_type_str = _PBModelTestType.Name(test_type)
            query += f" AND test_type='{test_type_str}'"
        if data_collection_id:
            query += f" AND (data_collection_id='{data_collection_id}' OR data_collection_id=null)"
            dc = self.dataset_dao.get_by_id(
                obj_id=data_collection_id,
                request_ctx=request_ctx,
                exists=False
            )
            data_collection_name = dc.name if dc else None
        if split_id:
            query += f" AND (split_id='{split_id}' OR split_id=null)"
            split = self.datasplit_dao.get_by_id(
                obj_id=split_id, request_ctx=request_ctx, exists=False
            )
            split_name = split.name if split else None
            if split:
                if not check_if_split_not_prod_split(split):
                    raise TruEraUnsupportedError(
                        "Split {} is a production split from monitoring and we cannot get model tests from it."
                        .format(split.name)
                    )
                dc = self.dataset_dao.get_by_id(
                    obj_id=split.dataset_id,
                    request_ctx=request_ctx,
                    exists=False
                )
                data_collection_name = dc.name if dc else None
        if test_id:
            query += f" AND id='{test_id}'"
        if segmentation_id is not None:  # to allow for searching empty str
            query += f" AND segment_id.segmentation_id='{segmentation_id}'"
        if segment_name is not None:  # to allow for searching empty str
            query += f" AND segment_id.segment_name='{segment_name}'"
        if test_group_id:
            query += f" AND test_group_id='{test_group_id}'"
        if name:
            query += f" AND test_name='{name}'"

        result = self.modeltest_dao.search(
            request_ctx=request_ctx, query=query, as_proto=True
        )
        filtered_result = []
        for model_test in result:
            dc_filter_matched = True
            if data_collection_name:
                if model_test.data_collection_name_regex:
                    if not re.match(
                        model_test.data_collection_name_regex,
                        data_collection_name
                    ):
                        dc_filter_matched = False

            split_filter_matched = True
            if split_name:
                if model_test.split_name_regex:
                    if not re.match(model_test.split_name_regex, split_name):
                        split_filter_matched = False
            if dc_filter_matched and split_filter_matched:
                filtered_result.append(model_test)
        return filtered_result

    @initialize_grpc_servicer_context
    def GetModelTestGroups(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_viewable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="GET_MODEL_TEST_GROUPS",
            project_id=project_id
        )
        model_tests = self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=request.test_type,
            data_collection_id=request.data_collection_id,
            split_id=request.split_id,
            test_group_id=request.test_group_id,
            name=request.test_name
        )

        def get_segment_key(segment_id: _PBSegmentID):
            return f"{segment_id.segmentation_id}-{segment_id.segment_name}"

        unique_test_group_ids = set(
            [model_test.test_group_id for model_test in model_tests]
        )
        model_test_groups = []
        for test_group_id in unique_test_group_ids:
            model_tests_in_group = self.get_model_tests(
                request_ctx=request_ctx,
                project_id=project_id,
                test_group_id=test_group_id
            )
            split_ids = []
            split_name_regex = None
            data_collection_ids = []
            data_collection_name_regex = None
            segment_ids = {}
            protected_segment_name_regex = None
            protected_segment_ids = {}
            comparison_segment_ids = {}
            data_collection_id_to_base_split_id = {}
            for model_test in model_tests_in_group:
                if model_test.split_id:
                    split_ids.append(model_test.split_id)
                elif model_test.split_name_regex:
                    split_name_regex = model_test.split_name_regex
                    if model_test.data_collection_id:
                        data_collection_ids.append(
                            model_test.data_collection_id
                        )
                    elif model_test.data_collection_name_regex:
                        data_collection_name_regex = model_test.data_collection_name_regex

                if model_test.segment_id.segment_name:
                    segment_ids[get_segment_key(model_test.segment_id)
                               ] = model_test.segment_id
                if model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FAIRNESS:
                    if model_test.fairness_test.segment_id_protected.segment_name:
                        protected_segment_ids[get_segment_key(
                            model_test.fairness_test.segment_id_protected
                        )] = model_test.fairness_test.segment_id_protected
                    elif model_test.fairness_test.protected_segment_name_regex:
                        protected_segment_name_regex = model_test.fairness_test.protected_segment_name_regex
                    if model_test.fairness_test.segment_id_comparison.segment_name:
                        comparison_segment_ids[get_segment_key(
                            model_test.fairness_test.segment_id_protected
                        )] = model_test.fairness_test.segment_id_comparison
                elif model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_STABILITY:
                    if model_test.data_collection_id:
                        data_collection_id_to_base_split_id[
                            model_test.data_collection_id
                        ] = model_test.stability_test.base_split_id
                elif model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE:
                    if model_test.data_collection_id:
                        data_collection_id_to_base_split_id[
                            model_test.data_collection_id
                        ] = model_test.feature_importance_test.background_split_id

            if len(model_tests_in_group) == 0:
                continue
            split_ids = sorted(list(set(split_ids)))
            data_collection_ids = sorted(list(set(data_collection_ids)))
            segment_ids = sorted(
                list(segment_ids.values()),
                key=lambda i: f"{i.segmentation_id}-{i.segment_name}"
            )
            protected_segment_ids = sorted(
                list(protected_segment_ids.values()),
                key=lambda i: f"{i.segmentation_id}-{i.segment_name}"
            )
            comparison_segment_ids = sorted(
                list(comparison_segment_ids.values()),
                key=lambda i: f"{i.segmentation_id}-{i.segment_name}"
            )
            model_test_group = ModelTestGroup(
                project_id=model_test.project_id,
                split_ids=split_ids,
                split_name_regex=split_name_regex,
                data_collection_ids=data_collection_ids,
                data_collection_name_regex=data_collection_name_regex,
                data_collection_id_to_base_split_id=
                data_collection_id_to_base_split_id,
                test_group_id=model_test.test_group_id,
                test_name=model_test.test_name,
                description=model_test.description,
                segment_ids=segment_ids,
                protected_segment_ids=protected_segment_ids,
                comparison_segment_ids=comparison_segment_ids,
            )
            if model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE:
                model_test_group.performance_test.CopyFrom(
                    model_test.performance_test
                )
            elif model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_STABILITY:
                stability_test = _PBStabilityTest(
                    stability_metric_and_threshold=model_test.stability_test.
                    stability_metric_and_threshold
                )
                model_test_group.stability_test.CopyFrom(stability_test)
            elif model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FAIRNESS:
                fairness_test = _PBFairnessTest(
                    protected_segment_name_regex=protected_segment_name_regex,
                    fairness_metric_and_threshold=model_test.fairness_test.
                    fairness_metric_and_threshold
                )
                model_test_group.fairness_test.CopyFrom(fairness_test)
            elif model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE:
                feature_importance_test = _PBFeatureImportanceTest(
                    options_and_threshold=model_test.feature_importance_test.
                    options_and_threshold
                )
                model_test_group.feature_importance_test.CopyFrom(
                    feature_importance_test
                )
            model_test_groups.append(model_test_group)
        resp = GetModelTestGroupsResponse(model_test_groups=model_test_groups)
        return resp

    @initialize_grpc_servicer_context
    def GetTestResultsForModel(self, request, context):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_analyzable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="GET_TEST_RESULTS_FOR_MODEL",
            project_id=project_id
        )
        model_id = request.model_id
        model_metadata = self._check_if_model_exists(request_ctx, model_id)
        model_tests = self.get_model_tests(
            request_ctx=request_ctx,
            project_id=project_id,
            test_type=request.test_type,
            split_id=request.split_id,
            data_collection_id=model_metadata.dataset_id
        )
        resp = GetTestResultsForModelResponse()
        performance_tests = {}
        stability_tests = []
        fairness_tests = []
        for test in model_tests:
            if test.test_type == _PBModelTestType.MODEL_TEST_TYPE_PERFORMANCE:
                accuracy_type = test.performance_test.performance_metric_and_threshold.accuracy_type
                performance_tests[accuracy_type] = performance_tests.get(
                    accuracy_type, []
                ) + [test]
            elif test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FAIRNESS:
                fairness_tests.append(test)
            elif test.test_type == _PBModelTestType.MODEL_TEST_TYPE_STABILITY:
                stability_tests.append(test)
            elif test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE:
                test_result = self._get_feature_importance_test_result(
                    request_ctx,
                    project_id,
                    model_id,
                    test,
                    resp,
                    model_data_collection_id=model_metadata.dataset_id
                )
                if test_result is not None:
                    resp.feature_importance_test_results.extend(test_result)
            else:
                raise ValueError(f"Test type {test.test_type} not supported!")
        for performance_tests_with_single_metric in performance_tests.values():
            resp.performance_test_results.extend(
                self._get_batched_performance_test_results(
                    request_ctx,
                    project_id,
                    model_id,
                    performance_tests_with_single_metric,
                    resp,
                    model_data_collection_id=model_metadata.dataset_id
                )
            )
        resp.stability_test_results.extend(
            self._get_batched_stability_test_result(
                request_ctx=request_ctx,
                project_id=project_id,
                model_id=model_id,
                tests=stability_tests,
                get_response=resp,
                model_data_collection_id=model_metadata.dataset_id
            )
        )
        resp.fairness_test_results.extend(
            self._get_batched_fairness_test_result(
                request_ctx=request_ctx,
                project_id=project_id,
                model_id=model_id,
                tests=fairness_tests,
                get_response=resp,
                model_data_collection_id=model_metadata.dataset_id
            )
        )
        return resp

    def GetDataSplitsFromRegex(
        self, request: modeltest_service_pb2.GetDataSplitsFromRegexRequest,
        context: grpc.ServicerContext
    ):
        project_id = request.project_id
        self._check_if_project_exists(project_id, context)
        request_ctx = check_permission_helper.authenticate_and_audit_request_viewable(
            logger=self.logger,
            request_ctx_helper=self.request_ctx_helper,
            rbac_client=self.rbac_client,
            context=context,
            caller_name="GET_DATA_SPLITS_FROM_REGEX",
            project_id=project_id
        )

        if not (
            request.data_collection_ids or request.data_collection_name_regex
        ):
            raise TruEraInvalidArgumentError(
                f"Request must specify either `data_collection_ids` or `data_collection_name_regex`: {request}"
            )

        try:
            data_splits = self._get_data_splits_from_regex(
                request_ctx=request_ctx,
                project_id=project_id,
                data_split_name_regex=request.split_name_regex,
                data_collection_ids=request.data_collection_ids,
                data_collection_name_regex=request.data_collection_name_regex
            )
        except re.error as e:
            raise TruEraInvalidArgumentError(
                f"Error when compiling regex in request: {e}. Request:{request}"
            )
        except ValueError as e:
            raise TruEraInvalidArgumentError(
                f"Error when trying to get splits from regex: {e}. Request:{request}"
            )

        resp = modeltest_service_pb2.GetDataSplitsFromRegexResponse(
            splits_metadata=[
                transform_split_to_public(i, context) for i in data_splits
            ]
        )
        return resp

    def _get_protected_segment_ids_from_regex(
        self, request_ctx: RequestContext, project_id: str,
        segment_name_regex: str
    ) -> Sequence[_PBSegmentID]:
        segment_name_re = re.compile(segment_name_regex)
        segment_groups = self.segmentation_dao.get_all(
            request_ctx=request_ctx, project_id=project_id
        )
        result = []
        for sg in segment_groups:
            for segment in sg.segments:
                if segment.is_protected and segment_name_re.match(segment.name):
                    result.append(
                        _PBSegmentID(
                            segmentation_id=sg.id, segment_name=segment.name
                        )
                    )
        return result

    def _get_data_splits_from_regex(
        self,
        request_ctx: RequestContext,
        project_id: str,
        data_split_name_regex: str,
        data_collection_ids: Optional[Sequence[str]] = None,
        data_collection_name_regex: Optional[str] = None
    ) -> Sequence[_PBDataSplit]:
        if not (data_collection_ids or data_collection_name_regex):
            raise TruEraInvalidArgumentError(
                "Need to provide either `data_collection_id` or `data_collection_name_regex`."
            )
        if data_collection_ids and data_collection_name_regex:
            raise TruEraInvalidArgumentError(
                "Please only provide one of `data_collection_id` or `data_collection_name_regex`."
            )
        data_split_re = re.compile(data_split_name_regex)
        data_collection_re = None
        query = ""
        if data_collection_ids:
            query += " OR ".join(
                [f"dataset_id='{dc_id}'" for dc_id in data_collection_ids]
            )
        elif data_collection_name_regex:
            data_collection_re = re.compile(data_collection_name_regex)
            data_collections = self.dataset_dao.get_all(
                request_ctx=request_ctx, project_id=project_id, as_proto=True
            )
            matched_dc_ids = [
                dc.id
                for dc in data_collections
                if data_collection_re.match(dc.name)
            ]
            query += " OR ".join(
                [f"dataset_id='{dc_id}'" for dc_id in matched_dc_ids]
            )
        else:
            raise ValueError(
                "Please provide either `data_collection_id` or `data_collection_name_regex`."
            )

        data_splits: Sequence[_PBDataSplit] = self.datasplit_dao.search(
            project_id=project_id,
            query=query,
            as_proto=True,
            request_ctx=request_ctx
        )
        data_splits = _filter_to_active_splits(data_splits)
        data_splits = filter_to_non_prod_splits(data_splits)
        return [i for i in data_splits if data_split_re.match(i.name)]

    def _get_batched_performance_test_results(
        self, request_ctx: RequestContext, project_id: str, model_id: str,
        tests: Sequence[_PBModelTest],
        get_response: GetTestResultsForModelResponse,
        model_data_collection_id: str
    ) -> Sequence[modeltest_service_pb2.PerformanceTestResult]:
        model_input_specs = []
        aiq_client = self._get_aiq_client(request_ctx)
        metric_name = _PBAccuracyType.Type.Name(
            tests[0].performance_test.performance_metric_and_threshold.
            accuracy_type
        )
        rets = []
        test_ids = []
        for test in tests:
            if test.split_name_regex:
                data_splits = self._get_data_splits_from_regex(
                    request_ctx=request_ctx,
                    project_id=project_id,
                    data_split_name_regex=test.split_name_regex,
                    data_collection_ids=[model_data_collection_id]
                )
                split_ids = [i.id for i in data_splits]
            else:
                split_ids = [test.split_id]
            for split_id in split_ids:
                mis = ModelInputSpec(
                    split_id=split_id, all_available_inputs=True
                )
                if test.segment_id.segmentation_id:
                    mis.filter_expression.CopyFrom(
                        self._get_segment_proto(
                            request_ctx, test.segment_id.segmentation_id,
                            test.segment_id.segment_name
                        ).filter_expression
                    )
                model_input_specs.append(mis)
                test_ids.append(test.id)
                test_result = modeltest_service_pb2.PerformanceTestResult(
                    test_details=test
                )
                test_result.test_details.split_id = split_id
                rets.append(test_result)

        performance_aiq_response = aiq_client.compute_batched_performance(
            project_id=project_id,
            model_id=model_id,
            input_specs=model_input_specs,
            metric_type=metric_name,
            as_proto=True,
            wait=False
        )

        for pending_ops, test_id in zip(
            performance_aiq_response.pending_operations, test_ids
        ):
            if pending_ops:
                get_response.pending_operations.waiting_on_operation_ids.extend(
                    pending_ops
                )
                get_response.pending_test_results.pending_test_ids.append(
                    test_id
                )
        if get_response.pending_operations.waiting_on_operation_ids:
            return rets

        for accuracy, ret in zip(performance_aiq_response.response, rets):
            if accuracy.type == _PBAccuracyResult.AccuracyResultType.VALUE:
                ret.metric_result = accuracy.value
                ret.result_type = _PBTestResultType.VALUE
            elif accuracy.type == _PBAccuracyResult.AccuracyResultType.PREDICTION_UNAVAILABLE:
                ret.metric_result = np.nan
                ret.result_type = _PBTestResultType.PREDICTION_UNAVAILABLE
                ret.error_message = f"{_BASE_ERROR_MESSAGE}: {accuracy.error_message}"
                continue
            else:
                ret.metric_result = np.nan
                ret.result_type = _PBTestResultType.OTHER_EXCEPTION
                ret.error_message = f"{_BASE_ERROR_MESSAGE}: {accuracy.error_message}"
                continue

            metric_and_threshold = ret.test_details.performance_test.performance_metric_and_threshold
            ret.warning_result = self._evaluate_score_against_threshold(
                request_ctx,
                score=ret.metric_result,
                threshold=metric_and_threshold.threshold_warning,
                project_id=project_id,
                model_id=model_id,
                metric_name=metric_name,
                segment_id_proto=ret.test_details.segment_id,
                get_response=get_response,
                test_id=ret.test_details.id,
                split_id=ret.test_details.split_id
            )
            ret.pass_fail_result = self._evaluate_score_against_threshold(
                request_ctx,
                score=ret.metric_result,
                threshold=metric_and_threshold.threshold_fail,
                project_id=project_id,
                model_id=model_id,
                metric_name=metric_name,
                segment_id_proto=ret.test_details.segment_id,
                get_response=get_response,
                test_id=ret.test_details.id,
                split_id=ret.test_details.split_id
            )
        return rets

    def _get_batched_stability_test_result(
        self, request_ctx: RequestContext, project_id: str, model_id: str,
        tests: Sequence[_PBModelTest],
        get_response: GetTestResultsForModelResponse,
        model_data_collection_id: str
    ) -> Sequence[modeltest_service_pb2.StabilityTestResult]:
        if not tests:
            return []
        aiq_client = self._get_aiq_client(request_ctx)
        distance_type_to_output_specs = {}
        distance_type_to_test_results = {}
        for test in tests:
            if test.split_name_regex:
                data_splits = self._get_data_splits_from_regex(
                    request_ctx=request_ctx,
                    project_id=project_id,
                    data_split_name_regex=test.split_name_regex,
                    data_collection_ids=[model_data_collection_id]
                )
                split_ids = [i.id for i in data_splits]
            else:
                split_ids = [test.split_id]

            distance_type_name = _PBDistanceType.Name(
                test.stability_test.stability_metric_and_threshold.distance_type
            )
            if distance_type_name not in distance_type_to_output_specs:
                distance_type_to_output_specs[distance_type_name] = []
                distance_type_to_test_results[distance_type_name] = []

            if test.stability_test.base_split_id:
                base_data_split_id = test.stability_test.base_split_id
                base_data_split_metadata = self._check_if_split_exists(
                    request_ctx, base_data_split_id
                )
                base_data_split_dc_id = base_data_split_metadata.dataset_id
            else:
                base_data_split_id = self.model_dao.get_by_id(
                    obj_id=model_id, request_ctx=request_ctx
                ).training_metadata.train_split_id
                base_data_split_dc_id = model_data_collection_id
            if not base_data_split_id or base_data_split_dc_id != model_data_collection_id:
                continue
            segment = None
            if test.segment_id.segment_name:
                segment_proto = self._get_segment_proto(
                    request_ctx, test.segment_id.segmentation_id,
                    test.segment_id.segment_name
                )
                segment = Segment(segment_proto.name, project_id, segment_proto)
            for split_id in split_ids:
                ret = modeltest_service_pb2.StabilityTestResult()
                ret.test_details.CopyFrom(test)
                ret.test_details.split_id = split_id
                distance_type_to_output_specs[distance_type_name].append(
                    (
                        ModelOutputSpec(model_id, base_data_split_id, segment),
                        ModelOutputSpec(model_id, split_id, segment)
                    )
                )
                distance_type_to_test_results[distance_type_name].append(ret)

        batched_stability_aiq_response = aiq_client.batch_compute_model_score_instability(
            project_id=project_id,
            distance_type_to_output_specs=distance_type_to_output_specs,
            as_proto=True,
            wait=False
        )
        if batched_stability_aiq_response.pending_operations:
            get_response.pending_operations.waiting_on_operation_ids.extend(
                batched_stability_aiq_response.pending_operations
            )
            get_response.pending_test_results.pending_test_ids.append(test.id)
        rets = []
        for distance_type_name, distance_results in batched_stability_aiq_response.response.items(
        ):
            for i, ret in enumerate(
                distance_type_to_test_results[distance_type_name]
            ):
                result = distance_results[i]
                if result.result_type == _PBBatchCompareModelOutputResponse.CompareModelOutputResultType.VALUE:
                    ret.metric_result = result.distance_value
                    ret.result_type = _PBTestResultType.VALUE
                elif result.result_type == _PBBatchCompareModelOutputResponse.CompareModelOutputResultType.PREDICTION_UNAVAILABLE:
                    ret.metric_result = np.nan
                    ret.result_type = _PBTestResultType.PREDICTION_UNAVAILABLE
                    ret.error_message = f"{_BASE_ERROR_MESSAGE}: {result.error_message}"
                    rets.append(ret)
                    continue
                else:
                    ret.metric_result = np.nan
                    ret.result_type = _PBTestResultType.OTHER_EXCEPTION
                    ret.error_message = f"{_BASE_ERROR_MESSAGE}: {result.error_message}"
                    rets.append(ret)
                    continue

                test = ret.test_details
                metric_and_threshold = test.stability_test.stability_metric_and_threshold
                ret.warning_result = self._evaluate_score_against_threshold(
                    request_ctx,
                    score=ret.metric_result,
                    threshold=metric_and_threshold.threshold_warning,
                    project_id=project_id,
                    model_id=model_id,
                    metric_name=distance_type_name,
                    segment_id_proto=test.segment_id,
                    get_response=get_response,
                    test_id=test.id
                )
                ret.pass_fail_result = self._evaluate_score_against_threshold(
                    request_ctx,
                    score=ret.metric_result,
                    threshold=metric_and_threshold.threshold_fail,
                    project_id=project_id,
                    model_id=model_id,
                    metric_name=distance_type_name,
                    segment_id_proto=test.segment_id,
                    get_response=get_response,
                    test_id=test.id
                )
                rets.append(ret)
        return rets

    def _get_batched_fairness_test_result(
        self, request_ctx: RequestContext, project_id: str, model_id: str,
        tests: Sequence[_PBModelTest],
        get_response: GetTestResultsForModelResponse,
        model_data_collection_id: str
    ) -> Sequence[modeltest_service_pb2.FairnessTestResult]:
        if not tests:
            return []
        aiq_client = self._get_aiq_client(request_ctx)
        segments_map = self._get_all_segments_in_project(
            project_id, request_ctx
        )
        batch_bias_requests = {}
        results = []

        def get_request_key_from_test_pb(test_pb: _PBModelTest):
            return (
                test_pb.split_id,
                test_pb.fairness_test.segment_id_protected.segmentation_id,
                test_pb.fairness_test.segment_id_protected.segment_name,
                test_pb.fairness_test.segment_id_comparison.segmentation_id,
                test_pb.fairness_test.segment_id_comparison.segment_name
            )

        for test in tests:
            if test.split_name_regex:
                data_splits = self._get_data_splits_from_regex(
                    request_ctx=request_ctx,
                    project_id=project_id,
                    data_split_name_regex=test.split_name_regex,
                    data_collection_ids=[model_data_collection_id]
                )
                split_ids = [i.id for i in data_splits]
            else:
                split_ids = [test.split_id]
            protected_segments = []
            comparison_segments = []
            if test.fairness_test.protected_segment_name_regex:
                protected_segments = self._get_protected_segment_ids_from_regex(
                    request_ctx, project_id,
                    test.fairness_test.protected_segment_name_regex
                )
                comparison_segments = [
                    _PBSegmentID() for i in protected_segments
                ]
            else:
                protected_segments.append(
                    test.fairness_test.segment_id_protected
                )
                comparison_segments.append(
                    test.fairness_test.segment_id_comparison
                )
            for split_id in split_ids:
                for i, _ in enumerate(protected_segments):
                    ret = modeltest_service_pb2.FairnessTestResult()
                    ret.test_details.CopyFrom(test)
                    ret.test_details.split_id = split_id
                    ret.test_details.fairness_test.segment_id_protected.CopyFrom(
                        protected_segments[i]
                    )
                    ret.test_details.fairness_test.segment_id_comparison.CopyFrom(
                        comparison_segments[i]
                    )
                    results.append(ret)

                    bias_type_name = _PBBiasType.Type.Name(
                        test.fairness_test.fairness_metric_and_threshold.
                        bias_type
                    )
                    protected_segment = Segment(
                        name=protected_segments[i].segment_name,
                        project_id=project_id,
                        segment_proto=segments_map[(
                            protected_segments[i].segmentation_id,
                            protected_segments[i].segment_name
                        )]
                    )
                    comparison_segment = None
                    if comparison_segments[i].segment_name:
                        comparison_segment = Segment(
                            name=comparison_segments[i].segment_name,
                            project_id=project_id,
                            segment_proto=segments_map[(
                                comparison_segments[i].segmentation_id,
                                comparison_segments[i].segment_name
                            )]
                        )
                    key = get_request_key_from_test_pb(ret.test_details)
                    if key not in batch_bias_requests:
                        batch_bias_requests[key] = (
                            ModelBiasRequest(
                                model_id=model_id,
                                data_split_id=split_id,
                                protected_segment=protected_segment,
                                comparison_segment=comparison_segment,
                                bias_types=[]
                            ), test.id
                        )
                    batch_bias_requests[key][0].bias_types.append(
                        bias_type_name
                    )

        if not batch_bias_requests:
            return results
        bias_requests_list, test_ids = zip(*batch_bias_requests.values())
        batched_fairness_aiq_response = aiq_client.batch_compute_fairness(
            project_id=project_id, bias_requests=bias_requests_list, wait=False
        )

        def get_result_key(
            *, split_id: str, protected_segment_pb: _PBSegment,
            comparison_segment_pb: _PBSegment, bias_type: str
        ):
            protected_segment_def = FilterProcessor.stringify_filter(
                protected_segment_pb.filter_expression, ingestable=True
            )
            comparison_segment_def = FilterProcessor.stringify_filter(
                comparison_segment_pb.filter_expression, ingestable=True
            ) if comparison_segment_pb else None
            return (
                split_id, protected_segment_def, comparison_segment_def,
                bias_type
            )

        results_map = {}
        for i, bias_request in enumerate(bias_requests_list):
            for bias_result in batched_fairness_aiq_response.response[i]:
                key = get_result_key(
                    split_id=bias_request.data_split_id,
                    protected_segment_pb=bias_request.protected_segment.
                    _segment_proto,
                    comparison_segment_pb=bias_request.comparison_segment.
                    _segment_proto if bias_request.comparison_segment else None,
                    bias_type=bias_result.metric_name
                )
                results_map[key] = bias_result
            pending_op_ids = batched_fairness_aiq_response.pending_operations[i]
            if pending_op_ids:
                get_response.pending_operations.waiting_on_operation_ids.extend(
                    pending_op_ids
                )
                get_response.pending_test_results.pending_test_ids.append(
                    test_ids[i]
                )
        for ret in results:
            test = ret.test_details
            protected_segment_id = ret.test_details.fairness_test.segment_id_protected
            protected_segment_pb = segments_map.get(
                (
                    protected_segment_id.segmentation_id,
                    protected_segment_id.segment_name
                )
            )
            comparison_segment_id = ret.test_details.fairness_test.segment_id_comparison
            comparison_segment_pb = segments_map.get(
                (
                    comparison_segment_id.segmentation_id,
                    comparison_segment_id.segment_name
                )
            )

            key = get_result_key(
                split_id=test.split_id,
                protected_segment_pb=protected_segment_pb,
                comparison_segment_pb=comparison_segment_pb,
                bias_type=_PBBiasType.Type.Name(
                    test.fairness_test.fairness_metric_and_threshold.bias_type
                )
            )
            if key in results_map:
                result = results_map[key]
                if result.result_type == _PBBiasResult.BiasResultType.VALUE:
                    ret.metric_result = result.aggregate_metric
                    ret.result_type = _PBTestResultType.VALUE
                elif result.result_type == _PBBiasResult.BiasResultType.PREDICTION_UNAVAILABLE:
                    ret.metric_result = np.nan
                    ret.result_type = _PBTestResultType.PREDICTION_UNAVAILABLE
                    ret.error_message = f"{_BASE_ERROR_MESSAGE}: {result.error_message}"
                else:
                    ret.metric_result = np.nan
                    ret.result_type = _PBTestResultType.OTHER_EXCEPTION
                    ret.error_message = f"{_BASE_ERROR_MESSAGE}: {result.error_message}"
                    continue
            else:
                ret.metric_result = np.nan
            metric_and_threshold = test.fairness_test.fairness_metric_and_threshold
            ret.warning_result = self._evaluate_score_against_threshold(
                request_ctx,
                score=ret.metric_result,
                threshold=metric_and_threshold.threshold_warning,
                project_id=project_id,
                model_id=model_id,
                metric_name=bias_type_name,
                segment_id_proto=test.segment_id,
                get_response=get_response,
                test_id=test.id
            )
            ret.pass_fail_result = self._evaluate_score_against_threshold(
                request_ctx,
                score=ret.metric_result,
                threshold=metric_and_threshold.threshold_fail,
                project_id=project_id,
                model_id=model_id,
                metric_name=bias_type_name,
                segment_id_proto=test.segment_id,
                get_response=get_response,
                test_id=test.id
            )
        return results

    def _get_feature_importance_test_result(
        self, request_ctx: RequestContext, project_id: str, model_id: str,
        test: _PBModelTest, get_response: GetTestResultsForModelResponse,
        model_data_collection_id: str
    ) -> Sequence[modeltest_service_pb2.StabilityTestResult]:
        if test.split_name_regex:
            data_splits = self._get_data_splits_from_regex(
                request_ctx=request_ctx,
                project_id=project_id,
                data_split_name_regex=test.split_name_regex,
                data_collection_ids=[model_data_collection_id]
            )
            split_ids = [i.id for i in data_splits]
        else:
            split_ids = [test.split_id]
        results = []
        for split_id in split_ids:
            ret = modeltest_service_pb2.FeatureImportanceTestResult()
            ret.test_details.CopyFrom(test)
            ret.test_details.split_id = split_id
            options_and_threshold = test.feature_importance_test.options_and_threshold
            score_type = aiq_proto.GetScoreTypeFromQuantityOfInterest(
                options_and_threshold.qoi
            )
            try:
                self._check_if_model_and_split_in_the_same_dc(
                    request_ctx, model_id,
                    test.feature_importance_test.background_split_id
                )
            except TruEraInvalidArgumentError as exc:
                self.logger.warning(exc)
                continue
            try:
                feature_importance_aiq_response = self._get_feature_importances(
                    request_ctx=request_ctx,
                    project_id=project_id,
                    model_id=model_id,
                    data_split_id=split_id,
                    score_type=score_type,
                    segment_id_proto=test.segment_id,
                    background_split_id=test.feature_importance_test.
                    background_split_id
                )
                if feature_importance_aiq_response.pending_operations:
                    get_response.pending_operations.waiting_on_operation_ids.extend(
                        feature_importance_aiq_response.pending_operations
                    )
                    get_response.pending_test_results.pending_test_ids.append(
                        test.id
                    )
                else:
                    feature_importances = feature_importance_aiq_response.response
                    ret.num_features_below_importance_threshold = np.sum(
                        feature_importances.to_numpy() <
                        options_and_threshold.min_importance_value
                    )
                    ret.result_type = _PBTestResultType.VALUE
                    ret.warning_result = self._evaluate_score_against_threshold(
                        request_ctx,
                        score=ret.num_features_below_importance_threshold,
                        threshold=options_and_threshold.threshold_warning,
                        project_id=project_id,
                        model_id=model_id,
                        metric_name=None,
                        segment_id_proto=test.segment_id,
                        get_response=get_response,
                        test_id=test.id
                    )
                    ret.pass_fail_result = self._evaluate_score_against_threshold(
                        request_ctx,
                        score=ret.num_features_below_importance_threshold,
                        threshold=options_and_threshold.threshold_fail,
                        project_id=project_id,
                        model_id=model_id,
                        metric_name=None,
                        segment_id_proto=test.segment_id,
                        get_response=get_response,
                        test_id=test.id
                    )
            except NotFoundError as err:
                ret.result_type = _PBTestResultType.INFLUENCE_UNAVAILABLE
                ret.error_message = f"{_BASE_ERROR_MESSAGE}: {err.message}"
            except Exception as exc:
                ret.result_type = _PBTestResultType.OTHER_EXCEPTION
                ret.error_message = f"{_BASE_ERROR_MESSAGE}: {str(exc)}"
            results.append(ret)
        return results

    def _evaluate_score_against_single_value_threshold(
        self, request_context: RequestContext, *, score: float,
        threshold: modeltest_pb2.TestThreshold, project_id: str, model_id: str,
        metric_name: str, segment_id_proto: _PBSegmentID,
        get_response: GetTestResultsForModelResponse, test_id: str,
        split_id: str
    ) -> modeltest_service_pb2.ThresholdResult:
        if np.isnan(score):
            return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
        effective_threshold = threshold.value.value
        if threshold.threshold_type == modeltest_pb2.TestThreshold.ThresholdType.RELATIVE_SINGLE_VALUE:
            performance_aiq_response = self._compute_performance_on_reference_split_or_model(
                request_context=request_context,
                threshold=threshold,
                project_id=project_id,
                model_id=model_id,
                metric_name=metric_name,
                segment_id_proto=segment_id_proto,
                split_id=split_id
            )
            if performance_aiq_response is None:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            if performance_aiq_response.pending_operations:
                get_response.pending_operations.waiting_on_operation_ids.extend(
                    performance_aiq_response.pending_operations
                )
                get_response.pending_test_results.pending_test_ids.append(
                    test_id
                )
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            response = performance_aiq_response.response[0]
            if response.type == _PBAccuracyResult.AccuracyResultType.VALUE:
                effective_threshold = response.value + threshold.value.value * response.value
            elif response.type == _PBAccuracyResult.AccuracyResultType.PREDICTION_UNAVAILABLE:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            else:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
        if threshold.value.condition == modeltest_pb2.TestThreshold.ThresholdValue.WARN_OR_FAIL_IF_LESS_THAN:
            if score < effective_threshold:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_FAIL
            return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_PASS
        elif threshold.value.condition == modeltest_pb2.TestThreshold.ThresholdValue.WARN_OR_FAIL_IF_GREATER_THAN:
            if score > effective_threshold:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_FAIL
            return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_PASS
        return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED

    def _evaluate_score_against_value_range_threshold(
        self, request_context: RequestContext, *, score: float,
        threshold: modeltest_pb2.TestThreshold, project_id: str, model_id: str,
        metric_name: str, segment_id_proto: _PBSegmentID,
        get_response: GetTestResultsForModelResponse, test_id: str,
        split_id: str
    ) -> modeltest_service_pb2.ThresholdResult:
        if np.isnan(score):
            return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
        effective_lower_bound = threshold.value_range.lower_bound
        effective_upper_bound = threshold.value_range.upper_bound
        if threshold.threshold_type == modeltest_pb2.TestThreshold.ThresholdType.RELATIVE_VALUE_RANGE:
            performance_aiq_response = self._compute_performance_on_reference_split_or_model(
                request_context=request_context,
                threshold=threshold,
                project_id=project_id,
                model_id=model_id,
                metric_name=metric_name,
                segment_id_proto=segment_id_proto,
                split_id=split_id
            )
            if performance_aiq_response is None:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            if performance_aiq_response.pending_operations:
                get_response.pending_operations.waiting_on_operation_ids.extend(
                    performance_aiq_response.pending_operations
                )
                get_response.pending_test_results.pending_test_ids.append(
                    test_id
                )
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            response = performance_aiq_response.response[0]
            if response.type == _PBAccuracyResult.AccuracyResultType.VALUE:
                reference_score = response.value
            elif response.type == _PBAccuracyResult.AccuracyResultType.PREDICTION_UNAVAILABLE:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            else:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED
            effective_lower_bound = reference_score + threshold.value_range.lower_bound * reference_score
            effective_upper_bound = reference_score + threshold.value_range.upper_bound * reference_score
        if threshold.value_range.condition == modeltest_pb2.TestThreshold.ThresholdValueRange.WARN_OR_FAIL_IF_WITHIN:
            if effective_lower_bound < score and score < effective_upper_bound:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_FAIL
            return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_PASS
        elif threshold.value_range.condition == modeltest_pb2.TestThreshold.ThresholdValueRange.WARN_OR_FAIL_IF_OUTSIDE:
            if score < effective_lower_bound or score > effective_upper_bound:
                return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_FAIL
            return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_PASS
        return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED

    def _compute_performance_on_reference_split_or_model(
        self, request_context: RequestContext, *,
        threshold: modeltest_pb2.TestThreshold, project_id: str, model_id: str,
        metric_name: str, segment_id_proto: _PBSegmentID, split_id: str
    ) -> Optional[AiqClientResponse]:
        split_metadata = self._check_if_split_exists(request_context, split_id)
        try:
            self._check_if_model_and_split_in_the_same_dc(
                request_context,
                threshold.reference_model_id,
                threshold.reference_split_id,
                test_data_collection_id=split_metadata.dataset_id
            )
        except TruEraInvalidArgumentError as exc:
            self.logger.warning(exc)
            return
        if threshold.reference_model_id:
            if threshold.reference_split_id:
                performance_aiq_response = self._get_performance(
                    request_context, project_id, threshold.reference_model_id,
                    threshold.reference_split_id, metric_name, segment_id_proto
                )
            else:
                performance_aiq_response = self._get_performance(
                    request_context, project_id, threshold.reference_model_id,
                    split_id, metric_name, segment_id_proto
                )
        else:
            reference_split_id = threshold.reference_split_id or self.model_dao.get_by_id(
                obj_id=model_id, request_ctx=request_context
            ).training_metadata.train_split_id
            if not reference_split_id:
                return None
            performance_aiq_response = self._get_performance(
                request_context, project_id, model_id, reference_split_id,
                metric_name, segment_id_proto
            )
        return performance_aiq_response

    def _evaluate_score_against_threshold(
        self,
        request_ctx: RequestContext,
        *,
        score: float,
        threshold: modeltest_pb2.TestThreshold,
        project_id: str,
        model_id: str,
        metric_name: str,
        segment_id_proto: _PBSegmentID,
        get_response: GetTestResultsForModelResponse,
        test_id: str,
        split_id: Optional[str] = None
    ) -> modeltest_service_pb2.ThresholdResult:
        if threshold.WhichOneof("threshold") == "value":
            return self._evaluate_score_against_single_value_threshold(
                request_context=request_ctx,
                score=score,
                threshold=threshold,
                project_id=project_id,
                model_id=model_id,
                metric_name=metric_name,
                segment_id_proto=segment_id_proto,
                get_response=get_response,
                test_id=test_id,
                split_id=split_id
            )
        elif threshold.WhichOneof("threshold") == "value_range":
            return self._evaluate_score_against_value_range_threshold(
                request_context=request_ctx,
                score=score,
                threshold=threshold,
                project_id=project_id,
                model_id=model_id,
                metric_name=metric_name,
                segment_id_proto=segment_id_proto,
                get_response=get_response,
                test_id=test_id,
                split_id=split_id
            )
        return modeltest_service_pb2.ThresholdResult.THRESHOLD_RESULT_UNDEFINED

    def _get_segment_group_name_by_id(
        self, request_ctx: RequestContext, segmentation_id: str
    ) -> str:
        return self.segmentation_dao.get_by_id(
            obj_id=segmentation_id, request_ctx=request_ctx
        ).name

    def _get_segment_proto(
        self, request_ctx: RequestContext, segmentation_id: str,
        segment_name: str
    ) -> _PBSegment:
        segmentation_proto = self.segmentation_dao.get_by_id(
            obj_id=segmentation_id, request_ctx=request_ctx
        )
        if not segmentation_proto:
            raise TruEraNotFoundError(
                f"Couldn't find segment group {segmentation_id}."
            )
        for segment in segmentation_proto.segments:
            if segment.name == segment_name:
                return segment
        raise TruEraNotFoundError(
            f"Couldn't find segment {segment_name} in segment group {segmentation_id}."
        )

    def _get_aiq_client(self, request_context: RequestContext) -> AiqClient:
        auth_details = AuthDetails(
            impersonation_metadata=request_context.get_impersonation_metadata()
        )
        return AiqClient(
            aiq_connection_string=self.aiq_connection_string,
            mrc_connection_string=self.mrc_connection_string,
            auth_details=auth_details,
            use_http=False
        )

    def _get_ar_client(
        self, request_context: RequestContext
    ) -> ArtifactRepoClient:
        auth_details = AuthDetails(
            impersonation_metadata=request_context.get_impersonation_metadata()
        )
        return ArtifactRepoClient(
            connection_string=self.ar_connection_string,
            auth_details=auth_details,
            use_http=False
        )

    def _validate_name_and_description_in_request(
        self,
        request: Union[CreatePerformanceTestRequest, CreateFairnessTestRequest,
                       CreateStabilityTestRequest,
                       CreateFeatureImportanceTestRequest, ModelTestGroup],
        context: grpc.ServicerContext,
        test_group_id: Optional[str] = None,
        test_name_required: bool = False
    ) -> RequestContext:
        request_ctx = self.request_ctx_helper.create_request_context_grpc(
            context
        )
        try:
            ensure_valid_identifier(
                to_check=request.test_name,
                context=context,
                logger=self.logger,
                raise_value_error=True
            )
            ensure_valid_identifier(
                to_check=request.description,
                context=context,
                logger=self.logger,
                raise_value_error=True
            )
        except ValueError as e:
            raise TruEraInvalidArgumentError(str(e))
        # test_name is unique for each test group
        if request.test_name:
            if test_group_id:
                search_params = {
                    "project_id": request.project_id,
                    "test_name": request.test_name,
                    "test_group_id": {
                        "$ne": test_group_id
                    }
                }
            else:
                search_params = {
                    "project_id": request.project_id,
                    "test_name": request.test_name
                }
            existing_tests = self.modeltest_dao.get_all(
                request_ctx=request_ctx, params=search_params, as_proto=True
            )
            if len(existing_tests) > 0:
                raise TruEraAlreadyExistsError(
                    f"Test with name \"{request.test_name}\" already exists: {existing_tests}"
                )
        elif test_name_required:
            raise TruEraInvalidArgumentError(
                f"Need to specify `test_name` in request: {request}"
            )

        return request_ctx

    def _get_model_tests_by_group_id(
        self, request_ctx: RequestContext, project_id: str, test_group_id: str,
        test_type: str
    ) -> str:
        search_params = {
            "project_id": project_id,
            "test_type": test_type,
            "test_group_id": test_group_id
        }
        model_tests = self.modeltest_dao.get_all(
            request_ctx=request_ctx, params=search_params, as_proto=True
        )
        if len(model_tests) == 0:
            raise TruEraNotFoundError(f"No such test group: {test_group_id}")
        return model_tests

    def _get_data_collection_by_id(
        self, request_ctx: RequestContext, data_collection_id: str
    ) -> Optional[str]:
        dc = self.dataset_dao.get_by_id(
            obj_id=data_collection_id, request_ctx=request_ctx, exists=False
        )
        if not dc:
            raise TruEraNotFoundError(
                f"No such data collection: {data_collection_id}"
            )
        return dc

    def _get_data_split_name_by_id(
        self, request_ctx: RequestContext, data_split_id: str
    ) -> Optional[str]:
        data_split = self.datasplit_dao.get_by_id(
            obj_id=data_split_id, request_ctx=request_ctx, exists=False
        )
        if data_split:
            return data_split.name
        raise TruEraNotFoundError(f"No such data split: {data_split_id}")

    def _create_tests_from_templates(
        self, request_ctx: RequestContext,
        test_templates: Sequence[_PBModelTest], request
    ):
        test_ids = []
        if request.data_collection_name_regex:
            for test_template in test_templates:
                model_test_id = str(uuid.uuid4())
                test_template.id = model_test_id
                test_template.data_collection_name_regex = request.data_collection_name_regex
                self.modeltest_dao.add(
                    model_test=test_template,
                    insert_only=True,
                    request_ctx=request_ctx
                )
                test_ids.append(model_test_id)

        elif request.data_collection_ids:
            for data_collection_id in request.data_collection_ids:
                for test_template in test_templates:
                    model_test_id = str(uuid.uuid4())
                    model_test = _PBModelTest()
                    model_test.CopyFrom(test_template)
                    if model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_STABILITY:
                        base_split_id = request.data_collection_id_to_base_split_id.get(
                            data_collection_id
                        )
                        if base_split_id:
                            model_test.stability_test.base_split_id = base_split_id
                    if model_test.test_type == _PBModelTestType.MODEL_TEST_TYPE_FEATURE_IMPORTANCE:
                        background_split_id = request.data_collection_id_to_base_split_id.get(
                            data_collection_id
                        )
                        if background_split_id:
                            model_test.feature_importance_test.background_split_id = background_split_id
                    model_test.id = model_test_id
                    model_test.data_collection_id = data_collection_id
                    self.modeltest_dao.add(
                        model_test=model_test,
                        insert_only=True,
                        request_ctx=request_ctx
                    )
                    test_ids.append(model_test_id)
        return test_ids

    def _assign_test_group_for_legacy_tests(self, request_ctx: RequestContext):
        model_tests = self.modeltest_dao.search(
            request_ctx=request_ctx, query="test_group_id=null", as_proto=True
        )
        count = 0
        for model_test in model_tests:
            if model_test.test_group_id == "":
                count += 1
                model_test.test_group_id = model_test.id
                self.modeltest_dao.add(
                    model_test=model_test,
                    insert_only=False,
                    request_ctx=request_ctx
                )
        self.logger.info(
            f"Assigned test_group_id to {len(model_tests)} legacy tests."
        )

    def _get_all_segments_in_project(
        self, project_id: str, request_ctx: RequestContext
    ) -> Mapping[Tuple[str, str], _PBSegment]:
        segment_groups = self.segmentation_dao.get_all(
            request_ctx, project_id=project_id
        )
        segments_map: Mapping[Tuple[str, str], _PBSegment] = {}
        for sg in segment_groups:
            for segment in sg.segments:
                segments_map[(sg.id, segment.name)] = segment
        return segments_map
