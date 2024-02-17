from typing import Any, List, Sequence, Tuple, Union

import pandas as pd

from truera.protobuf.public import common_pb2
from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyType  # pylint: disable=no-name-in-module
from truera.protobuf.public.qoi_pb2 import \
    ExplanationAlgorithmType  # pylint: disable=no-name-in-module
from truera.protobuf.queryservice import query_service_pb2 as qs_pb


def compute_inner_merge(
    data: Sequence[Union[pd.Series, pd.DataFrame]]
) -> Sequence[Union[pd.Series, pd.DataFrame]]:
    if len(data) <= 1:
        return data
    indexes = compute_index_intersection(data)
    return [curr.loc[indexes] for curr in data]


def compute_index_intersection(
    data: Sequence[Union[pd.Series, pd.DataFrame]]
) -> Sequence[Any]:
    ret = data[0].index
    for i in range(1, len(data)):
        ret = ret.intersection(data[i].index)
    return ret


QS_ACCURACIES = [
    AccuracyType.Type.LOG_LOSS, AccuracyType.Type.CLASSIFICATION_ACCURACY,
    AccuracyType.Type.PRECISION, AccuracyType.Type.RECALL, AccuracyType.Type.F1,
    AccuracyType.Type.TRUE_POSITIVE_RATE, AccuracyType.Type.TRUE_NEGATIVE_RATE,
    AccuracyType.Type.FALSE_POSITIVE_RATE,
    AccuracyType.Type.FALSE_NEGATIVE_RATE,
    AccuracyType.Type.NEGATIVE_PREDICTIVE_VALUE, AccuracyType.Type.RMSE,
    AccuracyType.Type.MSE, AccuracyType.Type.MAE, AccuracyType.Type.MSLE,
    AccuracyType.Type.R_SQUARED, AccuracyType.Type.MAPE,
    AccuracyType.Type.WMAPE, AccuracyType.Type.NDCG
]

QS_UDF_ACCURACIES = [
    AccuracyType.Type.AUC, AccuracyType.Type.GINI,
    AccuracyType.Type.ACCURACY_RATIO
]


def segregate_accuracies(
    accuracy_types: Sequence
) -> Tuple[List[str], List[str]]:
    qs_accuracies = []
    legacy_accuracies = []
    for accuracy_type in accuracy_types:
        if (accuracy_type
            in QS_ACCURACIES) or (accuracy_type in QS_UDF_ACCURACIES):
            qs_accuracies.append(accuracy_type)
        else:
            legacy_accuracies.append(accuracy_type)
    return legacy_accuracies, qs_accuracies


shap_algorithm_types = [
    ExplanationAlgorithmType.KERNEL_SHAP,
    ExplanationAlgorithmType.TREE_SHAP_INTERVENTIONAL,
    ExplanationAlgorithmType.TREE_SHAP_PATH_DEPENDENT,
    ExplanationAlgorithmType.NLP_SHAP
]

non_shap_algorithm_types = [
    ExplanationAlgorithmType.TRUERA_QII,
    ExplanationAlgorithmType.INTEGRATED_GRADIENTS
]

gradient_algorithm_types = [ExplanationAlgorithmType.INTEGRATED_GRADIENTS]

missing_preds_errors = [
    'data locator not found: dataKind=DATA_KIND_PREDICTIONS',
    'Score types not found'
]

QS_TO_UI_ERROR_MAP = {
    qs_pb.QueryItemResult.QueryError.NO_ERROR:
        {
            "code": common_pb2.ErrorCode.NO_ERROR,
            "msg": "no error"
        },
    qs_pb.QueryItemResult.QueryError.DATA_LOCATOR_NOT_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "data locator not found"
        },
    qs_pb.QueryItemResult.QueryError.MISSING_REQUIRED_DETAILS:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "missing required details"
        },
    qs_pb.QueryItemResult.QueryError.INVALID_OPERATION:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "invalid operation"
        },
    qs_pb.QueryItemResult.QueryError.INVALID_AGGREGATION:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "invalid aggregation"
        },
    qs_pb.QueryItemResult.QueryError.COLUMN_NOT_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "column not found"
        },
    qs_pb.QueryItemResult.QueryError.DATA_COLLECTION_NOT_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "data collection not found"
        },
    qs_pb.QueryItemResult.QueryError.INVALID_FILTER_EXPRESSION:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "invalid filter expression"
        },
    qs_pb.QueryItemResult.QueryError.MULTIPLE_DATA_LOCATORS_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "multiple data locators found"
        },
    qs_pb.QueryItemResult.QueryError.MULTIPLE_OPTION_HASH_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "multiple option hash found"
        },
    qs_pb.QueryItemResult.QueryError.OPTION_HASH_NOT_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "option hash not found"
        },
    qs_pb.QueryItemResult.QueryError.PREDICTION_SCORE_NOT_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "prediction score not found"
        },
    qs_pb.QueryItemResult.QueryError.SCHEMA_NOT_FOUND:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "schema not found"
        },
    qs_pb.QueryItemResult.QueryError.UNKNOWN_ERROR:
        {
            "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
            "msg": "unknown error from query service"
        }
}


def build_error(
    qs_error_code: qs_pb.QueryItemResult.QueryError,
    resp_entry_error: common_pb2.Error
):
    unknown_error_struct = {
        "code": common_pb2.ErrorCode.UNKNOWN_ERROR,
        "msg": "unknown error"
    }
    error_struct = QS_TO_UI_ERROR_MAP[
        qs_error_code
    ] if qs_error_code in QS_TO_UI_ERROR_MAP else unknown_error_struct
    resp_entry_error.error_code = error_struct["code"]
    resp_entry_error.error_msg = error_struct["msg"]
