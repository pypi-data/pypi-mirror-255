from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import asdict
from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple, Union

import pandas as pd

from truera.client.client_utils import get_string_from_qoi_string
from truera.client.column_info import ColumnInfo
from truera.client.column_info import CreateCacheInfo
from truera.client.ingestion.constants import \
    FEATURE_INFLUENCE_SUFFIX_TRUERA_QII
from truera.client.util import workspace_validation_utils
from truera.client.util.workspace_validation_utils import \
    is_nontabular_influence_type
from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb


@dataclass(eq=True, frozen=True)
class BaseColumnSpec(ABC):
    '''Parameter data class mapping column names to data kinds

    Args:
        id_col_name: Name of the id column
        timestamp_col_name: Name of the timestamp column
        tags_col_name: Name of tags column
        extra_data_col_names: Name(s) of extra data column(s)
    '''
    id_col_name: str
    ranking_item_id_column_name: str = None
    ranking_group_id_column_name: str = None
    timestamp_col_name: str = None
    tags_col_name: str = None
    extra_data_col_names: Sequence[str] = tuple()

    def copy(self, **kwargs):
        kwargs = {**self.to_dict(), **kwargs}
        return self.__class__(**kwargs)

    @classmethod
    def valid_types(cls) -> Sequence[BaseColumnSpec]:
        return [ColumnSpec, NLPColumnSpec]

    @abstractmethod
    def _column_info_mapping(self) -> Dict[str, Union[tuple, str]]:
        return dict(
            id_column=self.id_col_name,
            ranking_item_id_column=self.ranking_item_id_column_name,
            ranking_group_id_column=self.ranking_group_id_column_name,
            timestamp_column=self.timestamp_col_name,
            tags_column=self.tags_col_name,
            extra=self.extra_data_col_names
        )

    def to_column_info(self) -> ColumnInfo:
        return ColumnInfo(**self._column_info_mapping())

    def to_dict(self) -> dict:
        return asdict(self)

    def get_all_columns(self) -> Sequence[str]:
        all_col_names = []
        for col_names in self.to_dict().values():
            if col_names:
                all_col_names.extend(
                    [col_names] if isinstance(col_names, str) else col_names
                )
        return list(set(all_col_names))

    def __getitem__(self, item):
        return self.to_dict()[item]

    def __contains__(self, item):
        return item in self.to_dict()


@dataclass(eq=True, frozen=True)
class ColumnSpec(BaseColumnSpec):
    '''Parameter data class mapping column names to data kinds

    Args:
        pre_data_col_names: Name(s) of pre-transform data column(s)
        post_data_col_names: Name(s) of post-transform data column(s)
        prediction_col_names: Name(s) of prediction column(s)
        label_col_names: Name(s) of ground truth label column(s)
        feature_influence_col_names: Name(s) of feature influences column(s)
    '''
    pre_data_col_names: Sequence[str] = tuple()
    post_data_col_names: Sequence[str] = tuple()
    prediction_col_names: Sequence[str] = tuple()
    label_col_names: Sequence[str] = tuple()
    feature_influence_col_names: Sequence[str] = tuple()

    def _column_info_mapping(self) -> Dict[str, Union[tuple, str]]:
        column_info_mapping = super()._column_info_mapping()
        return dict(
            pre=self.pre_data_col_names,
            post=self.post_data_col_names,
            label=self.label_col_names,
            prediction=self.prediction_col_names,
            feature_influences=self.feature_influence_col_names,
            **column_info_mapping
        )


@dataclass(eq=True, frozen=True)
class NLPColumnSpec(BaseColumnSpec):
    '''Parameter data class mapping column names to data kinds

    Args:
        text_col_name: Name of pre-transform raw text column
        prediction_col_name: Name of prediction column
        label_col_name: Name of ground truth label column
        token_influence_col_name: Name of feature influences column
        tokens_col_name: Name of tokens column
        sentence_embeddings_col_name: Name of embeddings column
    '''
    text_col_name: str = None
    prediction_col_name: str = None
    label_col_name: str = None
    token_influence_col_name: str = None
    tokens_col_name: str = None
    sentence_embeddings_col_name: str = None

    def _column_info_mapping(self) -> Dict[str, Union[tuple, str]]:
        column_info_mapping = super()._column_info_mapping()
        return dict(
            pre=self.text_col_name,
            label=self.label_col_name,
            prediction=self.prediction_col_name,
            feature_influences=self.token_influence_col_name,
            tokens_column=self.tokens_col_name,
            embeddings_column=self.sentence_embeddings_col_name,
            **column_info_mapping
        )

    @classmethod
    def for_explainer(
        cls,
        sentence_embeddings_col_name: str = None,
        select_columns: list[str] = None,
        **kwargs
    ):
        """Provides a NLPColumnSpec to match NLPExplainer.explain() output format. 

        Args:
            sentence_embeddings_col_name (str, optional): If provided, represents the name of the embeddings column in add_data DataFrame. Defaults to None.
            select_columns (list[str], optional): A filtered list of columns to apply. If not provided, returns all default NLPExplainer columns. Defaults to None.
            Values may include:
             - `id_col_name`
             - `text_col_name`
             - `prediction_col_name`
             - `label_col_name`
             - `token_influence_col_name`
             - `tokens_col_name`

        Returns:
            NLPColumnSpec: A NLPColumnSpec object with default column names matching the returned DataFrame from NLPExplainer.explain().
        """
        defaults = dict(
            id_col_name="original_index",
            text_col_name="text",
            prediction_col_name="preds",
            label_col_name="labels",
            token_influence_col_name="influences",
            tokens_col_name="tokens"
        )
        if select_columns:
            defaults = {
                k: v for k, v in defaults.items() if k in select_columns
            }
        if sentence_embeddings_col_name:
            kwargs['sentence_embeddings_col_name'
                  ] = sentence_embeddings_col_name
        params = defaults | kwargs
        return cls(**params)


