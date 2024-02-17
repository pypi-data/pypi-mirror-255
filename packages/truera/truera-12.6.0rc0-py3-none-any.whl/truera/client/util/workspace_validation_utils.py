from __future__ import annotations

import itertools
import logging
from typing import Any, Mapping, Optional, Sequence, TYPE_CHECKING, Union

import numpy as np
import pandas as pd

from truera.client.client_utils import get_input_data_format_from_string
from truera.client.client_utils import STR_TO_EXPLANATION_ALGORITHM_TYPE
from truera.client.public.communicator.http_communicator import \
    AlreadyExistsError
from truera.protobuf.public.aiq import intelligence_service_pb2 as is_pb
# pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.accuracy_pb2 import AccuracyType
from truera.protobuf.public.metadata_message_types_pb2 import \
    FEATURE_TRANSFORM_TYPE_MODEL_FUNCTION
from truera.protobuf.public.metadata_message_types_pb2 import \
    FEATURE_TRANSFORM_TYPE_NO_TRANSFORM
from truera.protobuf.public.metadata_message_types_pb2 import \
    FEATURE_TRANSFORM_TYPE_PRE_POST_DATA
from truera.protobuf.public.metadata_message_types_pb2 import \
    FeatureTransformationType
from truera.protobuf.public.metadata_message_types_pb2 import InputDataFormat
from truera.protobuf.public.qoi_pb2 import ExplanationAlgorithmType
# pylint: enable=no-name-in-module
from truera.protobuf.public.util import split_mode_pb2 as sm_pb
from truera.public.artifact_repo_lib import \
    ensure_valid_identifier as check_identifier
from truera.public.feature_influence_constants import \
    VALID_SCORE_TYPES_FOR_RANKING
import truera.public.feature_influence_constants as fi_constants
from truera.utils.data_constants import NORMALIZED_ID_COLUMN_NAME

if TYPE_CHECKING:
    from truera.client.ingestion_client import Table


def validate_influence_type_str_for_virtual_model_upload(
    provided_influence_type: Optional[str], project_influence_type: str
) -> ExplanationAlgorithmType:
    """Validates the influence type for a virtual model and returns enum of influence type.

    Args:
        provided_influence_type: influence type of influences to upload for virtual model.
        project_influence_type: influence type of project.

    Returns:
        ExplanationAlgorithmType: Validated influence type.
    """

    infl_types = list(STR_TO_EXPLANATION_ALGORITHM_TYPE.keys()) + ["shap"]
    shap_types = {k for k in infl_types if "shap" in k}
    use_shap = project_influence_type in shap_types

    # allow algorithm to be inferred if QII.
    if not use_shap and provided_influence_type is None:
        return ExplanationAlgorithmType.TRUERA_QII
    if provided_influence_type not in STR_TO_EXPLANATION_ALGORITHM_TYPE:
        raise ValueError(
            f"Expected `influence_type` to be one of {list(STR_TO_EXPLANATION_ALGORITHM_TYPE.keys())}, but got {provided_influence_type}!"
        )
    if use_shap and provided_influence_type not in shap_types:
        raise ValueError(
            f"Project influence type is set to 'shap', but provided influence type '{provided_influence_type}' is not a valid 'shap' influence. "
            f"Please provide influences with one of the following 'shap' influence types: {shap_types}.! "
            f"Alternatively, use `set_influence_type(\"{provided_influence_type}\")` to change the project influence type."
        )
    elif not use_shap and provided_influence_type in shap_types:
        raise ValueError(
            f"Influence type of project is set to {project_influence_type}, but provided influence type was '{provided_influence_type}'. "
            f"Please provide influences of type {project_influence_type}. "
            f"Alternatively, use `set_influence_type(\"{provided_influence_type}\")` to change the project influence type."
        )
    return STR_TO_EXPLANATION_ALGORITHM_TYPE[provided_influence_type]


