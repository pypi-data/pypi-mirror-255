from logging import Logger
from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
import pandas as pd

from truera.client.column_info import validate_column_input
from truera.client.util import workspace_validation_utils
# pylint: disable=no-name-in-module,no-member
from truera.protobuf.public import metadata_message_types_pb2 as md_pb

# pylint: enable=no-name-in-module
if TYPE_CHECKING:
    from truera.client.ingestion import ModelOutputContext
    from truera.client.ingestion.util import BaseColumnSpec

from truera.client.ingestion.constants import DEFAULT_MAX_EMBEDDINGS_LENGTH
from truera.client.ingestion.constants import DEFAULT_MAX_TOKEN_LENGTH
from truera.client.ingestion.constants import PROD_DATA_SPLIT_TYPE
from truera.client.ingestion.constants import SPECIAL_COLUMN_NAMES


def validate_column_spec_and_model_output_context(
    column_spec: 'BaseColumnSpec',
    model_output_context: Optional['ModelOutputContext'], *, split_name: str,
    existing_models: Sequence[str], existing_splits: Sequence[str],
    project_influence_type: str, is_production_data: bool
):
    column_info = column_spec.to_column_info()

    # Validate columns
    if not column_spec.id_col_name:
        raise ValueError("`id_col_name` is required in `column_spec`.")
    for column_type, column_names in column_spec.to_dict().items():
        if column_names:
            for column_name in validate_column_input(column_names):
                if column_name in SPECIAL_COLUMN_NAMES:
                    raise ValueError(
                        f"Column name '{column_name}' from `{column_type}` can not be used as it is reserved for use by TruEra services."
                    )

    # Validate uniqueness of system columns
    system_cols = [
        column_info.id_column, column_info.ranking_item_id_column,
        column_info.ranking_group_id_column, column_info.tags_column,
        column_info.timestamp_column
    ]
    col_tuples = [
        (column_info.pre, "pre_data_col_names"),
        (column_info.post, "post_data_col_names"),
        (column_info.prediction, "prediction_col_names"),
        (column_info.label, "label_col_names"),
        (column_info.feature_influences, "feature_influence_col_names"),
        (column_info.extra, "extra_col_names")
    ]
    for col_names, data_type_str in col_tuples:
        if col_names is not None:
            for system_col in system_cols:
                if system_col is not None:
                    check = system_col in col_names if type(
                        system_col
                    ) is str else len(
                        set.intersection(set(system_col), set(col_names))
                    ) > 0
                    if check:
                        if type(system_col) is str:
                            system_col_str = f"'{system_col}'"
                        else:
                            duplicate_cols = list(
                                set.intersection(
                                    set(system_col), set(col_names)
                                )
                            )
                            system_col_str = ", ".join(
                                [f"'{col}'" for col in duplicate_cols]
                            )
                        raise ValueError(
                            f"System column(s) {system_col_str} provided in {data_type_str}! This will cause ambiguity during ingestion."
                        )

    # Validate appending data
    is_appending = split_name in existing_splits and (
        column_info.pre or column_info.post
    )
    if is_appending and not is_production_data:
        raise ValueError(
            f"Data split '{split_name}' already exists. Appending data is supported only for production monitoring data splits created by add_production_data."
        )

    # Validate model exists
    if model_output_context and model_output_context.model_name and model_output_context.model_name not in existing_models:
        raise ValueError(
            f"Model '{model_output_context.model_name}' does not exist among available models: {existing_models}"
        )

    # Validate production data
    if is_production_data:
        if not column_info.timestamp_column:
            raise ValueError(
                "Production monitoring data requires `timestamp_col_name` in `column_spec`."
            )
        if column_info.label:
            # Labels require model_id in production data
            if not model_output_context or not model_output_context.model_name:
                raise ValueError(
                    "Labels need to be associated with a model for production data. Please supply `model_name` in `model_output_context` or set a model in current workspace context."
                )

    # Validate model_output_context
    if column_info.prediction or column_info.feature_influences:
        if not model_output_context:
            raise ValueError(
                "`model_output_context` is required when ingesting predictions or feature influences."
            )

        # Validate model_name exists
        if not model_output_context.model_name:
            raise ValueError(
                "`model_name` is required in model output context when ingesting predictions or feature influences."
            )

        # Validate score_type exists
        if not model_output_context.score_type:
            raise ValueError(
                f"`score_type` is required in model output context when ingesting predictions or feature influences."
            )

        if column_info.feature_influences:
            if not workspace_validation_utils.is_nontabular_influence_type(
                model_output_context.influence_type
            ):
                # Validate background_split_name
                if not model_output_context.background_split_name:
                    raise ValueError(
                        "`background_split_name` is required in model output context when ingesting feature influences."
                    )
                if model_output_context.background_split_name not in existing_splits:
                    raise ValueError(
                        f"Data split '{model_output_context.background_split_name}' does not exist among available splits: {existing_splits}"
                    )

            # Validate influence_type
            if not model_output_context.influence_type:
                raise ValueError(
                    "`influence_type` is required in model output context when ingesting feature influences."
                )
            workspace_validation_utils.validate_influence_type_str_for_virtual_model_upload(
                model_output_context.influence_type, project_influence_type
            )

    # Validate tokens and embeddings
    if column_info.tokens_column or column_info.embeddings_column:
        if not column_info.prediction:
            raise ValueError(
                "`prediction_col_name` is required in `NLPColumnSpec` when ingesting tokens or embeddings."
            )


