from __future__ import annotations

from typing import List, Mapping

from google.protobuf.timestamp_pb2 import \
    Timestamp  # pylint: disable=no-name-in-module

from truera.client.ingestion import ColumnSpec
from truera.client.ingestion import ModelOutputContext
from truera.client.ingestion.constants import DEFAULT_APPROX_MAX_ROWS
from truera.client.ingestion.constants import DEFAULT_SPLIT_TYPE
from truera.client.ingestion.ingestion import _build_materialize_request
from truera.client.ingestion.ingestion import _submit_data_service_requests
from truera.client.ingestion.ingestion_validation_util import \
    PROD_DATA_SPLIT_TYPE
from truera.client.services.scheduled_ingestion_client import _DEFAULT_SCHEDULE
from truera.client.truera_workspace import TrueraWorkspace
# pylint: disable=no-name-in-module
from truera.protobuf.public.common.data_kind_pb2 import DATA_KIND_ALL
from truera.protobuf.public.common.schema_pb2 import ColumnDetails
from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb
from truera.protobuf.public.data_service import data_service_pb2 as ds_pb
from truera.protobuf.public.util.data_type_pb2 import DataType
from truera.protobuf.public.util.data_type_pb2 import StaticDataTypeEnum
from truera.protobuf.public.util.time_range_pb2 import TimeRange

# pylint: enable=no-name-in-module

DEFAULT_ID_COLUMN_NAME = "row_id"
TIMESTAMP_COLUMN_NAME = "inference_time"
EVENT_ID_COLUMN_NAME = "event_id"
OUTPUT_COLUMN_NAME = "output"

SAGEMAKER_DATACAPTURE_SPECIAL_COLUMN_NAMES = [
    DEFAULT_ID_COLUMN_NAME, TIMESTAMP_COLUMN_NAME, EVENT_ID_COLUMN_NAME,
    OUTPUT_COLUMN_NAME
]


def setup_monitoring(
    tru: TrueraWorkspace,
    datacapture_uri: str,
    credential_name: str,
    column_spec: ColumnSpec,
    *,
    cron_schedule: str = None,
    initial_split_time_range: TimeRange = None,
    column_data_types: Mapping[str, StaticDataTypeEnum] = None
) -> str:
    """Sets up scheduled ingestion of SageMaker data capture logs for production monitoring.

    Will first ingest the last hour (or `initial_split_time_range` if provided) as an initial ingestion.
    If successful, scheduled ingestion will be set up based on the `cron_schedule` (once per hour by default).

    Args:
        tru: TrueraWorkspace with project, data_collection, and model set
        datacapture_uri: URI of SageMaker data capture, s3a://<prefix>/<variant>
        credential_name: Name of the credential to assume when accessing S3. If one with the name does not exist, a new credential will be created if aws_access_key_id and aws_secret_access_key are provided.
        column_spec: ColumnSpec of SageMaker data capture
        cron_schedule (optional): Schedule to run ingestion. Defaults to "0 * * * *" (once per hour).
        initial_split_time_range (optional): TimeRange for the initial ingestion
        column_data_types (optional): Mapping of column names in column_spec to data types

    Returns:
        str: Workflow ID of the scheduled ingestion
    """
    tru.logger.info("Initializing split...")
    materialize_operation_id = ingest_logs_as_split(
        tru,
        split_name="prod",
        datacapture_uri=datacapture_uri,
        credential_name=credential_name,
        time_range=initial_split_time_range,
        column_spec=column_spec,
        column_data_types=column_data_types,
        split_type=PROD_DATA_SPLIT_TYPE
    )

    si_client = tru.current_tru.scheduled_ingestion_client
    schedule = _DEFAULT_SCHEDULE if cron_schedule is None else si_client.serialize_schedule(
        cron_schedule
    )
    workflow_id = si_client.schedule(
        project_id=tru.current_tru.project.id,
        template_operation_id=materialize_operation_id,
        schedule=schedule,
        append=True
    )
    tru.logger.info(
        f"SageMaker data ingestion scheduled with workflow id '{workflow_id}' and schedule '{schedule}'"
    )
    return workflow_id


def _augment_column_spec(
    tru: TrueraWorkspace, column_spec: ColumnSpec
) -> ColumnSpec:
    id_col_name = DEFAULT_ID_COLUMN_NAME
    if column_spec.id_col_name:
        tru.logger.info(
            f"Overriding default value '{DEFAULT_ID_COLUMN_NAME}' for SageMaker ColumnSpec `id_col_name` with '{column_spec.id_col_name}'."
        )
        id_col_name = column_spec.id_col_name

    timestamp_col_name = TIMESTAMP_COLUMN_NAME
    if column_spec.timestamp_col_name:
        tru.logger.info(
            f"Overriding default value '{TIMESTAMP_COLUMN_NAME}' for SageMaker ColumnSpec `timestamp_col_name` with '{column_spec.timestamp_col_name}''"
        )
        timestamp_col_name = column_spec.timestamp_col_name

    if column_spec.prediction_col_names:
        raise ValueError(
            f"Cannot override default value '{OUTPUT_COLUMN_NAME}' for SageMaker ColumnSpec `prediction_col_name` . Please omit from `column_spec`."
        )

    return ColumnSpec(
        id_col_name=id_col_name,
        timestamp_col_name=timestamp_col_name,
        pre_data_col_names=column_spec.pre_data_col_names,
        post_data_col_names=column_spec.post_data_col_names,
        prediction_col_names=OUTPUT_COLUMN_NAME,
        label_col_names=column_spec.label_col_names,
        extra_data_col_names=set(
            list(column_spec.extra_data_col_names) + [EVENT_ID_COLUMN_NAME]
        )
    )