def verify_label_values_for_classification(ys: Union[pd.Series, np.ndarray]):
    """Verify labels for classification (i.e. values must be in {0, 1}).

    Args:
        ys: labels.
    """
    if not np.isin(ys, [0, 1]).all():
        raise ValueError(
            "Classification models require label data to be binary!"
        )


def verify_label_values_for_regression(ys: Union[pd.Series, np.ndarray]):
    """Verify labels for regression (i.e. values must be numeric).

    Args:
        ys: labels.
    """
    if not pd.api.types.is_numeric_dtype(ys):
        raise ValueError("Regression models require label data to be numeric!")


def is_nlp_project(input_type: str) -> bool:
    """Check if provided `input_type` is for an NLP project.

    Args:
        input_type: Input type.

    Returns:
        bool: Whether `input_type` is for an NLP project.
    """
    return get_input_data_format_from_string(input_type) == InputDataFormat.TEXT


def is_rnn_project(input_type: str) -> bool:
    """Check if provided `input_type` is for an RNN project.

    Args:
        input_type: Input type.

    Returns:
        bool: Whether `input_type` is for an RNN project.
    """
    return get_input_data_format_from_string(
        input_type
    ) == InputDataFormat.TIME_SERIES_TABULAR


def is_nontabular_project(input_type: str) -> bool:
    """Check if provided `input_type` is for a non-tabular project.

    Args:
        input_type: Input type.

    Returns:
        bool: Whether `input_type` is for a non-tabular project.
    """
    return is_nlp_project(input_type) or is_rnn_project(input_type)


def is_tabular_project(input_type: str) -> bool:
    """Check if provided `input_type` is for a tabular project.

    Args:
        input_type: Input type.

    Returns:
        bool: Whether `input_type` is for a tabular project.
    """
    # legacy projects can have UNKNOWN input data types, so this safeguards against that.
    return not is_nontabular_project(input_type)


def _assert_dataframe_columns_are_strings(df: pd.DataFrame, df_name: str):
    for col in df.columns:
        if not isinstance(col, str):
            raise ValueError(
                f"Found column name {col} in `{df_name}` of type {type(col)} but expected `str`!"
            )


def _assert_is_dataframe(df: Any, df_name: str):
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"`{df_name}` must be of type `pandas.DataFrame`!")


def _assert_df_len(df: pd.DataFrame, df_name: str, expected_len: int):
    if len(df) != expected_len:
        raise ValueError(
            f"`{df_name}` must have {expected_len} rows but has {len(df)}!"
        )


def _assert_labels_are_single_dim(
    label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]],
    id_column_name: Optional[str]
):
    expected_label_cols = 1 + (1 if id_column_name is not None else 0)
    if label_data is not None and (
        label_data.ndim > expected_label_cols and
        label_data.shape[1] != expected_label_cols
    ):
        raise ValueError(
            f"`label_data` has {label_data.shape[1]} columns! Pass in a one-dimensional np.ndarray, a pd.Series or a single-column pd.DataFrame."
        )


def ensure_valid_identifier(artifact_name: str):
    """Ensure provided identifier is valid.

    Args:
        artifact_name: Proposed identifier.
    """
    check_identifier(
        to_check=artifact_name,
        context=None,
        ignore_empty=False,
        logger=None,
        raise_value_error=True
    )


def validate_split_against_data_collection_feature_transform(
    feature_transform_type: FeatureTransformationType,
    post_data: Optional[Union[pd.DataFrame, Table, str]] = None
):
    """Validate existance of provided post-transformed data against the feature transform type of the data-collection it will be added to.

    Args:
        feature_transform_type: Feature transform type of data-collection.
        post_data: Post-transformed data. Defaults to None.
    """
    if feature_transform_type == FEATURE_TRANSFORM_TYPE_PRE_POST_DATA and post_data is None:
        raise ValueError(
            "Cannot add a split without post data when feature transform is set to have pre-/post- transform data."
        )
    elif feature_transform_type in [
        FEATURE_TRANSFORM_TYPE_MODEL_FUNCTION,
        FEATURE_TRANSFORM_TYPE_NO_TRANSFORM
    ] and post_data is not None:
        raise ValueError(
            "Cannot add a split with post data when there is no feature transform or it is being done with a model transform function."
        )


