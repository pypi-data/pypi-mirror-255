from cachetools.keys import hashkey

from truera.authn.usercontext import RequestContext
from truera.protobuf.public.data.segment_pb2 import \
    SegmentID  # pylint: disable=no-name-in-module
from truera.utils.cache_utils import get_or_create_request_id


def performance_metric_cache_key(
    _self,
    request_context: RequestContext,
    project_id: str,
    model_id: str,
    data_split_id: str,
    metric_type: str,
    segment_id_proto: SegmentID,
):
    request_id = get_or_create_request_id(request_context)
    return hashkey(
        request_id, project_id, model_id, data_split_id, metric_type,
        segment_id_proto.segmentation_id, segment_id_proto.segment_name
    )


def stability_metric_cache_key(
    _self,
    request_context: RequestContext,
    project_id: str,
    model_id: str,
    data_split_id: str,
    reference_data_split_id: str,
    distance_type: str,
    segment_id_proto: SegmentID,
):
    request_id = get_or_create_request_id(request_context)
    return hashkey(
        request_id, project_id, model_id, data_split_id,
        reference_data_split_id, distance_type,
        segment_id_proto.segmentation_id, segment_id_proto.segment_name
    )


def fairness_metric_cache_key(
    _self,
    request_context: RequestContext,
    project_id: str,
    model_id: str,
    data_split_id: str,
    bias_type: str,
    segment_id_protected_proto: SegmentID,
    segment_id_comparison_proto: SegmentID,
):
    request_id = get_or_create_request_id(request_context)
    return hashkey(
        request_id, project_id, model_id, data_split_id, bias_type,
        segment_id_protected_proto.segmentation_id,
        segment_id_protected_proto.segment_name,
        segment_id_comparison_proto.segmentation_id,
        segment_id_comparison_proto.segment_name
    )


def feature_importance_cache_key(
    _self, request_ctx: RequestContext, project_id: str, model_id: str,
    data_split_id: str, score_type: str, segment_id_proto: SegmentID,
    background_split_id: str
):
    request_id = get_or_create_request_id(request_ctx)
    return hashkey(
        request_id, project_id, model_id, data_split_id, score_type,
        segment_id_proto.segmentation_id, segment_id_proto.segment_name,
        background_split_id
    )
