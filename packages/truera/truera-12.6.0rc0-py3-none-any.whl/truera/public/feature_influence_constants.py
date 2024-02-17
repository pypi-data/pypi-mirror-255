from typing import Sequence

# pylint: disable=no-name-in-module
from truera.protobuf.public.model_output_type_pb2 import ModelOutputType
from truera.protobuf.public.qoi_pb2 import QuantityOfInterest

# pylint: enable=no-name-in-module

VALID_MODEL_OUTPUT_TYPES = [
    "classification", "regression", "ranking", "text_output"
]

PREDICTOR_SCORE_TYPE_REGRESSION = "regression"
PREDICTOR_SCORE_TYPE_RANK = "rank"
PREDICTOR_SCORE_TYPE_RANKING_SCORE = "ranking_score"
PREDICTOR_SCORE_TYPE_LOGITS = "logits"
PREDICTOR_SCORE_TYPE_PROBITS = "probits"
PREDICTOR_SCORE_TYPE_CLASSIFICATION = "classification"
PREDICTOR_SCORE_TYPE_LOG_LOSS = "log_loss"
PREDICTOR_SCORE_TYPE_MAE_CLASSIFICATION = "mean_absolute_error_for_classification"
PREDICTOR_SCORE_TYPE_MAE_REGRESSION = "mean_absolute_error_for_regression"
PREDICTOR_SCORE_TYPE_GENERATIVE_TEXT = "generative_text"
# For unittesting
PREDICTOR_SCORE_TYPE_LOGITS_UNNORM = "logits_unnormalized"

MODEL_ERROR_SCORE_TYPE_TO_MODEL_OUTPUT_SCORE_TYPE = {
    PREDICTOR_SCORE_TYPE_LOG_LOSS: PREDICTOR_SCORE_TYPE_PROBITS,
    PREDICTOR_SCORE_TYPE_MAE_CLASSIFICATION: PREDICTOR_SCORE_TYPE_PROBITS,
    PREDICTOR_SCORE_TYPE_MAE_REGRESSION: PREDICTOR_SCORE_TYPE_REGRESSION
}

MODEL_ERROR_SCORE_TYPES = set(
    MODEL_ERROR_SCORE_TYPE_TO_MODEL_OUTPUT_SCORE_TYPE.keys()
)

SCORE_TYPE_TO_MODEL_OUTPUT = {
    PREDICTOR_SCORE_TYPE_LOGITS:
        "logit_capped",
    PREDICTOR_SCORE_TYPE_PROBITS:
        "probability",
    PREDICTOR_SCORE_TYPE_CLASSIFICATION:
        "classification",
    PREDICTOR_SCORE_TYPE_LOGITS_UNNORM:
        "logit_unnorm",
    PREDICTOR_SCORE_TYPE_REGRESSION:
        "raw",
    PREDICTOR_SCORE_TYPE_LOG_LOSS:
        "log_loss",
    PREDICTOR_SCORE_TYPE_MAE_CLASSIFICATION:
        "mean_absolute_error_for_classification",
    PREDICTOR_SCORE_TYPE_MAE_REGRESSION:
        "mean_absolute_error_for_regression",
    PREDICTOR_SCORE_TYPE_RANK:
        "rank",
    PREDICTOR_SCORE_TYPE_RANKING_SCORE:
        "ranking_score",
    PREDICTOR_SCORE_TYPE_GENERATIVE_TEXT:
        "generative_text"
}

ALL_REGRESSION_SCORE_TYPES = [
    PREDICTOR_SCORE_TYPE_REGRESSION, PREDICTOR_SCORE_TYPE_MAE_REGRESSION
]
ALL_CLASSIFICATION_SCORE_TYPES = [
    PREDICTOR_SCORE_TYPE_PROBITS, PREDICTOR_SCORE_TYPE_LOGITS,
    PREDICTOR_SCORE_TYPE_CLASSIFICATION, PREDICTOR_SCORE_TYPE_LOG_LOSS,
    PREDICTOR_SCORE_TYPE_MAE_CLASSIFICATION
]
ALL_RANKING_SCORE_TYPES = [
    PREDICTOR_SCORE_TYPE_RANK, PREDICTOR_SCORE_TYPE_RANKING_SCORE
]
ALL_TEXT_OUTPUT_SCORE_TYPES = [PREDICTOR_SCORE_TYPE_GENERATIVE_TEXT]

ALL_CLASSIFICATION_QOI = [
    QuantityOfInterest.CLASSIFICATION_SCORE, QuantityOfInterest.PROBITS_SCORE,
    QuantityOfInterest.LOGITS_SCORE
]