def validate_model_threshold(
    threshold: Optional[float], score_type: str
) -> float:
    """Validate proposed model threshold for a proposed score type.

    Args:
        threshold: Proposed threshold.
        score_type: Proposed score type.

    Returns:
        float: Validated threshold (if threshold was `None`, then would correspond to 0.5 probability).
    """
    if score_type in ["regression", "ranking_score", "rank"]:
        return None
    if score_type == "probits" or score_type == "classification":
        if threshold is None:
            return 0.5
        if threshold > 1 or threshold < 0:
            raise ValueError(
                f"Thresholds for score type {score_type} must be between 0 and 1. Provided threshold: {threshold}"
            )
        return threshold
    if score_type == "logits":
        return 0 if threshold is None else threshold
    raise ValueError(
        f"Attempted to set threshold for unrecognized score type {score_type}."
    )


def is_feature_map_identity_transform(
    pre_to_post_feature_map: Optional[Mapping[str, Sequence[str]]]
) -> bool:
    """Check if provided feature map is the identity. If `None` this will be treated as the identity.

    Args:
        pre_to_post_feature_map: Feature map.

    Returns:
        bool: Whether the feature map is the identity or `None`.
    """
    if pre_to_post_feature_map is None:
        return True
    return all(
        len(v) == 1 and k == v[0] for k, v in pre_to_post_feature_map.items()
    )


def is_nontabular_influence_type(infl_type: str) -> bool:
    """Check if provided influence type is for nontabular projects.

    Args:
        infl_type: Influence type.

    Returns:
        bool: Whether the provided influence type is for nontabular projects.
    """
    return infl_type in set(["integrated-gradients", 'nlp-shap'])


def get_feature_transform_type_from_feature_map(
    pre_to_post_feature_map: Optional[Mapping[str, Sequence[str]]],
    provide_transform_with_model: Optional[bool]
) -> FeatureTransformationType:
    """Get the `FeatureTransformationType` corresponding to a data-collection with the provided feature map and transfrom providing mechanism.

    Args:
        pre_to_post_feature_map: Feature map of data-collection.
        provide_transform_with_model: Whether a transform for the data-collection will be provided by the model.

    Returns:
        FeatureTransformationType: The `FeatureTransformationType` corresponding to a data-collection with the provided feature map and transfrom providing mechanism.
    """
    if pre_to_post_feature_map:
        if provide_transform_with_model:
            return FEATURE_TRANSFORM_TYPE_MODEL_FUNCTION
        elif provide_transform_with_model == False:
            return FEATURE_TRANSFORM_TYPE_PRE_POST_DATA
        elif is_feature_map_identity_transform(
            pre_to_post_feature_map
        ) and provide_transform_with_model is None:
            return FEATURE_TRANSFORM_TYPE_NO_TRANSFORM
        else:
            raise ValueError(
                "Must use `provide_transform_with_model` to specify how feature mapping will be done in this data collection."
            )
    elif not provide_transform_with_model:
        return FEATURE_TRANSFORM_TYPE_NO_TRANSFORM
    else:
        raise ValueError(
            "Must specify `pre_to_post_feature_map` if transforms are provided with models!"
        )


