from typing import Any, Dict, Optional, Sequence, Union

from google.protobuf.struct_pb2 import \
    ListValue  # pylint: disable=no-name-in-module
from google.protobuf.struct_pb2 import \
    NULL_VALUE  # pylint: disable=no-name-in-module
from google.protobuf.struct_pb2 import \
    Struct  # pylint: disable=no-name-in-module
from google.protobuf.struct_pb2 import \
    Value  # pylint: disable=no-name-in-module
from pydantic import BaseModel

from truera.protobuf.public.common import data_kind_pb2 as dk_pb
from truera.protobuf.public.common import ingestion_schema_pb2 as pb
from truera.protobuf.public.common import schema_pb2 as column_pb
from truera.protobuf.public.data_service import data_service_pb2 as ds_pb
from truera.protobuf.public.util import data_type_pb2 as dt_pb


class IntColumn(BaseModel):
    name: str


class BoolColumn(BaseModel):
    name: str


class FloatColumn(BaseModel):
    name: str


class StringColumn(BaseModel):
    name: str


class EmbeddingColumn(BaseModel):
    name: str


class TokensColumn(BaseModel):
    name: str


PrimitiveColumn = Union[IntColumn, BoolColumn, FloatColumn, StringColumn]
ArrayColumn = Union[EmbeddingColumn, TokensColumn]


class BinaryClassificationColumns(BaseModel):
    # should be 0 or 1
    label: IntColumn

    # should be in range [0, 1]
    probit_score: FloatColumn

    # should be 0 or 1
    class_score: Optional[IntColumn] = None
    logit_score: Optional[FloatColumn] = None


class RegressionColumns(BaseModel):
    label: FloatColumn
    regression_score: FloatColumn


class TabularInputColumns(BaseModel):
    pre_transformed_features: Sequence[PrimitiveColumn] = []
    post_transformed_features: Sequence[PrimitiveColumn] = []


class NLPInputColumns(BaseModel):
    embedding_column_name: Optional[str] = None
    tokens_column_name: Optional[str] = None


class Schema(BaseModel):
    id_column_name: str
    timestamp_column_name: str
    tags_column_name: str
    input_columns: Union[TabularInputColumns, NLPInputColumns]
    score_columns: Union[BinaryClassificationColumns, RegressionColumns]
    extra_columns: Optional[Sequence[PrimitiveColumn]] = []


def column_to_proto(column: Union[PrimitiveColumn, ArrayColumn]) -> pb.Column:
    if isinstance(column, BoolColumn):
        return pb.Column(type=pb.BOOL)
    if isinstance(column, FloatColumn):
        return pb.Column(type=pb.FLOAT)
    if isinstance(column, IntColumn):
        return pb.Column(type=pb.INT)
    if isinstance(column, StringColumn):
        return pb.Column(type=pb.STRING)
    if isinstance(column, EmbeddingColumn):
        return pb.Column(type=pb.EMBEDDING)
    if isinstance(column, TokensColumn):
        return pb.Column(type=pb.TOKENS)
    return pb.Column()


def column_to_column_details(
    column: Union[PrimitiveColumn, ArrayColumn]
) -> column_pb.ColumnDetails:
    #TODO: delete this once old schema is deprecated
    dt = None
    if isinstance(column, BoolColumn):
        dt = dt_pb.DataType(static_data_type=dt_pb.BOOL)
    elif isinstance(column, FloatColumn):
        dt = dt_pb.DataType(static_data_type=dt_pb.FLOAT64)
    elif isinstance(column, IntColumn):
        dt = dt_pb.DataType(static_data_type=dt_pb.INT64)
    elif isinstance(column, StringColumn):
        dt = dt_pb.DataType(static_data_type=dt_pb.STRING)
    elif isinstance(column, EmbeddingColumn):
        dt = dt_pb.DataType(
            array_type=dt_pb.ArrayType(
                data_type=dt_pb.DataType(static_data_type=dt_pb.FLOAT64)
            )
        )
    elif isinstance(column, TokensColumn):
        dt = dt_pb.DataType(
            array_type=dt_pb.ArrayType(
                data_type=dt_pb.DataType(static_data_type=dt_pb.STRING)
            )
        )
    return column_pb.ColumnDetails(name=column.name, data_type=dt)


