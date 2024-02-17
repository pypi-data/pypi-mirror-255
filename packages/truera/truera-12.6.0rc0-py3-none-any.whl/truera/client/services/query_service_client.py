from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
import json
import logging
from typing import (
    List, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING, Union
)

import pandas as pd

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.query_service_communicator import \
    AbstractQueryServiceCommunicator
from truera.client.public.communicator.query_service_http_communicator import \
    HttpQueryServiceCommunicator
from truera.client.util.data.row_major_value_table_util import \
    RowMajorValueTableUtil
from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyType  # pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.intelligence_service_pb2 import \
    BiasType  # pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.intelligence_service_pb2 import \
    BucketizedStatsType  # pylint: disable=no-name-in-module
import truera.protobuf.public.common_pb2 as common_pb
from truera.protobuf.public.qoi_pb2 import \
    QuantityOfInterest  # pylint: disable=no-name-in-module
from truera.protobuf.queryservice import query_service_pb2 as qs_pb
from truera.utils.data_constants import NORMALIZED_EMBEDDINGS_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_ID_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_LABEL_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_PREDICTION_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_RANKING_ITEM_ID_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_TIMESTAMP_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_TOKENS_COLUMN_NAME
from truera.utils.data_constants import SYSTEM_COLUMNS
from truera.utils.truera_status import TruEraInternalError
from truera.utils.truera_status import TruEraNotFoundError

if TYPE_CHECKING:
    from truera.authn.usercontext import RequestContext

TRUERA_SPLIT_ID_COL = "__truera_split_id__"


@dataclass
class BatchDataSummaryResults:

    @dataclass
    class BatchDataSummaryResult:
        df: pd.DataFrame
        error: qs_pb.QueryItemResult.QueryError

    entries: List[BatchDataSummaryResult]


@dataclass
class BatchISPResults:

    @dataclass
    class BatchISPResult:
        is_categorical: bool
        df: pd.DataFrame

        def json(self):
            batch_isp_dict = {
                "is_categorical": self.is_categorical,
                "df": self.df.to_dict(orient='dict')
            }
            return json.dumps(batch_isp_dict)

        @classmethod
        def from_json(cls, string: str):
            data: dict = json.loads(string)
            if isinstance(data['df'], dict):
                data['df'] = pd.DataFrame.from_dict(data['df'])
            return cls(**data)

    entries: Mapping[str, BatchISPResult]


def _remove_additional_bins_isp(
    df: pd.DataFrame, fv_grid_size: int, fi_grid_size: int
) -> pd.DataFrame:
    # making an assumption here that if there are additional bins, it is only off by 1
    # in case of numeric features it will be both sets of bounds and for categorical just the upper/lower bounds
    right_unique_vals = df["right_bound"].unique()
    left_unique_vals = df["left_bound"].unique()
    if (
        len(right_unique_vals) > fv_grid_size and
        len(left_unique_vals) > fv_grid_size
    ):  # this should only affect numeric features
        r_corner_val = right_unique_vals.max()
        l_corner_val = left_unique_vals.max()
        df = df.drop(
            df[(df["right_bound"] == r_corner_val) &
               (df["left_bound"] == l_corner_val) & (df["bin_count"] == 0) &
               (df["avg_fi"] == 0)].index
        )
    upper_unique_vals = df["upper_bound"].unique()
    lower_unique_vals = df["lower_bound"].unique()
    if (
        len(upper_unique_vals) > fi_grid_size and
        len(lower_unique_vals) > fi_grid_size
    ):
        up_corner_val = upper_unique_vals.max()
        low_corner_val = lower_unique_vals.max()
        df = df.drop(
            df[(df["upper_bound"] == up_corner_val) &
               (df["lower_bound"] == low_corner_val) & (df["bin_count"] == 0) &
               (df["avg_fi"] == 0)].index
        )
    return df