def validate_split_with_feature_map(
    logger: logging.Logger, feature_map: Mapping[str, Sequence[str]],
    pre_data: pd.DataFrame, post_data: Optional[pd.DataFrame]
):
    """Validate the provided pre- and post-transformed data can work with the provided feature map.

    Args:
        logger: logger.
        feature_map: feature map.
        pre_data: pre-transformed data.
        post_data: post-transformed data.
    """
    pre_features_from_map = set(feature_map.keys())
    pre_features_from_data = set(pre_data.columns)
    post_features_from_map = set(
        itertools.chain.from_iterable(feature_map.values())
    )
    if pre_features_from_map != pre_features_from_data:
        missing_cols = sorted(
            list(pre_features_from_map - pre_features_from_data)
        )
        added_cols = sorted(
            list(pre_features_from_data - pre_features_from_map)
        )
        raise ValueError(
            f"`pre_data` does not match existing feature map! Missing columns: {missing_cols} \nAdditional columns: {added_cols}"
        )
    if post_features_from_map:
        if post_data is None:
            logger.warning(
                "Feature map detected, but post-transformed data is not provided with this split. Make sure that uploaded models contain a transform function to perform the feature mapping!"
            )
        else:
            post_features_from_data = set(post_data.columns)
            missing_cols = sorted(
                list(post_features_from_map - post_features_from_data)
            )
            added_cols = sorted(
                list(post_features_from_data - post_features_from_map)
            )
            if missing_cols or added_cols:
                raise ValueError(
                    f"`post_data` does not match existing feature map! Missing columns: {missing_cols} \nAdditional columns: {added_cols}"
                )


def validate_score_type(
    project_score_type: str, score_type: Optional[str] = None
):
    """Validate provided score type can work with a project with the provided score type.

    Args:
        project_score_type: project's score type.
        score_type: score type. Defaults to None.
    """
    if project_score_type == "classification" and score_type is None:
        raise ValueError(
            "`score_type` must be specified while adding prediction/feature influence data if project `score_type` is `classification`. It is strongly recommended to upload `probits`."
        )


def validate_ranking_ids(
    score_type: str, ranking_group_id_column_name: str,
    ranking_item_id_column_name: str
):
    if score_type in VALID_SCORE_TYPES_FOR_RANKING:
        if not ranking_group_id_column_name or not ranking_item_id_column_name:
            raise ValueError(
                "`ranking_group_id_column_name` and `ranking_item_id_column_name` must be set for ranking projects!"
            )
    else:
        if ranking_group_id_column_name or ranking_item_id_column_name:
            raise ValueError(
                "`ranking_group_id_column_name` and `ranking_item_id_column_name` must not be set for non-ranking projects!"
            )


