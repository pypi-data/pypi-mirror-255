# pylint: disable=no-name-in-module
from truera.protobuf.public.streaming.streaming_ingress_service_pb2 import \
    BulkPoint


def upload_event(
    workspace,
    project_id,
    data_collection_id,
    *,
    id,
    timestamp,
    model_id=None,
    split_id=None,
    score_type=None,
    options_hash=None,
    data=None,
    extra=None,
    label=None,
    prediction_score=None,
):
    if not prediction_score and not label and not data and not extra:
        raise ValueError("No data, pass in prediction, label, data, or extra")
    if prediction_score and not score_type:
        raise ValueError("score_type expected with prediction")
    workspace.remote_tru.streaming_ingress_client.ingest_point(
        project_id=project_id,
        data_collection_id=data_collection_id,
        id=id,
        timestamp=timestamp,
        split_id=split_id,
        model_id=model_id,
        data=data,
        extra=extra,
        label=label,
        score_type=score_type,
        options_hash=options_hash,
        prediction_score=prediction_score,
    )


def upload_events(
    workspace,
    project_id,
    data_collection_id,
    *,
    points,
    split_id=None,
    model_id=None,
    options_hash=None,
):
    formatted_points = []
    for i, point in enumerate(points):
        if not point.get("prediction_score") and not point.get(
            "label"
        ) and not point.get("data") and not point.get("extra"):
            raise ValueError(
                F"No data, pass in prediction, label, data, or extra (idx: {i})"
            )
        if point.get("prediction_score") and not point.get("score_type"):
            raise ValueError(F"score_type expected with prediction (idx: {i})")
        formatted_points.append(BulkPoint(**point),)
    workspace.remote_tru.streaming_ingress_client.ingest_bulk(
        project_id=project_id,
        data_collection_id=data_collection_id,
        split_id=split_id,
        model_id=model_id,
        options_hash=options_hash,
        points=formatted_points,
    )


def upload_generative_trace(
    workspace,
    trace_id,
    project_id,
    data_collection_id,
    split_id,
    model_id,
    prompt,
    cost,
):
    workspace.remote_tru.streaming_ingress_client.ingest_generative_trace(
        trace_id=trace_id,
        project_id=project_id,
        data_collection_id=data_collection_id,
        split_id=split_id,
        model_id=model_id,
        prompt=prompt,
        cost=cost,
    )


def upload_generative_feedback(
    workspace,
    trace_id,
    project_id,
    data_collection_id,
    split_id,
    model_id,
    feedback_result_id,
    feedback_function_id,
    feedback_result,
    cost,
):
    workspace.remote_tru.streaming_ingress_client.ingest_generative_feedback(
        trace_id=trace_id,
        project_id=project_id,
        data_collection_id=data_collection_id,
        split_id=split_id,
        model_id=model_id,
        feedback_result_id=feedback_result_id,
        feedback_function_id=feedback_function_id,
        feedback_result=feedback_result,
        cost=cost,
    )
