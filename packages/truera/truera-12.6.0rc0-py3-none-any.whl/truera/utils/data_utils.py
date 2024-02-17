from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Generator, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

import truera.protobuf.public.aiq.intelligence_service_pb2 as is_pb
from truera.protobuf.public.qoi_pb2 import QuantityOfInterest
import truera.protobuf.public.util.elementary_types_pb2 as el_pb
from truera.utils.truera_status import TruEraInternalError

MAX_UNIQUE_VALS_FOR_CATEGORICAL_FEATURES = 5
MAX_CHUNK_SIZE_IN_BYTES = 4000000


@dataclass
class ClassificationParameters:
    classification_threshold: Optional[float] = None
    classification_qoi: QuantityOfInterest = QuantityOfInterest.UNKNOWN_QOI
    classification_score_type: Optional[is_pb.ModelThresholdScoreType.Type
                                       ] = None


def update_value_table_from_dataframe(
    df: pd.DataFrame, value_table: is_pb.ValueTable
):
    for col, col_dtype in df.dtypes.items():
        value_list = value_table.column_value_map[col]
        series = df[col]
        if len(series) > 0 and pd.api.types.is_list_like(series.iloc[0]):
            value_list.nested.values.extend(
                _extract_value_list_from_series(series).nested.values
            )
        elif pd.api.types.is_string_dtype(col_dtype):
            series = series.fillna("").astype(str)
            value_list.strings.values.extend(series.tolist())
        elif pd.api.types.is_integer_dtype(col_dtype):
            value_list.integers.values.extend(series.tolist())
        elif pd.api.types.is_numeric_dtype(col_dtype):
            value_list.floats.values.extend(series.tolist())
        else:
            raise TruEraInternalError(
                f"Could not find appropriate datatype to serialize column {col} of type {col_dtype}!"
            )
    try:
        #devnote: this will try to set the row_labels if index is there else just let it be without disrupting the flow
        index_list = df.index.tolist()
        value_table.row_labels.extend(index_list)
    except:
        pass


def _extract_value_list_from_series(
    list_of_elements: Union[pd.Series, list]
) -> el_pb.ValueList:
    if isinstance(list_of_elements, pd.Series):
        list_of_elements = list_of_elements.tolist()

    first_element = None
    first_element_dtype = str
    if list_of_elements:
        first_element = list_of_elements[0]
        first_element_dtype = type(first_element)

    inner_value_list = el_pb.ValueList()
    if (pd.api.types.is_integer_dtype(first_element_dtype)):
        inner_value_list.integers.values.extend(list_of_elements)
    elif (pd.api.types.is_float_dtype(first_element_dtype)):
        inner_value_list.floats.values.extend(list_of_elements)
    elif (first_element_dtype == str):
        inner_value_list.strings.values.extend(list_of_elements)
    elif (pd.api.types.is_list_like(first_element)):
        inner_values = [
            _extract_value_list_from_series(v) for v in list_of_elements
        ]
        inner_value_list.nested.values.extend(inner_values)
    else:
        raise ValueError("UNKNOWN TYPE: " + str(first_element_dtype))
    return inner_value_list


def update_float_table_from_dataframe(
    df: pd.DataFrame, float_table: is_pb.FloatTable
):
    for col in df.columns:
        float_list = float_table.column_value_map[col]
        float_list.values.extend(df[col].tolist())
    if df.index.name:
        float_table.row_labels.extend(df.index.tolist())


def update_string_table_from_dataframe(
    df: pd.DataFrame, string_table: is_pb.StringTable
):
    for col in df.columns:
        string_list = string_table.column_value_map[col]
        string_list.values.extend(df[col].tolist())
    if df.index.name:
        string_table.row_labels.extend(df.index.tolist())


def is_categorical_feature(
    feature_data: pd.Series,
    max_unique_vals_for_categorical_features:
    int = MAX_UNIQUE_VALS_FOR_CATEGORICAL_FEATURES
) -> bool:
    return (not pd.api.types.is_numeric_dtype(feature_data.dtype)) or (
        len(feature_data.unique()) <= max_unique_vals_for_categorical_features
    )


def value_table_to_df(
    value_table: is_pb.ValueTable,
    ordered_column_names: Optional[Sequence[str]] = None
):
    cvm = value_table.column_value_map
    cols = ordered_column_names if ordered_column_names else cvm.keys()
    mp = {col: get_list_from_value_list(cvm[col]) for col in cols}
    ret = pd.DataFrame(mp, columns=list(cols))
    row = value_table.row_labels
    if row:
        ret = ret.set_index(pd.Series(list(row)))
    return ret