@dataclass(eq=True, frozen=True)
class ModelOutputContext:
    '''Parameter data class representing context for model predictions and feature influences

    Args:
        model_name: Name of the model corresponding to the data
        score_type: Score type of the data. For a list of valid score types, see `tru.list_valid_score_types`.
        background_split_name: Name of the split that feature influences are computed against. Feature influences only.
        influence_type: Type of algorithm used to compute influence. Feature influences only.
    '''
    model_name: str
    score_type: str = ""
    background_split_name: str = ""
    influence_type: str = ""

    def __post_init__(self):
        if is_nontabular_influence_type(
            self.influence_type
        ) and self.background_split_name:
            raise ValueError(
                f"`background_split_name` cannot be used with influence_type `{self.influence_type}`"
            )

    def clone(
        self,
        *,
        model_name: Optional[str] = None,
        score_type: Optional[str] = None,
        background_split_name: Optional[str] = None,
        influence_type: Optional[str] = None
    ) -> ModelOutputContext:
        '''Return new ModelOutputContext with any provided parameter replaced'''
        return ModelOutputContext(
            model_name=model_name or self.model_name,
            score_type=score_type or self.score_type,
            background_split_name=background_split_name or
            self.background_split_name,
            influence_type=influence_type or self.influence_type
        )

    def to_create_cache_info(
        self, workspace
    ) -> Optional[ds_messages_pb.CreateCacheInfo]:
        if not self.model_name:
            return None

        model_id = workspace.ar_client.get_model_metadata(
            project_id=workspace.project.id, model_name=self.model_name
        ).id

        background_split_id = None
        if self.background_split_name and not is_nontabular_influence_type(
            self.influence_type
        ):
            background_split_id = workspace.ar_client.get_datasplit_metadata(
                project_id=workspace.project.id,
                data_collection_name=workspace.data_collection.name,
                datasplit_name=self.background_split_name
            ).id

        return CreateCacheInfo(
            model_id=model_id,
            score_type=self.score_type,
            background_split_id=background_split_id,
            explanation_algorithm_type=self.influence_type
        ).build_create_cache_info()

    def infer_model_name(self, workspace) -> ModelOutputContext:
        if self.model_name:
            return self
        model_in_context = workspace.get_context().get("model", None)
        if model_in_context:
            workspace.logger.info(
                f"Inferred `model_name` to be '{model_in_context}' from the current workspace context."
            )
            return self.clone(model_name=model_in_context)
        raise ValueError(
            "Could not infer `model_name` for ModelOutputContext as there is no model set in the current workspace context. Please supply `model_name` in `model_output_context` or set a model in current workspace context."
        )

    def infer_score_type(self, workspace) -> ModelOutputContext:
        if self.score_type:
            return self
        score_type = get_string_from_qoi_string(
            workspace.artifact_interaction_client.get_project_metadata(
                workspace.project.id
            )["settings"]["score_type"]
        )
        workspace.logger.info(
            f"Inferred `score_type` to be '{score_type}' from current project in workspace context."
        )
        return self.clone(score_type=score_type)

    def infer_background_split_name(self, workspace) -> ModelOutputContext:
        if self.background_split_name:
            return self
        background_split_name = None
        if workspace_validation_utils.is_tabular_project(
            workspace._get_input_type()
        ):
            background_split_name, _ = workspace._infer_background_split(None)
        return self.clone(background_split_name=background_split_name)

    def infer_influence_type(self, workspace) -> ModelOutputContext:
        if self.influence_type:
            return self
        influence_type = workspace.get_influence_type()
        workspace.logger.info(
            f"Inferred `influence_type` to be '{influence_type}' from current workspace context."
        )
        return self.clone(influence_type=influence_type)


def column_spec_from_kwargs(**kwargs) -> BaseColumnSpec:
    matched = False
    for cls in BaseColumnSpec.valid_types():
        try:
            column_spec = cls(**kwargs)
            matched = True
            break
        except TypeError:
            continue
    if not matched:
        raise TypeError(
            "column_spec must be a dict or a valid ColumnSpec object"
        )
    return column_spec


