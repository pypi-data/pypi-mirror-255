from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    import pandas as pd

    from truera.authn.usercontext import RequestContext
    from truera.client.public.auth_details import AuthDetails
    from truera.client.services.aiq_client import AiqClient
    from truera.client.services.artifact_interaction_client import \
        ArtifactInteractionClient
    from truera.client.services.artifact_repo_client_factory import \
        get_ar_client
    from truera.client.services.data_service_client import DataServiceClient
    from truera.modeltest.baseline_models import ClassificationBaseLineModel
    from truera.modeltest.baseline_models import RegressionBaseLineModel

from dataclasses import dataclass
from datetime import timedelta
import logging

from temporalio import activity
from temporalio.common import RetryPolicy

from truera.utils.data_utils import drop_data_with_no_labels


@dataclass
class BaselineModelCreationRequest:
    request_context: RequestContext
    aiq_connection_string: str
    mrc_connection_string: str
    ar_connection_string: str
    ds_connection_string: str
    project_id: str
    project_name: str
    data_collection_id: str
    data_collection_name: str
    split_id: str
    split_name: str
    output_type: str


MAX_ATTEMPTS_RETRY = 3


@workflow.defn
class BaselineModelCreationWorkflow:

    @workflow.run
    async def run(self, request: BaselineModelCreationRequest) -> str:
        return await workflow.execute_activity(
            create_baseline_model,
            request,
            start_to_close_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(maximum_attempts=MAX_ATTEMPTS_RETRY)
        )


BASELINE_MODEL_MAX_DATA_ROWS = 10000
MAX_RETRY_FOR_SPLITS = 5


@activity.defn
async def create_baseline_model(req: BaselineModelCreationRequest) -> None:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info(f"Model test creation: {req.project_id}, {req.split_id}!")
    aiq_client = _get_aiq_client(
        req.request_context, req.aiq_connection_string,
        req.mrc_connection_string
    )
    auth = AuthDetails(
        impersonation_metadata=req.request_context.get_impersonation_metadata()
    )
    ar_client = get_ar_client(
        connection_string=req.ar_connection_string,
        auth_details=auth,
        use_http=False,
        ignore_version_mismatch=True
    )
    ds_client = DataServiceClient.create(
        connection_string=req.ds_connection_string,
        auth_details=auth,
        use_http=False
    )
    ar_interaction_client = ArtifactInteractionClient(ar_client, ds_client)
    xs_and_ys = aiq_client.get_xs_and_ys(
        req.project_id,
        req.split_id,
        req.data_collection_id,
        stop=BASELINE_MODEL_MAX_DATA_ROWS,
        get_post_processed_data=True,
        pre_processed_data_required=False
    ).response
    xs, ys = drop_data_with_no_labels(xs_and_ys.xs, xs_and_ys.ys)
    xs.fillna(0, inplace=True)

    if ys.shape[0] > 0 and (ys.shape[0] == xs.shape[0]):
        if req.output_type == "classification":
            model = ClassificationBaseLineModel(
                req.project_id, req.project_name, req.split_name
            )
        if req.output_type == "regression":
            model = RegressionBaseLineModel(
                req.project_id, req.project_name, req.split_name
            )
        model.build_model(xs, ys)
        logger.info(f"Model score: {model.score(xs, ys)}!")
        model_id = model.ingest_model(
            ar_interaction_client, req.data_collection_name
        )

        existing_splits = ar_interaction_client.get_all_datasplits_in_data_collection(
            req.project_name, req.data_collection_name, fetch_metadata=True
        )

        for split in existing_splits["name_id_pairs"]:
            for attempts in range(0, MAX_RETRY_FOR_SPLITS):
                try:
                    aiq_client.get_ys_pred(
                        req.project_id,
                        model_id,
                        split["id"],
                        include_all_points=True,
                        wait=False
                    )
                    aiq_client.get_feature_influences(
                        req.project_id, model_id, split["id"], wait=False
                    )
                except:
                    attempts += 1
                    continue
            else:
                logger.error(f"Unable to calculate for split: {split}")

    else:
        raise AssertionError(
            f"Invalid data for model creation. X shape: {xs.shape}, Y shape: {ys.shape}"
        )


def _get_aiq_client(
    request_context: RequestContext, aiq_connection_string: str,
    mrc_connection_string: str
) -> AiqClient:
    auth_details = AuthDetails(
        impersonation_metadata=request_context.get_impersonation_metadata()
    )
    return AiqClient(
        aiq_connection_string=aiq_connection_string,
        mrc_connection_string=mrc_connection_string,
        auth_details=auth_details,
        use_http=False
    )