def validate_split_for_dataframe(
    logger: logging.Logger,
    *,
    pre_data: Optional[pd.DataFrame],
    post_data: Optional[pd.DataFrame] = None,
    label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
    label_col_name: Optional[str] = None,
    extra_data_df: Optional[pd.DataFrame] = None,
    pre_to_post_feature_map: Optional[Mapping[str, Sequence[str]]] = None,
    output_type: str = "classification",
    id_column_name: Optional[str] = None,
    ranking_group_id_col_name: Optional[str] = None,
    ranking_item_id_col_name: Optional[str] = None,
    timestamp_col_name: Optional[str] = None,
    prediction_col_name: Optional[str] = None,
    input_type: Optional[str] = "tabular",
    split_mode=sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED,
    model_set_in_context: bool = False
):
    """Validate data-split creation parameters when using `pandas.DataFrame` to describe the data.

    Args:
        logger: logger.
        pre_data: pre-transformed data.
        post_data: post-transformed data. Defaults to None.
        label_data: labels if provided separately to `pre_data`. Defaults to None.
        label_col_name: column name in `pre_data` corresponding to labels. Defaults to None.
        extra_data_df: extra data. Defaults to None.
        pre_to_post_feature_map: feature map. Defaults to None.
        output_type: output type. Defaults to "classification".
        id_column_name: id column name. Defaults to None.
        ranking_group_id_column_name: ranking group id column name. Defaults to None.
        ranking_item_id_column_name: ranking item id column name. Defaults to None.
        timestamp_col_name: timestamp column name. Defaults to None.
        prediction_col_name: prediction column name. Defaults to None.
        input_type: input type. Defaults to "tabular".
        split_mode: split mode. Defaults to sm_pb.SplitMode.SPLIT_MODE_DATA_REQUIRED.
        model_set_in_context: Whether the `TrueraWorkspace` adding this data-split has a model set in context. Defaults to False.
    """
    # verify types and length of rows
    n_pre_data_records = None
    if pre_data is not None:
        if is_rnn_project(input_type):
            assert isinstance(
                pre_data, np.ndarray
            ), f"`pre_data` must be of type `pandas.DataFrame`!"
            n_pre_data_records = pre_data.shape[0] * pre_data.shape[1]
        else:
            n_pre_data_records = len(pre_data)
            _assert_is_dataframe(pre_data, "pre_data")
            _assert_dataframe_columns_are_strings(pre_data, "pre_data")

    if post_data is not None:
        _assert_is_dataframe(post_data, "post_data")
        _assert_dataframe_columns_are_strings(post_data, "post_data")
        if pre_data is not None:
            _assert_df_len(post_data, "post_data", n_pre_data_records)

    if split_mode != sm_pb.SplitMode.SPLIT_MODE_PREDS_REQUIRED:
        if label_data is not None and pre_data is not None:
            _assert_df_len(label_data, "label_data", n_pre_data_records)

    if extra_data_df is not None:
        _assert_dataframe_columns_are_strings(extra_data_df, "extra_data_df")
        if pre_data is not None:
            _assert_df_len(extra_data_df, "extra_data_df", n_pre_data_records)
        if NORMALIZED_ID_COLUMN_NAME in extra_data_df.columns:
            raise ValueError(
                f"extra_data_df cannot have column named \"{NORMALIZED_ID_COLUMN_NAME}\"!"
            )

    _assert_labels_are_single_dim(label_data, id_column_name)

    # verify presence of special cols
    if isinstance(pre_data, pd.DataFrame):
        # devnote: we could consider applying this check to tables too.
        pre_data_columns = pre_data.columns
        if id_column_name:
            if id_column_name not in pre_data_columns:
                raise ValueError(
                    f"Provided `id_column_name` \"{id_column_name}\" not found in `pre_data`!"
                )
            if post_data is not None and id_column_name not in post_data.columns:
                raise ValueError(
                    f"Provided `id_column_name` \"{id_column_name}\" not found in `post_data`!"
                )
            if label_data is not None:
                if not isinstance(label_data, pd.DataFrame):
                    raise ValueError(
                        f"Expected ID column {id_column_name} to be present in `label_data`, but found type {type(label_data)}! Pass in a pd.DataFrame with the ID column present."
                    )
                if id_column_name not in label_data.columns:
                    raise ValueError(
                        f"Provided `id_column_name` \"{id_column_name}\" not found in `label_data`!"
                    )
        if label_col_name and label_col_name not in pre_data_columns:
            raise ValueError(
                f"Provided `label_col_name` \"{label_col_name}\" not found in `pre_data`!"
            )
        if prediction_col_name:
            if prediction_col_name not in pre_data_columns:
                raise ValueError(
                    f"Provided `prediction_column_name` \"{prediction_col_name}\" not found in `pre_data`!"
                )
            if not model_set_in_context:
                raise ValueError(
                    "Must set model in workspace context prior to uploading predictions alongside a split!"
                )
        num_pre_cols = len(pre_data_columns) - bool(prediction_col_name) - bool(
            label_col_name
        ) - bool(id_column_name)
        if num_pre_cols <= 0 and split_mode != sm_pb.SplitMode.SPLIT_MODE_PREDS_REQUIRED:
            raise ValueError(
                "Provided `pre_data` DataFrame does not have any non-label or non-prediction columns!"
            )
    # verify against feature map
    if pre_to_post_feature_map:
        pre_data_dropping_cols = pre_data
        post_data_dropping_cols = post_data
        if id_column_name:
            pre_data_dropping_cols = pre_data_dropping_cols.drop(
                columns=[id_column_name]
            )
            if post_data_dropping_cols is not None:
                post_data_dropping_cols = post_data_dropping_cols.drop(
                    columns=[id_column_name]
                )
        system_cols = [
            ranking_group_id_col_name, ranking_group_id_col_name,
            timestamp_col_name
        ]
        system_cols = [col for col in system_cols if col is not None]
        if len(system_cols):
            pre_data_dropping_cols = pre_data_dropping_cols.drop(
                columns=system_cols
            )
        validate_split_with_feature_map(
            logger, pre_to_post_feature_map, pre_data_dropping_cols,
            post_data_dropping_cols
        )

    # verify label values
    if is_tabular_project(input_type):
        # NOTE: Tabular classification cannot be multiclass
        label_verification_fn = verify_label_values_for_classification if output_type == "classification" else verify_label_values_for_regression
        label_data_to_verify = label_data
        if label_col_name:
            label_data_to_verify = pre_data[label_col_name]
        elif isinstance(
            label_data, pd.DataFrame
        ) and id_column_name in label_data.columns:
            col_to_index = [
                c for c in label_data.columns if c != id_column_name
            ][0]
            label_data_to_verify = label_data_to_verify[col_to_index]
        elif isinstance(label_data,
                        pd.DataFrame) and len(label_data.columns) == 1:
            label_data_to_verify = label_data_to_verify[label_data.columns[0]]
        if label_data_to_verify is not None:
            label_verification_fn(label_data_to_verify)

    if isinstance(label_data, pd.DataFrame):
        _assert_dataframe_columns_are_strings(label_data, "label_data")
        if NORMALIZED_ID_COLUMN_NAME in label_data.columns:
            raise ValueError(
                f"`label_data` cannot have column named \"{NORMALIZED_ID_COLUMN_NAME}\"!"
            )

    if label_data is not None and extra_data_df is not None:
        if len(label_data) != len(extra_data_df):
            # This is just a stop-gap till we get things going with data layer.
            raise ValueError(
                "`label_data` and `extra_data_df` must have matching lengths!"
            )