def schema_to_proto(schema: Schema) -> pb.Schema:
    input_columns = {}
    post_data_columns = {}
    if isinstance(schema.input_columns, TabularInputColumns):
        if schema.input_columns.pre_transformed_features:
            input_columns = {
                c.name: column_to_proto(c)
                for c in schema.input_columns.pre_transformed_features
            }
        if schema.input_columns.post_transformed_features:
            post_data_columns = {
                c.name: column_to_proto(c)
                for c in schema.input_columns.post_transformed_features
            }
    elif isinstance(schema.input_columns, NLPInputColumns):
        if schema.input_columns.embedding_column_name:
            input_columns[schema.input_columns.embedding_column_name
                         ] = pb.Column(type=pb.EMBEDDING)
        if schema.input_columns.tokens_column_name:
            input_columns[schema.input_columns.tokens_column_name
                         ] = pb.Column(type=pb.TOKENS)

    output_columns = {}
    if isinstance(schema.score_columns, RegressionColumns):
        output_columns = {
            schema.score_columns.regression_score.name:
                pb.OutputColumn(output_type=pb.REGRESSION)
        }
    elif isinstance(schema.score_columns, BinaryClassificationColumns):
        if schema.score_columns.probit_score:
            output_columns[schema.score_columns.probit_score.name
                          ] = pb.OutputColumn(output_type=pb.PROBITS)
        if schema.score_columns.class_score:
            output_columns[schema.score_columns.class_score.name
                          ] = pb.OutputColumn(output_type=pb.CLASSIFICATION)
        if schema.score_columns.logit_score:
            output_columns[schema.score_columns.logit_score.name
                          ] = pb.OutputColumn(output_type=pb.LOGITS)

    label_columns = {}
    if schema.score_columns and schema.score_columns.label:
        label_columns = {
            schema.score_columns.label.name:
                column_to_proto(schema.score_columns.label)
        }
    if schema.extra_columns:
        extra_columns = {
            c.name: column_to_proto(c) for c in schema.extra_columns
        }
    else:
        extra_columns = {}

    return pb.Schema(
        id_column_name=schema.id_column_name,
        timestamp_column_name=schema.timestamp_column_name,
        tags_column_name=schema.tags_column_name,
        input_columns=input_columns,
        output_columns=output_columns,
        label_columns=label_columns,
        extra_columns=extra_columns,
        post_data_columns=post_data_columns
    )


def python_val_to_pb_value(python_value: Any) -> Value:
    """Turns the trulens_eval JSON into a protobuf struct.Value"""
    if python_value is None:
        return Value(null_value=NULL_VALUE)
    if isinstance(python_value, Value):
        return python_value
    if isinstance(python_value, bool):
        return Value(bool_value=python_value)
    if isinstance(python_value, int):
        return Value(number_value=python_value)
    if isinstance(python_value, float):
        return Value(number_value=python_value)
    if isinstance(python_value, str):
        return Value(string_value=python_value)
    if isinstance(python_value, Dict):
        s = Struct()
        for k, v in python_value.items():
            s.fields[str(k)].CopyFrom(python_val_to_pb_value(v))
        return Value(struct_value=s)
    if isinstance(python_value, Sequence):
        return Value(
            list_value=ListValue(
                values=[python_val_to_pb_value(v) for v in python_value]
            )
        )
    raise ValueError(
        f"Could not encode python type '{type(python_value)}' with value '{python_value}'"
    )


def schema_to_schemas_to_register(
    schema: Schema
) -> Sequence[ds_pb.SchemaToRegister]:
    #TODO: delete this once old schema is deprecated
    schemas_to_register = []
    if isinstance(schema.input_columns, TabularInputColumns):
        if schema.input_columns.pre_transformed_features:
            schemas_to_register.append(
                ds_pb.SchemaToRegister(
                    columns=[
                        column_to_column_details(c)
                        for c in schema.input_columns.pre_transformed_features
                    ],
                    data_kind=dk_pb.DATA_KIND_PRE
                )
            )
        if schema.input_columns.post_transformed_features:
            schemas_to_register.append(
                ds_pb.SchemaToRegister(
                    columns=[
                        column_to_column_details(c)
                        for c in schema.input_columns.post_transformed_features
                    ],
                    data_kind=dk_pb.DATA_KIND_POST
                )
            )
    elif isinstance(schema.input_columns, NLPInputColumns):
        if schema.input_columns.embedding_column_name:
            schemas_to_register.append(
                ds_pb.SchemaToRegister(
                    columns=[
                        column_to_column_details(
                            EmbeddingColumn(
                                name=schema.input_columns.embedding_column_name
                            )
                        )
                    ],
                    data_kind=dk_pb.DATA_KIND_PRE
                )
            )
        if schema.input_columns.tokens_column_name:
            schemas_to_register.append(
                ds_pb.SchemaToRegister(
                    columns=[
                        column_to_column_details(
                            TokensColumn(
                                name=schema.input_columns.tokens_column_name
                            )
                        )
                    ],
                    data_kind=dk_pb.DATA_KIND_PRE
                )
            )

    if isinstance(schema.score_columns, RegressionColumns):
        schemas_to_register.append(
            ds_pb.SchemaToRegister(
                columns=[
                    column_to_column_details(
                        schema.score_columns.regression_score
                    )
                ],
                data_kind=dk_pb.DATA_KIND_PREDICTIONS
            )
        )
    elif isinstance(schema.score_columns, BinaryClassificationColumns):
        schemas_to_register.append(
            ds_pb.SchemaToRegister(
                columns=[
                    column_to_column_details(c) for c in [
                        schema.score_columns.probit_score, schema.score_columns.
                        class_score, schema.score_columns.logit_score
                    ] if c is not None
                ],
                data_kind=dk_pb.DATA_KIND_PREDICTIONS
            )
        )

    if schema.score_columns and schema.score_columns.label:
        schemas_to_register.append(
            ds_pb.SchemaToRegister(
                columns=[column_to_column_details(schema.score_columns.label)],
                data_kind=dk_pb.DATA_KIND_LABEL
            )
        )

    if schema.extra_columns:
        schemas_to_register.append(
            ds_pb.SchemaToRegister(
                columns=[
                    column_to_column_details(c) for c in schema.extra_columns
                ],
                data_kind=dk_pb.DATA_KIND_EXTRA
            )
        )
    return schemas_to_register
