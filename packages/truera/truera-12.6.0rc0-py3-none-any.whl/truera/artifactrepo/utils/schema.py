from typing import Sequence

from truera.artifactrepo.utils.constants import SCHEMA_INPUT_COLUMN_LIMIT
from truera.protobuf.public.common.ingestion_schema_pb2 import Schema


def validate_data_collection_schema(schema: Schema) -> Sequence[ValueError]:
    """Returns list of validation errors of schema."""
    errors = []

    if len(schema.input_columns) > SCHEMA_INPUT_COLUMN_LIMIT:
        errors.append(
            ValueError(
                f"Number of input columns in data collection schema exceeds limit of {SCHEMA_INPUT_COLUMN_LIMIT}."
            )
        )
    return errors