def validate_feature_influence_algorithm_generic(algorithm: str):
    """Validate provided feature influence algorithm is valid.

    Args:
        algorithm: proposed feature influence algorithm.
    """
    if algorithm not in [
        "truera-qii", "shap", "integrated-gradients", "nlp-shap"
    ]:
        raise ValueError(
            f"`algorithm` must be one of {['truera-qii', 'shap']}, but given \"{algorithm}\"!"
        )


def validate_feature_influence_score_type(is_regression: bool, score_type: str):
    """Validate score type works for a project.

    Args:
        is_regression: Whether the project is a regression project.
        score_type: score type.
    """
    if score_type is None:
        return  # use default score type
    if is_regression:
        if score_type not in fi_constants.ALL_REGRESSION_SCORE_TYPES:
            raise ValueError(
                f"Invalid score type \"{score_type}\" was provided. Valid influence score types for this model: {fi_constants.ALL_REGRESSION_SCORE_TYPES}"
            )
        return
    if score_type not in fi_constants.ALL_CLASSIFICATION_SCORE_TYPES:
        raise ValueError(
            f"Invalid score type \"{score_type}\" was provided. Valid influence score types for this model: {fi_constants.ALL_CLASSIFICATION_SCORE_TYPES}"
        )


def validate_performance_metrics(
    performance_metrics: Sequence[str], valid_performance_metrics: Sequence[str]
) -> Sequence[AccuracyType.Type]:
    """Validate performance metrics and convert from strings to a list of `AccuracyType.Type`.

    Args:
        performance_metrics: Proposed performance metrics.
        valid_performance_metrics: Valid performance metrics.

    Returns:
        Sequence[AccuracyType.Type]: Provided performance metrics converted to a list of `AccuracyType.Type`.
    """
    ret = []
    for curr in performance_metrics:
        if curr not in valid_performance_metrics:
            raise ValueError(
                f"Metric {curr} not a valid performance metric! Must be one of {valid_performance_metrics}"
            )
        ret.append(AccuracyType.Type.Value(curr))
    return ret


