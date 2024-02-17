from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
import logging
from typing import List, Optional, Sequence, Tuple, Union

import pandas as pd

from truera.protobuf.public.common import row_pb2 as row_pb
from truera.protobuf.queryservice import query_service_pb2 as qs_pb
from truera.utils.truera_status import TruEraInternalError

value_extractors = {
    "BYTE":
        lambda x: x.byte_value,
    "INT16":
        lambda x: x.short_value,
    "INT32":
        lambda x: x.int_value,
    "INT64":
        lambda x: x.long_value,
    "FLOAT":
        lambda x: x.float_value,
    "DOUBLE":
        lambda x: x.double_value,
    "STRING":
        lambda x: x.string_value,
    "BOOLEAN":
        lambda x: x.bool_value,
    "TIMESTAMP":
        lambda x: pd.Timestamp(x.timestamp_value.seconds, unit='s').
        to_datetime64()
}

dtype_conversion_dict = {
    "BYTE": "int8",
    "INT16": "int16",
    "INT32": "int32",
    "INT64": "int64",
    "FLOAT": "float32",
    "DOUBLE": "float64",
    "STRING": "str",
    "BOOLEAN": "bool",
    "TIMESTAMP": "datetime64[ns]"
}


class ArrayExtractor:

    def __init__(self, array_type: qs_pb.ArrayType):
        self.inner_extractor = self._get_inner_extractor(array_type.inner_type)

    def _get_inner_extractor(
        self, inner_type: qs_pb.ArrayType
    ) -> Union[ArrayExtractor, SimpleArrayValueExtractor]:
        member_set = inner_type.WhichOneof("type")
        if member_set == "value_type":
            return SimpleArrayValueExtractor()
        if member_set == "array_type":
            # Nested array case
            return ArrayExtractor(inner_type.array_type)
        raise ValueError("Unknown input type provided to array extractor.")

    def extract(self, v):
        extractor = self.get_values_from_array_value
        return extractor(v)

    def get_values_from_array_value(
        self, array_value: row_pb.ArrayValue
    ) -> List:
        member_set = array_value.WhichOneof("typed_array_value")
        if member_set == "float":
            return list(array_value.float.values)
        if member_set == "double":
            return list(array_value.double.values)
        if member_set == "int":
            return list(array_value.int.values)
        if member_set == "long":
            return list(array_value.long.values)
        if member_set == "string":
            return list(array_value.string.values)
        if member_set == "nested":
            return list(array_value.nested.values)
        raise ValueError(
            "Unknown member set on input array value: " + member_set
        )

    def get_extraction_lambda(self):
        return lambda x: [
            self.inner_extractor.extract(v)
            for v in self.get_values_from_array_value(x.array_value)
        ]


class SimpleArrayValueExtractor:

    def extract(self, v):
        return v


class RowMajorValueTableUtil:

    @classmethod
    def pb_stream_to_dataframe(
        cls, response_stream: Iterator[Union[qs_pb.QueryResponse,
                                             qs_pb.QueryItemResult]]
    ) -> pd.DataFrame:
        first_element = True
        dataframes = []
        extractors = None
        dtypes = None
        table_metadata = None

        for stream_element in response_stream:
            table = stream_element.row_major_value_table
            # only the first element contains the table's metadata
            if first_element:
                first_element = False
                extractors, dtypes, table_metadata = cls._process_metadata(
                    table, stream_element.request_id
                    if hasattr(stream_element, "request_id") else ""
                )
            # create a dataframe from single pb message/stream element
            df_data = [
                cls._extract_row_values(table_metadata, row, extractors)
                for row in table.rows
            ]
            dataframes.append(pd.DataFrame(df_data))

        if len(dataframes) == 0:
            return None

        # TODO(this_pr): Is this really the best place for this?
        dtypes = {
            k: v if v != "datetime64" else "datetime64[ns]"
            for k, v in dtypes.items()
        }
        return pd.concat(
            dataframes, ignore_index=True, copy=False
        ).astype(dtypes).rename(
            columns={tm.index: tm.name for tm in table_metadata}
        )

    @classmethod
    def row_major_value_table_to_df(cls, table):
        extractors, dtypes, table_metadata = cls._process_metadata(table, "")
        df_data = [
            cls._extract_row_values(table_metadata, row, extractors)
            for row in table.rows
        ]
        if len(df_data) == 0:
            return pd.DataFrame()
        return pd.DataFrame(df_data).astype(dtypes).rename(
            columns={tm.index: tm.name for tm in table_metadata}
        )

    @classmethod
    def _process_metadata(
        cls, table: qs_pb.QueryResponse.row_major_value_table, request_id: str
    ) -> Tuple[dict, dict, Sequence[qs_pb.ColumnMetadata]]:
        if len(table.metadata) == 0:
            raise TruEraInternalError(
                "table metadata is not available. request_id={}.".
                format(request_id)
            )
        return cls._value_extractors_for_response(
            table
        ), cls._dtypes_for_response(table), table.metadata

    @staticmethod
    def _extract_row_values(table_metadata, row, extractors) -> dict:
        row_dict = defaultdict()
        # Query service may filter out columns so the indexes from
        # column_metadata.index may not match row.columns
        # TODO: Validate ordering of row.columns and table_metadata line up
        # TODO: QS.processMetadata should order ColumnMetadata correctly
        if len(table_metadata) != len(row.columns):
            raise TruEraInternalError(
                "Number of columns in `row` does not match length of `table_metadata`."
            )

        for i, column_meta in enumerate(table_metadata):
            cell = row.columns[i]
            value_extractor = extractors.get(column_meta.index)
            value = value_extractor(cell)
            row_dict[column_meta.index] = value
        return row_dict

    # use qs_pb.ValueType and cls.value_extractors_dict to assign a value extractor to each column based on response metadata
    @classmethod
    def _value_extractors_for_response(
        cls, table: qs_pb.QueryResponse.row_major_value_table
    ) -> dict:
        return {
            column_meta.index: cls._get_extractor_for_type(column_meta)
            for column_meta in table.metadata
        }

    @classmethod
    def _get_extractor_for_type(cls, column_md: qs_pb.ColumnMetadata):
        member_set = column_md.WhichOneof("type_of_column")
        if member_set == "array_type":
            return ArrayExtractor(column_md.array_type).get_extraction_lambda()
        else:
            return value_extractors.get(qs_pb.ValueType.Name(column_md.type))

    # use qs_pb.ValueType and cls.dtypes_dict to get dtypes for the dataframe based on response metadata
    @classmethod
    def _dtypes_for_response(
        cls, table: qs_pb.QueryResponse.row_major_value_table
    ) -> dict:
        dtypes = {
            column_meta.index:
                dtype_conversion_dict.get(
                    qs_pb.ValueType.Name(column_meta.type)
                ) for column_meta in table.metadata
        }

        # Pandas gets confused if we ask it to change types to None
        return {
            key: value for key, value in dtypes.items() if value is not None
        }
