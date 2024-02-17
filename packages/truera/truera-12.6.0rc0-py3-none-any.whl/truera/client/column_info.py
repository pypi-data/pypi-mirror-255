from typing import Optional, Sequence

from truera.client.client_utils import \
    get_explanation_algorithm_type_from_string
from truera.client.client_utils import get_qoi_from_string
from truera.protobuf.public.common import schema_pb2 as schema_pb
from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb


def create_materialized_output_file(
    file_type: ds_messages_pb.MaterializedOutputFile.MaterializedFileType,
    *,
    column_names=[],
    skip_columns=[],
    upstream_input_rowset_id=""
) -> ds_messages_pb.MaterializedOutputFile:
    to_ret = ds_messages_pb.MaterializedOutputFile(
        type=file_type,
        columns=ds_messages_pb.ProjectionColumnCollection(),
        input_rowset_id=upstream_input_rowset_id
    )

    if column_names:
        for name in column_names:
            to_ret.columns.column_metadata.append(
                schema_pb.ColumnDetails(name=name)
            )
    else:
        for name in skip_columns:
            to_ret.columns.colummns_to_skip.append(name)

    return to_ret


def validate_column_input(column_input):
    if column_input is None:
        return None
    if not isinstance(column_input, (list, tuple, set, str)):
        raise TypeError(
            f"Invalid Column Input Type. Must provide sequence of column names or a single column name. Received input {column_input} of type {type(column_input)}"
        )
    return [column_input] if isinstance(column_input, str) else column_input