def validate_tokens(tokens: pd.Series, logger: Optional[Logger] = None):
    lengths = tokens.map(len)
    tokens = tokens.map(lambda x: list(x))
    if logger is not None and not lengths.map(
        lambda x: x < DEFAULT_MAX_TOKEN_LENGTH
    ).all():
        logger.warning(
            f"Got tokens length of {lengths.max()} exceeds default limit of {DEFAULT_MAX_TOKEN_LENGTH}. This may result in performance issues."
        )
    if not tokens.map(lambda x: len(np.array(x).shape) == 1).all():
        raise ValueError(
            f"Tokens for each record must be a 1-dimensional array."
        )
    if not tokens.map(
        lambda x: np.issubdtype(np.array(x).dtype, "U") or np.
        issubdtype(np.array(x).dtype, "S")
    ).all():
        raise ValueError(f"Tokens for each record must be string types.")


def validate_embeddings(embeddings: pd.Series, logger: Optional[Logger] = None):
    lengths = embeddings.map(len)
    if len(lengths.unique()) > 1:
        raise ValueError(
            f"Embeddings must be of the same length, but got lengths: {lengths.unique().tolist()}."
        )
    if logger is not None and lengths.unique(
    )[0] > DEFAULT_MAX_EMBEDDINGS_LENGTH:
        logger.warning(
            f"Embeddings length of {lengths.unique()[0]} exceeds default limit of {DEFAULT_MAX_EMBEDDINGS_LENGTH}. This may result in performance issues."
        )
    if not embeddings.map(lambda x: len(np.array(x).shape) == 1).all():
        raise ValueError(
            f"Embeddings for each record must be a 1-dimensional array."
        )
    if not embeddings.map(
        lambda x: np.issubdtype(np.array(x).dtype, np.integer) or np.
        issubdtype(np.array(x).dtype, np.floating)
    ).all():
        raise ValueError(f"Embeddings for each record must be numeric.")


def validate_dataframe(
    data: pd.DataFrame,
    column_spec: 'BaseColumnSpec',
    input_type: str,
    logger: Optional[Logger] = None
):
    # Validate data against columns
    for column_type, column_names in column_spec.to_dict().items():
        if column_names:
            for column_name in validate_column_input(column_names):
                if column_name not in data:
                    raise ValueError(
                        f"Column name '{column_name}' was provided though `{column_type}`, but not found in data."
                    )
    if logger is not None:
        column_spec_columns = column_spec.get_all_columns()
        for column in data.columns:
            if column not in column_spec_columns:
                logger.warning(
                    f"Column '{column}' found in `data`, but will be ignored as it is not specified in `column_spec`."
                )

    # Validate id column is string
    try:
        data[column_spec.id_col_name].astype("string")
    except Exception as exc:
        raise ValueError(
            f"`id_col_name` '{column_spec.id_col_name}' column must be convertible into string type. Could not convert column to string; error: {exc}"
        )

    # Validate timestamp is datetime
    if column_spec.timestamp_col_name:
        try:
            pd.to_datetime(data[column_spec.timestamp_col_name])
        except Exception as exc:
            raise ValueError(
                f"`timestamp_col_name` column '{column_spec.timestamp_col_name}' must have valid datetime format. Could not convert column to datetime; "
                f"error: {exc}"
            )

    column_info = column_spec.to_column_info()
    if column_info.tokens_column:
        tokens_column = column_info.tokens_column[0]
        if input_type != "text":
            raise ValueError(
                f"`tokens_col_name` '{tokens_column}' is only supported for text input."
            )
        validate_tokens(data[tokens_column], logger=logger)
    if column_info.embeddings_column:
        embeddings_column = column_info.embeddings_column[0]
        if input_type != "text":
            raise ValueError(
                f"`sentence_embeddings_col_name` '{embeddings_column}' is only supported for text input."
            )
        validate_embeddings(data[embeddings_column], logger=logger)

    if column_info.tokens_column and column_info.feature_influences:
        tokens_column = column_info.tokens_column[0]
        influence_column = column_info.feature_influences[0]
        if (
            data[tokens_column].map(len)
            != data[influence_column].map(lambda x: len(x[0]))
        ).any():
            raise ValueError(
                f"feature_influence_col_names` '{influence_column}' shapes do not match `tokens_col_name` '{tokens_column}' sequence lengths. \
                Each value in '{influence_column}' must be of shape (`n_classes`, `sequence_length`) and each value in '{tokens_column}' must be of length (`sequence_length`)."
            )

    # Validate feature influence columns for non-NLP ColumnSpec
    if column_info.feature_influences:
        for col_name in column_info.feature_influences:
            if workspace_validation_utils.is_tabular_project(input_type):
                if not pd.api.types.is_float_dtype(data[col_name].dtype):
                    raise ValueError(
                        f"`feature_influence_data` column '{col_name}' must have float dtype, but was '{data[col_name].dtype}'"
                    )
            elif workspace_validation_utils.is_nlp_project(input_type):
                if data[col_name].apply(
                    lambda x: not (
                        pd.api.types.is_array_like(x) or
                        isinstance(x, Sequence)
                    )
                ).any():
                    raise ValueError(
                        f"`feature_influence_data` column '{col_name}' must contain only array-like elements"
                    )
            else:
                raise ValueError(f"Invalid `input_type` specified {input_type}")