VALID_SCORE_TYPES_FOR_REGRESSION = [PREDICTOR_SCORE_TYPE_REGRESSION]
VALID_SCORE_TYPES_FOR_CLASSIFICATION = [
    PREDICTOR_SCORE_TYPE_PROBITS,
    PREDICTOR_SCORE_TYPE_LOGITS,
    PREDICTOR_SCORE_TYPE_CLASSIFICATION,
]
VALID_SCORE_TYPES_FOR_RANKING = [
    PREDICTOR_SCORE_TYPE_RANK, PREDICTOR_SCORE_TYPE_RANKING_SCORE
]
VALID_SCORE_TYPES_FOR_TEXT_OUTPUT = [PREDICTOR_SCORE_TYPE_GENERATIVE_TEXT]

LOGIT_CLIP_RANGE = (-10, 10)

DEFAULT_RANKING_K = 10

QOI_TO_SCORE_TYPE = {
    QuantityOfInterest.PROBITS_SCORE:
        PREDICTOR_SCORE_TYPE_PROBITS,
    QuantityOfInterest.CLASSIFICATION_SCORE:
        PREDICTOR_SCORE_TYPE_CLASSIFICATION,
    QuantityOfInterest.LOGITS_SCORE:
        PREDICTOR_SCORE_TYPE_LOGITS,
    QuantityOfInterest.REGRESSION_SCORE:
        PREDICTOR_SCORE_TYPE_REGRESSION,
    QuantityOfInterest.LOG_LOSS:
        PREDICTOR_SCORE_TYPE_LOG_LOSS,
    QuantityOfInterest.MEAN_ABSOLUTE_ERROR_FOR_REGRESSION:
        PREDICTOR_SCORE_TYPE_MAE_REGRESSION,
    QuantityOfInterest.MEAN_ABSOLUTE_ERROR_FOR_CLASSIFICATION:
        PREDICTOR_SCORE_TYPE_MAE_CLASSIFICATION,
    QuantityOfInterest.RANK:
        PREDICTOR_SCORE_TYPE_RANK,
    QuantityOfInterest.RANKING_SCORE:
        PREDICTOR_SCORE_TYPE_RANKING_SCORE,
    QuantityOfInterest.GENERATIVE_TEXT:
        PREDICTOR_SCORE_TYPE_GENERATIVE_TEXT
}

OUTPUT_STR_TO_ENUM = {
    "classification": ModelOutputType.CLASSIFICATION,
    "regression": ModelOutputType.REGRESSION,
    "ranking": ModelOutputType.RANKING,
    "text_output": ModelOutputType.TEXT_OUTPUT
}

QOI_STR_TO_SCORE_TYPE = {
    QuantityOfInterest.Name(qoi): score_type
    for qoi, score_type in QOI_TO_SCORE_TYPE.items()
}

SCORE_TYPE_TO_QOI = {
    score_type: qoi for qoi, score_type in QOI_TO_SCORE_TYPE.items()
}


def get_output_type_from_score_type(score_type: str) -> str:
    if score_type in VALID_SCORE_TYPES_FOR_CLASSIFICATION:
        return "classification"
    elif score_type in VALID_SCORE_TYPES_FOR_REGRESSION:
        return "regression"
    elif score_type in VALID_SCORE_TYPES_FOR_RANKING:
        return "ranking"
    elif score_type in VALID_SCORE_TYPES_FOR_TEXT_OUTPUT:
        return "text_output"
    else:
        raise ValueError(f"Score type \"{score_type}\" not recognized!")


def get_valid_score_type_for_output_type(output_type: str) -> Sequence[str]:
    if output_type == "classification":
        return VALID_SCORE_TYPES_FOR_CLASSIFICATION.copy()
    elif output_type == "regression":
        return VALID_SCORE_TYPES_FOR_REGRESSION.copy()
    elif output_type == "ranking":
        return VALID_SCORE_TYPES_FOR_RANKING.copy()
    elif output_type == "generative_text":
        return VALID_SCORE_TYPES_FOR_TEXT_OUTPUT.copy()
    else:
        raise ValueError(f"Output type \"{output_type}\" not recognized!")


def infer_error_score_type_from_output_type(output_type: str) -> str:
    if output_type == "classification":
        return PREDICTOR_SCORE_TYPE_MAE_CLASSIFICATION
    elif output_type == "regression":
        return PREDICTOR_SCORE_TYPE_MAE_REGRESSION
    raise ValueError(
        f"Could not infer error score type for output type \"{output_type}\"!"
    )


def is_regression_score_type(score_type: str) -> bool:
    return get_output_type_from_score_type(score_type) == "regression"


def is_classification_score_type(score_type: str) -> bool:
    return get_output_type_from_score_type(score_type) == "classification"


def is_ranking_score_type(score_type: str) -> bool:
    return get_output_type_from_score_type(score_type) == "ranking"