def build_datacapture_load_request(
    column_details: List[ColumnDetails], s3_uri: str, credential_id: str,
    project_id: str, data_collection_id: str, file_time_range: TimeRange
) -> ds_pb.LoadDataRequest:
    data_format = ds_messages_pb.Format(
        file_type=ds_messages_pb.FT_SAGEMAKER_MONITORING_LOG,
        columns=column_details
    )
    load_data_info = ds_messages_pb.LoadDataInfo(
        project_id=project_id,
        data_collection_id=data_collection_id,
        describes_file_kind=DATA_KIND_ALL,
        creation_reason=ds_messages_pb.DS_CR_USER_REQUESTED,
        type=ds_messages_pb.DS_S3_BUCKET,
        uri=s3_uri,
        credential_id=credential_id,
        format=data_format,
        file_time_range=file_time_range
    )
    return ds_pb.LoadDataRequest(data_source_info=load_data_info)


def ingest_logs_as_split(
    tru: TrueraWorkspace,
    split_name: str,
    datacapture_uri: str,
    credential_name: str,
    column_spec: ColumnSpec,
    *,
    model_output_context: ModelOutputContext = None,
    time_range: TimeRange = None,
    asynchronous: bool = False,
    column_data_types: Mapping[str, StaticDataTypeEnum] = None,
    split_type: str = DEFAULT_SPLIT_TYPE,
) -> str:
    project_name = tru._ensure_project()
    data_collection_name = tru._ensure_data_collection()
    tru._ensure_model()

    split_exists = split_name in tru.remote_tru.artifact_interaction_client.get_all_datasplits_in_data_collection(
        project_name, data_collection_name, exclude_prod=False
    )

    project_id = tru.current_tru.project.id
    data_collection_id = tru.current_tru.data_collection.id

    column_spec = _augment_column_spec(tru, column_spec)
    credential_id = tru.get_credential_metadata(credential_name).id

    model_output_context = model_output_context or ModelOutputContext(
        model_name=tru._get_current_active_model_name(),
        score_type=tru._get_score_type()
    )

    column_details = get_column_details_for_parsing(
        tru, column_spec, column_data_types=column_data_types
    )

    time_range = time_range or get_default_time_range()

    ingestion_client = tru.get_ingestion_client()
    ds_communicator = ingestion_client._data_service_client.communicator

    # Load data
    # note that we cannot use scheduled ingestion as file_time_range will be overridden
    load_request = build_datacapture_load_request(
        column_details=column_details,
        s3_uri=datacapture_uri,
        credential_id=credential_id,
        project_id=project_id,
        data_collection_id=data_collection_id,
        file_time_range=time_range
    )
    rowset_id = ds_communicator.load_data_source(load_request).rowset_id

    # Materialize
    materialize_request = _build_materialize_request(
        tru.remote_tru,
        split_name=split_name,
        column_spec=column_spec,
        model_output_context=model_output_context,
        row_count=DEFAULT_APPROX_MAX_ROWS,
        split_already_exists=split_exists,
        split_type=split_type,
        rowset_id=rowset_id
    )
    materialize_operation_id = _submit_data_service_requests(
        tru.remote_tru, materialize_request=materialize_request
    )
    if not asynchronous:
        tru.logger.info("Waiting for ingestion to complete...")
        ingestion_client._wait_for_materialize_operation(
            materialize_operation_id=materialize_operation_id
        )
        tru.logger.info("Ingestion complete.")
    return materialize_operation_id


def get_default_time_range(delta_min=60, offset_min=0):
    """Returns time range spanning the previous hour. 
    Set delta_min to increase the window of time. Set offset_min to offset backwards in time."""
    now = Timestamp()
    now.GetCurrentTime()
    now.FromSeconds(now.ToSeconds() - offset_min * 60)
    start = Timestamp()
    start.FromSeconds(now.ToSeconds() - delta_min * 60)
    return TimeRange(begin=start, end=now)


def get_column_details_for_parsing(
    tru: TrueraWorkspace,
    column_spec: ColumnSpec,
    column_data_types: Mapping[str, StaticDataTypeEnum] = None
) -> List[ColumnDetails]:
    """Returns column details used for parsing SageMaker DataCapture files."""
    column_details = []
    columns_to_be_inferred = []
    if column_data_types is None:
        column_data_types = {}
    for column_name in column_spec.get_all_columns():
        if column_name in column_data_types:
            column_details.append(
                ColumnDetails(
                    name=column_name,
                    data_type=DataType(
                        static_data_type=column_data_types[column_name]
                    )
                )
            )
        elif column_name not in SAGEMAKER_DATACAPTURE_SPECIAL_COLUMN_NAMES:
            columns_to_be_inferred.append(column_name)
            column_details.append(ColumnDetails(name=column_name))
    if columns_to_be_inferred:
        tru.logger.info(
            f"Data type for column(s) {columns_to_be_inferred} will be inferred, since no specification was found in `column_data_types`"
        )
    return column_details