class ColumnInfo:

    def __init__(
        self,
        *,
        pre: Optional[Sequence[str]] = None,
        post: Optional[Sequence[str]] = None,
        label: Optional[Sequence[str]] = None,
        prediction: Optional[Sequence[str]] = None,
        feature_influences: Optional[Sequence[str]] = None,
        extra: Optional[Sequence[str]] = None,
        pre_skip: Optional[Sequence[str]] = None,
        post_skip: Optional[Sequence[str]] = None,
        extra_skip: Optional[Sequence[str]] = None,
        id_column: Optional[Sequence[str]] = None,
        ranking_item_id_column: Optional[Sequence[str]] = None,
        ranking_group_id_column: Optional[Sequence[str]] = None,
        tokens_column: Optional[Sequence[str]] = None,
        embeddings_column: Optional[Sequence[str]] = None,
        timestamp_column: Optional[Sequence[str]] = None,
        tags_column: Optional[str] = None,
    ):
        self.pre = validate_column_input(pre)
        self.pre_skip = validate_column_input(pre_skip)
        self.post = validate_column_input(post)
        self.post_skip = validate_column_input(post_skip)
        self.extra = validate_column_input(extra)
        self.extra_skip = validate_column_input(extra_skip)

        self.prediction = validate_column_input(prediction)
        self.feature_influences = validate_column_input(feature_influences)
        self.label = validate_column_input(label)
        self.id_column = validate_column_input(id_column)
        self.ranking_item_id_column = validate_column_input(
            ranking_item_id_column
        )
        self.ranking_group_id_column = validate_column_input(
            ranking_group_id_column
        )

        self.tokens_column = validate_column_input(tokens_column)
        self.embeddings_column = validate_column_input(embeddings_column)
        self.timestamp_column = validate_column_input(timestamp_column)
        self.tags_column = validate_column_input(tags_column)

    #pylint: disable=no-member
    def get_projections(
        self
    ) -> Sequence[ds_messages_pb.MaterializedOutputFile]:
        projections = []
        all_options = [
            self.pre, self.pre_skip, self.post, self.post_skip, self.extra,
            self.extra_skip, self.prediction, self.feature_influences,
            self.label
        ]
        all_not_set = all(not t for t in all_options)
        if self.prediction or self.tags_column or self.tokens_column or self.embeddings_column:
            projections.append(
                create_materialized_output_file(
                    ds_messages_pb.MaterializedOutputFile.MaterializedFileType.
                    MFT_PREDICTIONCACHE,
                    column_names=self.prediction or [],
                )
            )
        if self.pre or self.pre_skip or all_not_set:
            projections.append(
                create_materialized_output_file(
                    ds_messages_pb.MaterializedOutputFile.MaterializedFileType.
                    MFT_PRETRANSFORM,
                    column_names=self.pre or [],
                    skip_columns=self.pre_skip or []
                )
            )
        if self.post or self.post_skip:
            projections.append(
                create_materialized_output_file(
                    ds_messages_pb.MaterializedOutputFile.MaterializedFileType.
                    MFT_POSTTRANSFORM,
                    column_names=self.post or [],
                    skip_columns=self.post_skip or []
                )
            )
        if self.extra or self.extra_skip:
            projections.append(
                create_materialized_output_file(
                    ds_messages_pb.MaterializedOutputFile.MaterializedFileType.
                    MFT_EXTRA,
                    column_names=self.extra or [],
                    skip_columns=self.extra_skip or []
                )
            )
        if self.label:
            projections.append(
                create_materialized_output_file(
                    ds_messages_pb.MaterializedOutputFile.MaterializedFileType.
                    MFT_LABEL,
                    column_names=self.label
                )
            )

        if self.feature_influences:
            projections.append(
                create_materialized_output_file(
                    ds_messages_pb.MaterializedOutputFile.MaterializedFileType.
                    MFT_EXPLANATIONCACHE,
                    column_names=self.feature_influences
                )
            )

        return projections

    def get_system_column_details(self):
        # pylint: disable=unsubscriptable-object
        system_column_details = ds_messages_pb.SystemColumnDetails()
        sys_columns = {
            "id_column":
                system_column_details.id_columns,
            "ranking_item_id_column":
                system_column_details.ranking_item_id_column,
            "ranking_group_id_column":
                system_column_details.ranking_group_id_column,
            "timestamp_column":
                system_column_details.timestamp_column,
            "tokens_column":
                system_column_details.tokens_column,
            "embeddings_column":
                system_column_details.embeddings_column,
            "tags_column":
                system_column_details.tags_column
        }
        if not any(
            attr_name for attr_name in sys_columns if getattr(self, attr_name)
        ):
            return None

        for attr_name, sys_details in sys_columns.items():
            col_names = getattr(self, attr_name)
            if col_names and isinstance(col_names, Sequence):
                if len(col_names) > 1:
                    self.logger.warning(
                        f"Warning: more then one {col_names} are specified, only first will be used!"
                    )
                if isinstance(sys_details, Sequence):
                    sys_details.append(
                        schema_pb.ColumnDetails(name=col_names[0])
                    )
                else:
                    sys_details.CopyFrom(
                        schema_pb.ColumnDetails(name=col_names[0])
                    )
        return system_column_details

    def includes_cache(self):
        return self.prediction is not None or self.feature_influences is not None


class CreateCacheInfo:

    def __init__(
        self,
        model_id: str,
        *,
        score_type: Optional[str] = "",
        background_split_id: Optional[str] = "",
        explanation_algorithm_type: str = ""
    ):
        self.model_id = model_id
        self.score_type = score_type
        self.background_split_id = background_split_id
        self.explanation_algorithm_type = explanation_algorithm_type

    def build_create_cache_info(self) -> ds_messages_pb.CreateCacheInfo:
        create_cache_proto = ds_messages_pb.CreateCacheInfo(
            model_id=self.model_id
        )
        if self.score_type:
            create_cache_proto.score_type = get_qoi_from_string(self.score_type)

        if self.background_split_id:
            create_cache_proto.background_split_id = self.background_split_id

        if self.explanation_algorithm_type:
            create_cache_proto.explanation_algorithm_type = \
                get_explanation_algorithm_type_from_string(self.explanation_algorithm_type)
        return create_cache_proto