def get_score_type_from_default(
    provided_score_type: Optional[str], default_score_type: str
) -> str:
    """Get score type given proposed score type and default score type.

    Args:
        provided_score_type: proposed score type.
        default_score_type: default score type.

    Returns:
        str: score type given proposed score type and default score type.
    """
    if not provided_score_type:
        return default_score_type

    for (project_type, valid_score_types) in [
        ("regression", fi_constants.VALID_SCORE_TYPES_FOR_REGRESSION),
        ("classification", fi_constants.VALID_SCORE_TYPES_FOR_CLASSIFICATION)
    ]:
        if default_score_type in valid_score_types and provided_score_type not in valid_score_types:
            raise ValueError(
                f"Cannot ingest predictions of score type {provided_score_type} for {project_type} project!"
            )
    return provided_score_type


def validate_add_data_split_generic(
    data_split_name: str,
    *,
    post_data: Optional[Union[pd.DataFrame, Table, str]] = None,
    label_data: Optional[Union[pd.DataFrame, pd.Series, np.ndarray]] = None,
    feature_influence_data: Optional[pd.DataFrame] = None,
    label_col_name: Optional[str] = None,
    background_split_name: Optional[str] = None,
    input_type: Optional[str] = None,
    data_splits: Optional[Sequence[str]] = None,
    feature_transform_type: Optional[FeatureTransformationType] = None,
    infl_type: Optional[str] = None
):
    """Validate `add_data_split` parameters.

    Args:
        data_split_name: proposed name.
        post_data: post-transformed data. Defaults to None.
        label_data: labels if provided separately to `pre_data`. Defaults to None.
        feature_influence_data: feature influence data. Defaults to None.
        label_col_name: column name in `pre_data` corresponding to labels. Defaults to None.
        split_type: split type. Defaults to "all".
        background_split_name: name of background data-split for any feature influences. Defaults to None.
        input_type: input type. Defaults to "tabular".
        data_splits: current data splits. Defaults to None.
        feature_transform_type: feature transform type. Defaults to None.
        infl_type: influence type. Defaults to None.
    """
    if data_split_name in data_splits:
        raise AlreadyExistsError(
            f"Data split \"{data_split_name}\" already exists!"
        )
    ensure_valid_identifier(data_split_name)
    if label_col_name and label_data is not None:
        raise ValueError(
            f"`label_data` and `label_col_name` both given, but at most one is allowed!"
        )

    if feature_influence_data is not None:
        if is_tabular_project(input_type
                             ) and is_nontabular_influence_type(infl_type):
            raise ValueError(
                f"{input_type.capitalize()} projects cannot use {infl_type}"
            )
        elif is_nontabular_influence_type(infl_type) and background_split_name:
            raise ValueError(
                f"Cannot have background_split_name for {infl_type}"
            )
        elif not is_nontabular_influence_type(
            infl_type
        ) and not background_split_name:
            raise ValueError(
                f"Must specify `background_split_name` for feature influence data"
            )
    if background_split_name:
        if background_split_name == data_split_name:
            raise ValueError(
                f"`background_split_name` cannot be same as `data_split_name`. Please ensure background split exists."
            )
        if background_split_name not in data_splits:
            raise ValueError(
                f"Background split \"{background_split_name}\" does not exist. Available splits: {data_splits}"
            )
    validate_split_against_data_collection_feature_transform(
        feature_transform_type, post_data=post_data
    )