def merge_dataframes_and_create_column_spec(
    id_col_name: str,
    timestamp_col_name: Optional[str] = None,
    pre_data: Optional[pd.DataFrame] = None,
    post_data: Optional[pd.DataFrame] = None,
    predictions: Optional[pd.DataFrame] = None,
    labels: Optional[pd.DataFrame] = None,
    extra_data: Optional[pd.DataFrame] = None,
    feature_influences: Optional[pd.DataFrame] = None,
    feature_influence_suffix: Optional[str
                                      ] = FEATURE_INFLUENCE_SUFFIX_TRUERA_QII
) -> Tuple[pd.DataFrame, ColumnSpec]:
    """Helper function to merge multiple DataFrames into one and generate a ColumnSpec

    Args:
        id_col_name (str): Id column name.
        timestamp_col_name (Optional[str], optional): Timestamp column name. Defaults to None.
        pre_data (Optional[pd.DataFrame], optional): DataFrame corresponding to pre data. Defaults to None.
        post_data (Optional[pd.DataFrame], optional): DataFrame corresponding to post data. Defaults to None.
        predictions (Optional[pd.DataFrame], optional): DataFrame corresponding to predictions. Defaults to None.
        labels (Optional[pd.DataFrame], optional): DataFrame corresponding to labels. Defaults to None.
        extra_data (Optional[pd.DataFrame], optional): DataFrame corresponding to extra data. Defaults to None.
        feature_influences (Optional[pd.DataFrame], optional): DataFrame correspondnig to feature influences. Defaults to None.
        feature_influence_suffix (Optional[str ], optional): Suffix to append to column names of feature influences in order to prevent duplicate name issues. Defaults to FEATURE_INFLUENCE_SUFFIX_TRUERA_QII.

    Returns:
        Tuple[pd.DataFrame, ColumnSpec]: A tuple consisting of the merged DataFrame and corresponding ColumnSpec
    """

    sys_cols = [id_col_name]
    if timestamp_col_name is not None:
        sys_cols.append(timestamp_col_name)

    pre_data_col_names = _get_columns(pre_data, exclude=sys_cols)

    if pre_data is not None and feature_influences is not None:

        def rename_fi_col(fi_col_name):
            if fi_col_name in pre_data_col_names:
                return fi_col_name + feature_influence_suffix
            return fi_col_name

        feature_influences = feature_influences.rename(columns=rename_fi_col)

    dfs = [
        df for df in [
            pre_data, post_data, predictions, labels, extra_data,
            feature_influences
        ] if df is not None
    ]

    data = None
    for df in dfs:
        if id_col_name not in df.columns:
            raise ValueError(
                f"Id column '{id_col_name}' needs to be in every dataframe."
            )
        if not df[id_col_name].is_unique:
            raise ValueError(f"Elements in id column need to be unique.")
        if data is None:
            data = df.copy()
        else:
            if len(df) != len(data):
                raise ValueError("DataFrames need to be the same length.")
            columns = df.columns.difference(data.columns
                                           ).to_list() + [id_col_name]
            data = data.merge(df[columns], on=id_col_name)

    column_spec = ColumnSpec(
        id_col_name=id_col_name,
        timestamp_col_name=timestamp_col_name,
        pre_data_col_names=pre_data_col_names,
        post_data_col_names=_get_columns(post_data, exclude=sys_cols),
        prediction_col_names=_get_columns(predictions, exclude=sys_cols),
        label_col_names=_get_columns(labels, exclude=sys_cols),
        extra_data_col_names=_get_columns(extra_data, exclude=sys_cols),
        feature_influence_col_names=_get_columns(
            feature_influences, exclude=sys_cols
        )
    )
    return data, column_spec


def _get_columns(data: pd.DataFrame, exclude: Sequence[str]) -> Sequence[str]:
    if data is None:
        return []
    columns = [c for c in data.columns if c not in exclude]
    return columns


def infer_model_output_context(
    workspace, column_spec: BaseColumnSpec,
    model_output_context: Optional['ModelOutputContext'],
    is_production_data: bool
) -> ModelOutputContext:
    if not model_output_context:
        model_output_context = ModelOutputContext("")

    column_info = column_spec.to_column_info()
    if column_info.label and is_production_data:
        model_output_context = model_output_context.infer_model_name(workspace)

    if column_info.prediction:
        model_output_context = model_output_context.infer_model_name(workspace)
        model_output_context = model_output_context.infer_score_type(workspace)

    if column_info.feature_influences:
        model_output_context = model_output_context.infer_model_name(workspace)
        model_output_context = model_output_context.infer_score_type(workspace)
        model_output_context = model_output_context.infer_background_split_name(
            workspace
        )
        model_output_context = model_output_context.infer_influence_type(
            workspace
        )

    return model_output_context
