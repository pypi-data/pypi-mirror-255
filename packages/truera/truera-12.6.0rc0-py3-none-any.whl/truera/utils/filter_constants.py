from typing import Optional, Tuple

from truera.protobuf.public.qoi_pb2 import \
    QuantityOfInterest  # pylint: disable=no-name-in-module
from truera.public.feature_influence_constants import QOI_TO_SCORE_TYPE
from truera.public.feature_influence_constants import \
    VALID_SCORE_TYPES_FOR_CLASSIFICATION
from truera.public.feature_influence_constants import \
    VALID_SCORE_TYPES_FOR_RANKING
from truera.public.feature_influence_constants import \
    VALID_SCORE_TYPES_FOR_REGRESSION

FILTER_GROUND_TRUTH_NAME = "_DATA_GROUND_TRUTH"
FILTER_RANKING_GROUP_ID_NAME = "_RANKING_GROUP_ID"
FILTER_RANKING_GROUP_ID_PREFIX = f"{FILTER_RANKING_GROUP_ID_NAME}_"
FILTER_MODEL_PREFIX = "_MODEL_"
FILTER_PREFIX_LIST = [FILTER_RANKING_GROUP_ID_PREFIX, FILTER_MODEL_PREFIX]
CLASSIFICATION_SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES = {
    i: f"{FILTER_MODEL_PREFIX}{i.upper()}"
    for i in VALID_SCORE_TYPES_FOR_CLASSIFICATION
}
REGRESSION_SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES = {
    i: f"{FILTER_MODEL_PREFIX}{i.upper()}"
    for i in VALID_SCORE_TYPES_FOR_REGRESSION
}
RANKING_SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES = {
    i: f"{FILTER_MODEL_PREFIX}{i.upper()}"
    for i in VALID_SCORE_TYPES_FOR_RANKING
}
RANKING_SCORE_TYPES_TO_FILTER_RANKING_GROUP_ID_NAMES = {
    i: f"{FILTER_RANKING_GROUP_ID_PREFIX}{i.upper()}"
    for i in VALID_SCORE_TYPES_FOR_RANKING
}

SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES = {
    **CLASSIFICATION_SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES,
    **REGRESSION_SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES,
    **RANKING_SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES
}
SCORE_TYPES_TO_FILTER_RANKING_GROUP_ID_NAMES = {
    **RANKING_SCORE_TYPES_TO_FILTER_RANKING_GROUP_ID_NAMES
}

FILTER_MODEL_OUTPUT_NAMES_TO_SCORE_TYPES = {
    column_name: score_type for score_type, column_name in
    SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES.items()
}
FILTER_RANKING_GROUP_ID_NAMES_TO_SCORE_TYPES = {
    column_name: score_type for score_type, column_name in
    SCORE_TYPES_TO_FILTER_RANKING_GROUP_ID_NAMES.items()
}

GENERIC_MODEL_ID = "__GENERIC_MODEL_ID__"

MODEL_ID_SEPARATOR = '$'


def get_filter_column_name_for_model_output(
    qoi: QuantityOfInterest, model_id: Optional[str] = None
) -> str:
    score_type = QOI_TO_SCORE_TYPE[qoi]
    ret = SCORE_TYPES_TO_FILTER_MODEL_OUTPUT_NAMES[score_type]
    if model_id and model_id != GENERIC_MODEL_ID:
        ret += f"{MODEL_ID_SEPARATOR}{model_id}"
    return ret


def get_base_column_name_and_model_id_from_filter_column_name(
    filter_column_name: str
) -> Tuple[str, Optional[str]]:
    if not filter_column_name.startswith(FILTER_MODEL_PREFIX):
        return filter_column_name, None
    parsed_column_name = filter_column_name.split(MODEL_ID_SEPARATOR)
    if len(parsed_column_name) > 2:
        raise ValueError(
            f"Cannot parse `score_type` and `model_id` from filter_column_name: {filter_column_name}."
        )
    model_output_column_name = parsed_column_name[0]
    model_id = parsed_column_name[1] if len(parsed_column_name) == 2 else None
    return model_output_column_name, model_id if model_id else None