def string_table_to_df(
    string_table: is_pb.StringTable,
    ordered_column_names: Optional[Sequence[str]] = None
):
    cvm = string_table.column_value_map
    cols = ordered_column_names if ordered_column_names else cvm.keys()
    mp = {col: list(cvm[col].values) for col in cols}
    ret = pd.DataFrame(mp, columns=list(cols))
    row = string_table.row_labels
    if row:
        ret = ret.set_index(pd.Series(list(row)))
    return ret


def value_table_to_df_or_series(
    value_table: is_pb.ValueTable,
    ordered_column_names: Optional[Sequence[str]] = None
):
    df = value_table_to_df(
        value_table, ordered_column_names=ordered_column_names
    )
    if df.shape[1] == 1:
        return df[df.columns[0]]
    return df


def float_table_to_df(float_table, ordered_column_names=None):
    cvm = float_table.column_value_map
    cols = ordered_column_names if ordered_column_names else cvm.keys()
    mp = {col: list(cvm[col].values) for col in cols}
    ret = pd.DataFrame(mp, columns=list(cols))
    row = float_table.row_labels
    if row:
        ret = ret.set_index(pd.Series(list(row)))
    return ret


def get_list_from_value_list(value_list):
    has_strings = hasattr(value_list,
                          "strings") and len(value_list.strings.values) > 0
    has_integers = hasattr(value_list,
                           "integers") and len(value_list.integers.values) > 0
    has_nested = hasattr(value_list,
                         "nested") and len(value_list.nested.values) > 0

    if has_integers:
        ret = value_list.integers.values
    elif has_strings:
        ret = value_list.strings.values
    elif has_nested:
        ret = [get_list_from_value_list(v) for v in value_list.nested.values]
    else:
        ret = value_list.floats.values
    return list(ret)


def merge_split_data_responses(
    responses: List[is_pb.SplitDataResponse]
) -> is_pb.SplitDataResponse:
    final_response = is_pb.SplitDataResponse()
    final_response.split_metadata.CopyFrom(responses[0].split_metadata)
    merge_value_tables(
        [resp.split_data for resp in responses], final_response.split_data
    )
    merge_value_tables(
        [resp.split_extra_data for resp in responses],
        final_response.split_extra_data
    )
    merge_value_tables(
        [resp.split_labels for resp in responses], final_response.split_labels
    )
    return final_response


def chunk_df(dataframe: pd.DataFrame) -> Generator[pd.DataFrame, None, None]:
    if dataframe is None or len(dataframe) == 0:
        return

    chunk_start_idx = 0
    chunk_bytes = 0
    for idx in range(len(dataframe)):
        row_bytes = sys.getsizeof(dataframe.iloc[idx])

        if row_bytes > MAX_CHUNK_SIZE_IN_BYTES:
            raise TruEraInternalError(
                "Dataframe single row size exceeds max chunk size"
            )
        elif chunk_bytes + row_bytes > MAX_CHUNK_SIZE_IN_BYTES:
            yield dataframe.iloc[chunk_start_idx:idx]
            chunk_start_idx = idx
            chunk_bytes = row_bytes
        else:
            chunk_bytes += row_bytes

    if chunk_start_idx < len(dataframe):
        yield dataframe.iloc[chunk_start_idx:]


def merge_value_tables(
    value_tables: List[is_pb.ValueTable], valueTable: is_pb.ValueTable
):
    value_tables_dfs = [value_table_to_df(table) for table in value_tables]
    merged_value_tables = pd.concat(value_tables_dfs)
    if not merged_value_tables.empty:
        update_value_table_from_dataframe(merged_value_tables, valueTable)


def drop_data_with_no_labels(xs, ys):
    y_label = ""
    if isinstance(ys, pd.DataFrame):
        if ys.shape[1] == 1:
            y_label = ys.columns[0]
        else:
            raise AssertionError("Too many columns in y dataframe.")
    else:
        y_label = "y"
        if isinstance(ys, pd.Series):
            ys = ys.to_frame(y_label)
        elif isinstance(ys, np.ndarray):
            ys = pd.DataFrame(ys, columns=[y_label])
        else:
            raise AssertionError("Unsupported data format")
    result = pd.concat([xs, ys], axis=1)
    result = result.dropna(subset=[y_label])
    Y = result[y_label]
    X = result
    X.drop(y_label, axis=1, inplace=True)
    return X, Y