class QueryServiceClient(object):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails = None,
        use_http: bool = False,
        logger=None,
        verify_cert: Union[bool, str] = True,
    ):
        if not use_http:
            from truera.client.private.communicator.query_service_grpc_communicator import \
                GrpcQueryServiceCommunicator
        self.communicator: AbstractQueryServiceCommunicator = HttpQueryServiceCommunicator(
            connection_string, auth_details, logger, verify_cert=verify_cert
        ) if use_http else GrpcQueryServiceCommunicator(
            connection_string, auth_details, logger
        )
        self.logger = logger or logging.getLogger(__name__)
        self._include_sys_cols = [
            NORMALIZED_ID_COLUMN_NAME, NORMALIZED_TIMESTAMP_COLUMN_NAME,
            NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME,
            NORMALIZED_RANKING_ITEM_ID_COLUMN_NAME
        ]

    def echo(self, request_id: str, message: str) -> qs_pb.EchoResponse:
        self.logger.info(
            f"QueryServiceClient::echo request_id={request_id}, message={message}"
        )
        request = qs_pb.EchoRequest(request_id=request_id, message=message)
        response = self.communicator.echo(request)
        return response

    def getPreprocessedData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        return self._read_static_data(
            project_id=project_id,
            data_collection_id=data_collection_id,
            query_spec=query_spec,
            expected_data_kind="DATA_KIND_PRE",
            system_cols_to_keep=self._include_sys_cols
            if include_system_data else [],
            request_id=request_id,
            request_context=request_context
        )

    def getProcessedOrPreprocessedData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        try:
            return self._read_static_data(
                project_id=project_id,
                data_collection_id=data_collection_id,
                query_spec=query_spec,
                expected_data_kind="DATA_KIND_POST",
                system_cols_to_keep=self._include_sys_cols
                if include_system_data else [],
                request_id=request_id,
                request_context=request_context
            )
        except TruEraNotFoundError:
            return self._read_static_data(
                project_id=project_id,
                data_collection_id=data_collection_id,
                query_spec=query_spec,
                expected_data_kind="DATA_KIND_PRE",
                system_cols_to_keep=self._include_sys_cols
                if include_system_data else [],
                request_id=request_id,
                request_context=request_context
            )

    def getLabels(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        try:
            return self._read_static_data(
                project_id=project_id,
                data_collection_id=data_collection_id,
                query_spec=query_spec,
                expected_data_kind="DATA_KIND_LABEL",
                system_cols_to_keep=[NORMALIZED_LABEL_COLUMN_NAME] +
                self._include_sys_cols
                if include_system_data else [NORMALIZED_LABEL_COLUMN_NAME],
                request_id=request_id,
                request_context=request_context
            )
        except TruEraNotFoundError as e:
            self.logger.info(
                f"GetLabels could not fetch labels. Returning 'None' instead. Exception raised is {e}."
            )
            return None
        except Exception as e:
            raise TruEraInternalError(
                f"GetLabels could not fetch labels for unknown reason. Exception raised is {e}."
            )

    def getExtraData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None,
    ) -> pd.DataFrame:
        return self._read_static_data(
            project_id=project_id,
            data_collection_id=data_collection_id,
            query_spec=query_spec,
            expected_data_kind="DATA_KIND_EXTRA",
            system_cols_to_keep=self._include_sys_cols
            if include_system_data else [],
            request_id=request_id,
            request_context=request_context
        )

    def getModelPredictions(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        classification_threshold: float,
        classification_threshold_qoi: QuantityOfInterest,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            prediction_request=qs_pb.PredictionRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec,
                classification_threshold=
                classification_threshold,  # [PI-910] to be deprecated
                threshold_context=qs_pb.ClassificationThresholdContext(
                    qoi=classification_threshold_qoi,
                    threshold=classification_threshold
                )
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            return None
        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=[NORMALIZED_PREDICTION_COLUMN_NAME] +
            self._include_sys_cols
            if include_system_data else [NORMALIZED_PREDICTION_COLUMN_NAME]
        )

        return dataframe

    def getBucketizedStats(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        classification_threshold: float,
        classification_threshold_qoi: QuantityOfInterest,
        stats_type: BucketizedStatsType.Type,
        request_id: str,
        request_context=None
    ) -> pd.DataFrame:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            bucketized_stats_request=qs_pb.BucketizedStatsRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec,
                classification_threshold=
                classification_threshold,  # [PI-910] to be deprecated
                threshold_context=qs_pb.ClassificationThresholdContext(
                    qoi=classification_threshold_qoi,
                    threshold=classification_threshold
                ),
                stats_type=stats_type
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        return dataframe

    def getBatchISP(
        self, request: qs_pb.QueryRequest, request_context,
        grid_size: Tuple[int, int]
    ) -> BatchISPResults:
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            return None
        return QueryServiceClient._parse_pb_df_into_batch_isp_results(
            dataframe, grid_size=grid_size, logger=self.logger
        )

    @staticmethod
    def _parse_pb_df_into_batch_isp_results(
        df: pd.DataFrame,
        grid_size: Tuple[int, int],
        logger: Optional[logging.Logger] = None
    ) -> BatchISPResults:
        """        feat_name; is_categorical; feat_value; left_bound; right_bound; lower_bound; upper_bound; bin_count; avg_fi
        Numerical:    float_0          0              ""            -1           1           -2            0         3     -0.5
        Categorical:   str_0           1              "A"            0           0            1            2         4      1.5
        """
        batch_results = BatchISPResults(entries={})
        grouped_dfs = {name: group for name, group in df.groupby('feat_name')}

        for feature_name, group_df in grouped_dfs.items():
            group_df.fillna(0, inplace=True)
            group_df = _remove_additional_bins_isp(
                group_df, fv_grid_size=grid_size[0], fi_grid_size=grid_size[1]
            )
            if logger and len(group_df) > grid_size[0] * grid_size[1]:
                logger.warning(
                    f"Incorrect sized ISP responses for feature: {feature_name}"
                )
            is_categorical = bool(group_df['is_categorical'].iloc[0])
            result = BatchISPResults.BatchISPResult(
                is_categorical=is_categorical, df=group_df
            )
            batch_results.entries[feature_name] = result

        return batch_results

    @staticmethod
    def _guarentee_select_cols(
        query_spec: qs_pb.QuerySpec, ensure_select_cols: List[str]
    ):
        copied = False
        for col in ensure_select_cols:
            if col not in query_spec.select_columns:
                if not copied:
                    new_query_spec = qs_pb.QuerySpec()
                    new_query_spec.CopyFrom(query_spec)
                    query_spec = new_query_spec
                    copied = True
                query_spec.select_columns.append(col)
        return query_spec

    def getTrace(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        request_id: str,
        request_context=None
    ) -> pd.DataFrame:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            raw_data_request=qs_pb.RawDataRequest(
                query_spec=query_spec,
                data_kind="DATA_KIND_TRACE",
                data_collection_id=data_collection_id,
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        return dataframe

    def getTraceDataset(
        self,
        project_id: str,
        model_id: str,
        data_collection_id: str,
        feedback_function_thresholds: dict[str, float],
        query_spec: qs_pb.QuerySpec,
        request_id: str,
        request_context=None
    ) -> pd.DataFrame:

        if feedback_function_thresholds:
            request = qs_pb.QueryRequest(
                id=request_id,
                project_id=project_id,
                feedback_threshold_request=qs_pb.FeedbackThresholdsRequest(
                    model_id=model_id,
                    query_spec=query_spec,
                    thresholds=[
                        qs_pb.FeedbackThresholdsRequest.FeedbackThresholds(
                            feedback_function_id=ff_id, threshold=threshold
                        ) for ff_id, threshold in
                        feedback_function_thresholds.items()
                    ],
                )
            )
        else:
            request = qs_pb.QueryRequest(
                id=request_id,
                project_id=project_id,
                raw_data_request=qs_pb.RawDataRequest(
                    data_kind="DATA_KIND_TRACE",
                    query_spec=query_spec,
                    data_collection_id=data_collection_id
                )
            )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        return dataframe

    def getFeedbackFunctionEvals(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        request_id: str,
        request_context=None
    ) -> pd.DataFrame:

        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            raw_data_request=qs_pb.RawDataRequest(
                query_spec=query_spec,
                data_kind="DATA_KIND_FEEDBACK",
                data_collection_id=data_collection_id,
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError(
                "Could not find any feedback function evaluations."
            )

        return dataframe

    def getModelTokens(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        include_system_data: bool,
        classification_threshold: float,
        classification_threshold_qoi: QuantityOfInterest,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        query_spec = self._guarentee_select_cols(
            query_spec,
            [NORMALIZED_ID_COLUMN_NAME, NORMALIZED_TOKENS_COLUMN_NAME]
        )
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            prediction_request=qs_pb.PredictionRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec,
                classification_threshold=
                classification_threshold,  # [PI-910] to be deprecated
                threshold_context=qs_pb.ClassificationThresholdContext(
                    qoi=classification_threshold_qoi,
                    threshold=classification_threshold
                )
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=[NORMALIZED_TOKENS_COLUMN_NAME] +
            self._include_sys_cols
            if include_system_data else [NORMALIZED_TOKENS_COLUMN_NAME],
            cols_to_drop=[NORMALIZED_PREDICTION_COLUMN_NAME]
        )
        return dataframe

    def getModelEmbeddings(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        query_spec = self._guarentee_select_cols(
            query_spec,
            [NORMALIZED_ID_COLUMN_NAME, NORMALIZED_EMBEDDINGS_COLUMN_NAME]
        )
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            prediction_request=qs_pb.PredictionRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=[NORMALIZED_EMBEDDINGS_COLUMN_NAME] +
            self._include_sys_cols
            if include_system_data else [NORMALIZED_EMBEDDINGS_COLUMN_NAME],
            cols_to_drop=[NORMALIZED_PREDICTION_COLUMN_NAME]
        )
        return dataframe

    def getModelInfluences(
        self,
        project_id: str,
        request_id: str,
        query_spec: qs_pb.QuerySpec,
        options: common_pb.FeatureInfluenceOptions,
        model_id: Optional[str] = None,
        include_system_data: bool = False,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            feature_influence_request=qs_pb.FeatureInfluenceRequest(
                model_id=model_id, query_spec=query_spec, options=options
            )
        )
        response_stream = self.communicator.query(request, request_context)
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            response_stream
        )
        if dataframe is None:
            return None

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=self._include_sys_cols
            if include_system_data else []
        )
        return dataframe

    def getAccuracies(
        self,
        project_id: str,
        model_id: str,
        accuracy_types: Sequence[AccuracyType.Type],
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        classification_threshold: float,
        classification_threshold_qoi: QuantityOfInterest,
        include_confusion_matrix: bool,
        include_record_count: bool,
        request_id: str,
        request_context=None
    ) -> qs_pb.AccuracyResponse:
        request = qs_pb.AccuracyRequest(
            request_id=request_id,
            project_id=project_id,
            model_id=model_id,
            accuracy_type=accuracy_types,
            query_spec=query_spec,
            qoi=quantity_of_interest,
            classification_threshold=
            classification_threshold,  # [PI-910] to be deprecated
            threshold_context=qs_pb.ClassificationThresholdContext(
                qoi=classification_threshold_qoi,
                threshold=classification_threshold
            ),
            include_confusion_matrix=include_confusion_matrix,
            include_compute_record_count=include_record_count
        )
        response = self.communicator.accuracy(request, request_context)
        return response

    def getModelComparison(
        self,
        request_id: str,
        project_id: str,
        comparison_specs: list,
        request_context=None
    ):
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            model_comparison_request=qs_pb.ModelComparisonRequest(
                comparison_specs=comparison_specs
            )
        )
        response = self.communicator.query(request, request_context)
        return RowMajorValueTableUtil.pb_stream_to_dataframe(response)

    def getModelBias(
        self,
        request_id: str,
        project_id: str,
        bias_type: BiasType.Type,
        model_id: str,
        query_spec_1: qs_pb.QuerySpec,
        query_spec_2: qs_pb.QuerySpec,
        qoi: QuantityOfInterest,
        classification_threshold: float,
        classification_threshold_qoi: QuantityOfInterest,
        positive_class_favored: bool,
        request_context=None
    ):
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            model_bias_request=qs_pb.ModelBiasRequest(
                bias_type=bias_type,
                model_id=model_id,
                query_spec_1=query_spec_1,
                query_spec_2=query_spec_2,
                qoi=qoi,
                classification_threshold=
                classification_threshold,  # [PI-910] to be deprecated
                threshold_context=qs_pb.ClassificationThresholdContext(
                    qoi=classification_threshold_qoi,
                    threshold=classification_threshold
                ),
                positive_class_favored=positive_class_favored
            )
        )
        response = self.communicator.query(request, request_context)
        return RowMajorValueTableUtil.pb_stream_to_dataframe(response)

    def getFilterData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            filter_data_request=qs_pb.FilterDataRequest(
                data_collection_id=data_collection_id, query_spec=query_spec
            )
        )
        response_stream = self.communicator.query(request, request_context)
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            response_stream
        )
        if dataframe is None:
            return None

        dataframe = self._resolve_split_metadata(dataframe=dataframe)
        return dataframe

    def getBatchQueryResponse(
        self,
        request: qs_pb.BatchQueryRequest,
        request_context=None
    ) -> Iterator[qs_pb.BatchQueryResponse]:
        return self.communicator.batch_query(request, request_context)

    def _pb_stream_to_batch_results(
        self, response_stream: Iterator[qs_pb.BatchQueryResponse]
    ) -> BatchDataSummaryResults:
        # NOTE: response_stream only contains one response for batch data summary though the generic getBatchQueryResponse is designed to return a response stream
        for response in response_stream:
            results = BatchDataSummaryResults(entries=[])
            for query_item_result in response.results:
                if query_item_result.error_code != qs_pb.QueryItemResult.QueryError.NO_ERROR:
                    results.entries.append(
                        BatchDataSummaryResults.BatchDataSummaryResult(
                            df=pd.DataFrame(),
                            error=query_item_result.error_code
                        )
                    )
                    continue
                dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
                    [query_item_result]
                )
                if dataframe is None or len(dataframe) == 0:
                    results.entries.append(
                        BatchDataSummaryResults.BatchDataSummaryResult(
                            df=pd.DataFrame(),
                            error=query_item_result.error_code
                        )
                    )
                    continue
                dataframe = self._resolve_split_metadata(
                    dataframe=dataframe,
                    system_cols_to_keep=self._include_sys_cols
                )
                if isinstance(dataframe, pd.Series):
                    dataframe = dataframe.to_frame()
                results.entries.append(
                    BatchDataSummaryResults.BatchDataSummaryResult(
                        df=dataframe, error=query_item_result.error_code
                    )
                )

            return results

    def getBatchDataSummary(
        self,
        request: qs_pb.BatchQueryRequest,
        request_context=None
    ) -> BatchDataSummaryResults:
        response_stream = self.getBatchQueryResponse(
            request_context=request_context, request=request
        )
        return self._pb_stream_to_batch_results(response_stream=response_stream)

    def _read_static_data(
        self,
        *,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        expected_data_kind: str,
        system_cols_to_keep: Sequence[str],
        request_id: str,
        request_context=None,
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            raw_data_request=qs_pb.RawDataRequest(
                data_kind=expected_data_kind,
                data_collection_id=data_collection_id,
                query_spec=query_spec
            )
        )
        response_stream = self.communicator.query(request, request_context)
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            response_stream
        )
        if dataframe is None:
            return None

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=system_cols_to_keep,
        )
        return dataframe

    def _resolve_split_metadata(
        self,
        dataframe: pd.DataFrame,
        system_cols_to_keep: Optional[list[str]] = None,
        cols_to_drop: Optional[Sequence[str]] = None
    ) -> pd.DataFrame:
        system_cols_to_keep = system_cols_to_keep or []
        cols_to_drop = cols_to_drop or []
        for col in SYSTEM_COLUMNS:
            if col not in dataframe.columns:
                continue
            elif col in [
                NORMALIZED_ID_COLUMN_NAME,
                NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME,
                NORMALIZED_RANKING_ITEM_ID_COLUMN_NAME
            ]:
                continue
            elif col not in system_cols_to_keep:
                cols_to_drop.append(col)
            elif col == NORMALIZED_TIMESTAMP_COLUMN_NAME:
                # get datetime from integer epoch, but cast to string for AIQ purposes
                dataframe[NORMALIZED_TIMESTAMP_COLUMN_NAME] = pd.to_datetime(
                    dataframe[NORMALIZED_TIMESTAMP_COLUMN_NAME], unit="s"
                ).astype(str)
        df_columns = set(dataframe.columns)
        cols_to_drop = [c for c in cols_to_drop if c in df_columns]
        dataframe.drop(cols_to_drop, axis="columns", inplace=True)
        if NORMALIZED_ID_COLUMN_NAME in dataframe.columns:
            dataframe.set_index(NORMALIZED_ID_COLUMN_NAME, inplace=True)
        return dataframe

    def getFeatureDrift(
        self,
        request_id: str,
        project_id: str,
        drift_request=qs_pb.DriftRequest,
        request_context=None
    ):
        request = qs_pb.QueryRequest(
            id=request_id, project_id=project_id, drift_request=drift_request
        )
        response = self.communicator.query(request, request_context)
        return RowMajorValueTableUtil.pb_stream_to_dataframe(response)
