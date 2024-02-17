from __future__ import annotations

import hashlib
from logging import Logger
from numbers import Number
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, Type

from google.protobuf.struct_pb2 import \
    Value  # pylint: disable=no-name-in-module
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# pylint: disable=no-name-in-module
from truera.protobuf.public.data.filter_pb2 import FilterExpression
from truera.protobuf.public.data.filter_pb2 import FilterExpressionOperator
from truera.protobuf.public.data.filter_pb2 import FilterLeaf
from truera.protobuf.public.data.segment_pb2 import InterestingSegment
from truera.protobuf.public.data.segment_pb2 import Segment
# pylint: enable=no-name-in-module
from truera.utils.accuracy_utils import absolute_error_pointwise
from truera.utils.accuracy_utils import auc_pointwise
from truera.utils.accuracy_utils import classification_accuracy_pointwise
from truera.utils.accuracy_utils import confusion_matrix_pointwise
from truera.utils.accuracy_utils import log_loss_score_pointwise
from truera.utils.accuracy_utils import squared_error_pointwise
from truera.utils.accuracy_utils import squared_log_error_pointwise
from truera.utils.truera_status import TruEraInvalidArgumentError

EPSILON = 1e-15  # factor to avoid NaNs in HIGH_LOG_LOSS calc
DEFAULT_MIN_SEGMENT_SIZE = 50

POINTWISE_METRIC_MAP = {
    InterestingSegment.Type.HIGH_MEAN_ABSOLUTE_ERROR:
        absolute_error_pointwise,
    InterestingSegment.Type.HIGH_MEAN_SQUARED_ERROR:
        squared_error_pointwise,
    InterestingSegment.Type.HIGH_MEAN_SQUARED_LOG_ERROR:
        squared_log_error_pointwise,
    InterestingSegment.Type.HIGH_LOG_LOSS:
        log_loss_score_pointwise,
    InterestingSegment.Type.LOW_POINTWISE_AUC:
        auc_pointwise,
    InterestingSegment.Type.LOW_CLASSIFICATION_ACCURACY:
        classification_accuracy_pointwise
}

THRESHOLDED_METRIC_MAP = {
    InterestingSegment.Type.LOW_PRECISION: (["TP"], ["TP", "FP"]),
    InterestingSegment.Type.LOW_RECALL: (["TP"], ["TP", "FN"]),
    InterestingSegment.Type.LOW_TRUE_POSITIVE_RATE: (["TP"], ["TP", "FN"]),
    InterestingSegment.Type.HIGH_FALSE_POSITIVE_RATE: (["FP"], ["FP", "TN"]),
    InterestingSegment.Type.LOW_TRUE_NEGATIVE_RATE: (["TN"], ["TN", "FP"]),
    InterestingSegment.Type.HIGH_FALSE_NEGATIVE_RATE: (["FN"], ["FN", "TP"])
}

MAX_NUM_FEATURES = 3


class InterestingSegmentsProcessor:
    """
    RPC calls covered here:

       GetInterestingSegments(InterestingSegmentsRequest) -> InterestingSegmentsResponse
    """
    _DEFAULT_NUM_SAMPLES = 100

    @staticmethod
    def validate_num_features(num_features: int) -> None:
        if num_features <= 0:
            raise TruEraInvalidArgumentError(f"`num_features` must be > 0!")
        if num_features > MAX_NUM_FEATURES:
            raise TruEraInvalidArgumentError(
                f"`num_features` must be <= {MAX_NUM_FEATURES}!"
            )

    @staticmethod
    def validate_and_get_num_samples(num_samples: int, logger: Logger) -> int:
        if num_samples <= 0:
            logger.info(
                f"`num_samples` is <= 0, setting to default value of {InterestingSegmentsProcessor._DEFAULT_NUM_SAMPLES}"
            )
            return InterestingSegmentsProcessor._DEFAULT_NUM_SAMPLES
        return num_samples

    @staticmethod
    def bootstrap(
        xs: Sequence[pd.DataFrame], ys: Sequence[pd.Series],
        ys_pred: Sequence[pd.Series], bootstrapping_fraction: float,
        random_state: int
    ):
        if bootstrapping_fraction == 1:
            return xs, ys, ys_pred
        ret_xs = []
        ret_ys = []
        ret_ys_pred = []
        for i in range(len(xs)):
            curr_xs, _, curr_ys, _, curr_ys_pred, _ = train_test_split(
                xs[i],
                ys[i],
                ys_pred[i],
                train_size=bootstrapping_fraction,
                random_state=random_state
            )
            ret_xs.append(curr_xs)
            ret_ys.append(curr_ys)
            ret_ys_pred.append(curr_ys_pred)
        return ret_xs, ret_ys, ret_ys_pred

    @staticmethod
    def validate_and_get_pointwise_metrics(
        interesting_segment_type: InterestingSegment.Type,
        all_ys: Sequence[pd.Series],
        all_ys_pred: Sequence[pd.Series],
    ) -> Sequence[pd.DataFrame]:
        if len(all_ys) != len(all_ys_pred) or len(all_ys) not in [1, 2]:
            raise ValueError(
                "`all_ys` and `all_ys_pred` must be the same length and in {1, 2}!"
            )
        ret = []
        for idx in range(len(all_ys)):
            if interesting_segment_type in POINTWISE_METRIC_MAP:
                pointwise_metric_fn = POINTWISE_METRIC_MAP[
                    interesting_segment_type]
                error = pointwise_metric_fn(all_ys[idx], all_ys_pred[idx])
                if len(all_ys) == 1:
                    error = error - np.mean(error)
                error = pd.DataFrame(error, index=all_ys[idx].index)
                ret.append(error)
            elif interesting_segment_type in THRESHOLDED_METRIC_MAP:
                numerator_quadrants, denominator_quadrants = THRESHOLDED_METRIC_MAP[
                    interesting_segment_type]
                numerators = confusion_matrix_pointwise(
                    all_ys[idx], all_ys_pred[idx], numerator_quadrants
                )
                denominators = confusion_matrix_pointwise(
                    all_ys[idx], all_ys_pred[idx], denominator_quadrants
                )
                if len(all_ys) == 1:
                    mean = np.sum(numerators) / np.sum(denominators)
                    numerators -= mean * denominators
                ret.append(
                    pd.DataFrame(
                        {
                            "numerator": numerators,
                            "denominator": denominators
                        }
                    )
                )
            elif interesting_segment_type == InterestingSegment.Type.HIGH_UNDER_OR_OVERSAMPLING:
                ret.append(
                    pd.DataFrame(
                        np.ones(all_ys[idx].shape[0]) / len(all_ys[idx]),
                        index=all_ys[idx].index
                    )
                )
            else:
                raise TruEraInvalidArgumentError(
                    f"Unsupported `interesting_segment_type`: {interesting_segment_type}!"
                )
        return ret

    @staticmethod
    def pointwise_metrics_aggregator(
        interesting_segment_type: InterestingSegment.Type,
        minimum_size: int = DEFAULT_MIN_SEGMENT_SIZE,
        minimum_metric_of_interest_threshold: float = 0.0,
        size_exponent: float = 0.25
    ) -> Type[AggregatorBaseClass]:
        """Returns a pointwise aggregator used in `find_interesting_segments` that computes a size-weighted value mean.

        Args:
            interesting_segment_type: Interesting segment type.
            minimum_size: Minimum size of a segment.
            minimum_metric_of_interest_threshold: Minimum difference between segment and comparison (i.e. entire split when `comparison_data_split_name` is not given, and segment on the `comparison_data_split_name` data-split otherwise). Defaults to 0.
            size_exponent: Exponential factor on size of segment. Should be in [0, 1]. A zero value implies the segment size has no effect.

        Returns:
            Callable[[Sequence[float], Sequence[int]], float]:
                Function which takes the sums of the subset of points in question (possibly with numerators and denominator) and the sizes of the subset and computes a size-weighted value mean.
        """

        if interesting_segment_type in POINTWISE_METRIC_MAP:
            return SimpleAggregator(
                interesting_segment_type, minimum_size,
                minimum_metric_of_interest_threshold, size_exponent
            )
        if interesting_segment_type in THRESHOLDED_METRIC_MAP:
            return NumeratorAndDenominatorAggregator(
                interesting_segment_type, minimum_size,
                minimum_metric_of_interest_threshold, size_exponent
            )
        if interesting_segment_type == InterestingSegment.Type.HIGH_UNDER_OR_OVERSAMPLING:
            return SegmentSizeAggregator(
                interesting_segment_type, None,
                minimum_metric_of_interest_threshold, None
            )
        raise ValueError(
            f"`interesting_segment_type` \"{interesting_segment_type}\" not supported!"
        )

    @staticmethod
    def find_interesting_segments(
        logger: Logger,
        xs: Sequence[pd.DataFrame],
        ys: Optional[Sequence[pd.Series]],
        pointwise_metrics: Sequence[pd.DataFrame],
        pointwise_metrics_aggregator: Callable[
            [Sequence[Sequence[float]], Sequence[int]], float],
        num_features: int,
        num_samples: int,
        random_state: Optional[int] = None
    ) -> pd.DataFrame:
        """Randomly searches for interesting segments in the provided data given by `xs`/`ys` that maximize the `f` function subject to being describable by `num_features`.

        Args:
            logger: logger to output to.
            xs: pretransformed xs data.
            ys: label data. Must correspond to xs if supplied.
            pointwise_metrics: metric value for each point we wish to maximize the pointwise_metrics_aggregator of. The ith entry must correspond to the ith entry of `xs`.
            pointwise_metrics_aggregator: function aggregating a subset of the pointwise_metrics to a single float to maximize.
            num_features: number of features to use to describe the segments.
            num_samples: number of random segments to investigate. Defaults to 100.
            random_state: random state for computation. Defaults to None which is unseeded.
            
        Returns:
            All found segments ranked from most interesting to least along with their corresponding hashed masks.
        """
        np.random.seed(random_state)
        if ys is not None:
            if len(xs) != len(ys):
                raise ValueError(
                    "`ys` must be `None` or of the same length as `xs`!"
                )
            new_xs = []
            for i in range(len(xs)):
                curr = xs[i].copy()
                curr["_DATA_GROUND_TRUTH"] = ys[i].to_numpy()
                new_xs.append(curr)
            xs = new_xs
        all_features = list(xs[0].columns)
        unique_vals = InterestingSegmentsProcessor._compute_unique_vals(xs[0])
        f_scores = []
        segments = []
        hashed_masks = []
        seen = set()
        for sample_idx in range(num_samples):
            features = np.random.choice(
                all_features,
                size=min(num_features, len(all_features)),
                replace=False
            )
            if tuple(features) in seen:
                continue
            seen.add(tuple(features))
            candidate_masks, candidate_filter, candidate_f_score, valid = InterestingSegmentsProcessor._find_interesting_segment_using_features(
                xs, unique_vals, pointwise_metrics,
                pointwise_metrics_aggregator, features
            )
            if valid:
                logger.info(f"sample = {sample_idx}: {candidate_f_score}")
                f_scores.append(candidate_f_score)
                segments.append(Segment(filter_expression=candidate_filter))
                hashed_masks.append(
                    hashlib.sha256(
                        np.hstack(
                            [curr.to_numpy() for curr in candidate_masks]
                        )
                    ).hexdigest()
                )
            else:
                logger.info("Could not find viable segment!")
        ret = pd.DataFrame.from_dict(
            {
                "f_scores": f_scores,
                "segments": segments,
                "hashed_masks": hashed_masks,
            }
        )
        ret.drop_duplicates(subset=["hashed_masks"], inplace=True)
        ret.sort_values(by="f_scores", ascending=False, inplace=True)
        ret.index = range(ret.shape[0])
        if len(ret) > 0:
            logger.info(f"best f_score = {ret['f_scores'].iloc[0]}")
            logger.debug(f"best filter = {ret['segments'].iloc[0]}")
        return ret

    @staticmethod
    def _find_interesting_segment_using_features(
        xs: Sequence[pd.DataFrame], unique_vals: Mapping[str, Sequence[Any]],
        pointwise_metrics: Sequence[pd.DataFrame],
        pointwise_metrics_aggregator: Callable[
            [Sequence[Sequence[float]], Sequence[int]],
            float], features: Sequence[str]
    ) -> Tuple[Optional[Sequence[pd.Series]], Optional[FilterExpression],
               Optional[float], bool]:
        """Greedily find the best possible segment for the provided data constrained by using exactly the features in `features`.

        Args:
            xs: pretransformed xs data.
            unique_vals: unique values of `xs` to use for segment construction.
            pointwise_metrics: metric value for each point we wish to maximize the pointwise_metrics_aggregator of. The ith entry must correspond to the ith entry of `xs`.
            pointwise_metrics_aggregator: function aggregating a subset of the pointwise_metrics to a single float to maximize.
            features: features to use to construct the segment.

        Returns:
            Tuple[Optional[Sequence[pd.Series]], Optional[FilterExpression], Optional[float], bool]:
                1. Masks determining which xs/ys/ys_pred to use.
                2. `FilterExpression` defining segment.
                3. Score of the segment.
                4. Whether the segment is a valid segment or not.
        """
        xs_orig_indexes = [curr.index.copy() for curr in xs]
        base_expressions = []
        ret_f_score = -np.inf
        zero = np.zeros(pointwise_metrics[0].shape[1])
        for feature in features:
            dtype = xs[0].dtypes[feature]
            best_f_score = -np.inf
            best_masks = None
            if dtype in ["object", "str"]:
                # Categorical feature.
                best_val = ""
                best_negate = None
                total_sums = []
                total_sizes = []
                for curr in pointwise_metrics:
                    total_sums.append(list(curr.sum()))
                    total_sizes.append(curr.shape[0])
                for val in unique_vals[feature]:
                    nonnegated_candidate_masks = []
                    nonnegated_candidate_sums = []
                    nonnegated_candidate_sizes = []
                    for idx in range(len(xs)):
                        nonnegated_candidate_mask = xs[idx][feature] == val
                        nonnegated_candidate_masks.append(
                            nonnegated_candidate_mask
                        )
                        nonnegated_pointwise_metrics = pointwise_metrics[idx][
                            nonnegated_candidate_mask]
                        nonnegated_candidate_sums.append(
                            list(nonnegated_pointwise_metrics.sum())
                        )
                        nonnegated_candidate_sizes.append(
                            nonnegated_pointwise_metrics.shape[0]
                        )
                    for negate in [False, True]:
                        candidate_sums = nonnegated_candidate_sums
                        candidate_sizes = nonnegated_candidate_sizes
                        if negate:
                            candidate_sums = []
                            for idx in range(len(xs)):
                                candidate_sums.append(
                                    [
                                        total_sums[idx][jdx] -
                                        nonnegated_candidate_sums[idx][jdx]
                                        for jdx in range(len(total_sums[0]))
                                    ]
                                )
                            candidate_sizes = [
                                total_sizes[idx] -
                                nonnegated_candidate_sizes[idx]
                                for idx in range(len(xs))
                            ]
                        candidate_f_score = pointwise_metrics_aggregator(
                            candidate_sums, candidate_sizes
                        )
                        if best_f_score < candidate_f_score:
                            best_f_score = candidate_f_score
                            best_val = val
                            best_negate = negate
                            best_masks = nonnegated_candidate_masks
                            if negate:
                                best_masks = [
                                    ~curr for curr in nonnegated_candidate_masks
                                ]
                # Create base expression.
                base_expression = InterestingSegmentsProcessor._create_categorical_base_expression(
                    feature, best_val, best_negate
                )
                base_expressions.append(base_expression)
            else:
                # Numerical feature.
                total_sizes = []
                for curr in pointwise_metrics:
                    total_sizes.append(curr.shape[0])
                xs_sorted = []
                for idx in range(len(xs)):
                    raw = pointwise_metrics[idx].copy()
                    raw.index = xs[idx].index
                    raw["feature"] = xs[idx][feature]
                    raw.sort_values(by="feature", inplace=True)
                    feature_vals = raw["feature"].to_numpy()
                    cumsums = raw.drop(columns=["feature"]).cumsum().to_numpy()
                    xs_sorted.append([feature_vals, cumsums])
                curr_unique_vals = unique_vals[feature]
                best_lo = -1
                best_hi = -1
                for lo_idx, lo in enumerate(curr_unique_vals):
                    for hi_idx in range(lo_idx, len(curr_unique_vals)):
                        hi = curr_unique_vals[hi_idx]
                        candidate_sums = []
                        candidate_sizes = []
                        for feature_vals, cumsums in xs_sorted:
                            range_lo_idx = np.searchsorted(
                                feature_vals, lo, side="left"
                            )
                            range_hi_idx = np.searchsorted(
                                feature_vals, hi, side="right"
                            )
                            hi_cumsum = cumsums[range_hi_idx -
                                                1] if range_hi_idx > 0 else zero
                            lo_cumsum = cumsums[range_lo_idx -
                                                1] if range_lo_idx > 0 else zero
                            candidate_sizes.append(range_hi_idx - range_lo_idx)
                            candidate_sums.append(list(hi_cumsum - lo_cumsum))
                        candidate_f_score = pointwise_metrics_aggregator(
                            candidate_sums,
                            candidate_sizes,
                        )
                        if best_f_score < candidate_f_score:
                            best_f_score = candidate_f_score
                            best_lo = lo
                            best_hi = hi
                if best_f_score > -np.inf:
                    best_masks = [
                        (best_lo <= curr[feature]) & (curr[feature] <= best_hi)
                        for curr in xs
                    ]
                # Create base expression.
                base_expression = InterestingSegmentsProcessor._create_numerical_base_expression(
                    feature, best_lo, best_hi
                )
                base_expressions.append(base_expression)
            if best_masks is None:
                return None, None, None, False
            ret_f_score = best_f_score
            xs = [xs[idx][best_masks[idx]] for idx in range(len(xs))]
            pointwise_metrics = [
                pointwise_metrics[idx][best_masks[idx]]
                for idx in range(len(xs))
            ]
        if len(base_expressions) == 0:
            return None, None, None, False
        ret_masks = []
        for idx in range(len(xs)):
            curr = pd.Series(
                np.zeros(len(xs_orig_indexes[idx]), dtype=bool),
                index=xs_orig_indexes[idx]
            )
            curr[xs[idx].index] = True
            ret_masks.append(curr)
        if len(base_expressions) == 1:
            return ret_masks, base_expressions[0], ret_f_score, True
        ret = base_expressions[0]
        for i in range(1, len(base_expressions)):
            left = ret
            ret = FilterExpression()
            ret.operator = FilterExpressionOperator.FEO_AND
            right = base_expressions[i]
            ret.sub_expressions.extend([left, right])
        return ret_masks, ret, ret_f_score, True

    @staticmethod
    def _create_numerical_base_expression(
        feature: str, lo: Number, hi: Number
    ) -> FilterExpression:
        column_name = feature
        value_type = FilterLeaf.FilterLeafValueType.COLUMN_VALUE
        if feature == "_DATA_GROUND_TRUTH":
            column_name = None
            value_type = FilterLeaf.FilterLeafValueType.GROUND_TRUTH
        if not np.isnan(lo) and not np.isnan(hi):
            return FilterExpression(
                filter_leaf=FilterLeaf(
                    value_type=value_type,
                    column_name=column_name,
                    filter_type=FilterLeaf.FilterLeafComparisonType.IN_RANGE,
                    values=[Value(number_value=lo),
                            Value(number_value=hi)]
                )
            )
        else:
            filter_type_lo = FilterLeaf.FilterLeafComparisonType.EQUALS if np.isnan(
                lo
            ) else FilterLeaf.FilterLeafComparisonType.GREATER_THAN_EQUAL_TO
            expression_lo = FilterExpression(
                filter_leaf=FilterLeaf(
                    value_type=value_type,
                    column_name=column_name,
                    filter_type=filter_type_lo,
                    values=[
                        Value(number_value=lo),
                    ]
                )
            )
            filter_type_hi = FilterLeaf.FilterLeafComparisonType.EQUALS if np.isnan(
                hi
            ) else FilterLeaf.FilterLeafComparisonType.LESS_THAN_EQUAL_TO
            expression_hi = FilterExpression(
                filter_leaf=FilterLeaf(
                    value_type=value_type,
                    column_name=column_name,
                    filter_type=filter_type_hi,
                    values=[
                        Value(number_value=hi),
                    ]
                )
            )
            if np.all(np.isnan([lo, hi])):
                # both features contain nan
                return expression_lo
            else:
                return FilterExpression(
                    operator=FilterExpressionOperator.FEO_OR,
                    sub_expressions=[expression_lo, expression_hi],
                )

    @staticmethod
    def _create_categorical_base_expression(
        feature: str, best_val: str, negate: bool
    ) -> FilterExpression:
        filter_type = FilterLeaf.FilterLeafComparisonType.EQUALS
        if negate:
            filter_type = FilterLeaf.FilterLeafComparisonType.NOT_EQUALS
        return FilterExpression(
            filter_leaf=FilterLeaf(
                value_type=FilterLeaf.FilterLeafValueType.COLUMN_VALUE,
                column_name=feature,
                filter_type=filter_type,
                values=[Value(string_value=best_val)]
            )
        )

    @staticmethod
    def _compute_unique_vals(xs: pd.DataFrame,
                             lim: int = 100) -> Mapping[str, np.ndarray]:
        ret = {}
        for feature in xs.columns:
            unique_vals = xs[feature]
            if unique_vals.dtype in [str, object]:
                unique_vals.fillna("", inplace=True)
            unique_vals = unique_vals.unique()
            ret[feature] = np.sort(xs[feature].unique())
            sz = len(ret[feature])
            if sz > lim:
                idxs = np.floor(np.linspace(0, sz - 1, lim)).astype(np.int64)
                ret[feature] = ret[feature][idxs]
        return ret


class AggregatorBaseClass():

    def __init__(
        self, segment_type: InterestingSegment.Type, minimum_size: int,
        minimum_metric_of_interest_threshold: float, size_exponent: float
    ):
        self.segment_type = segment_type
        self.minimum_size = minimum_size
        self.minimum_metric_of_interest_threshold = minimum_metric_of_interest_threshold
        self.size_exponent = size_exponent

    def __call__(self, sums, szs):
        pass


class SimpleAggregator(AggregatorBaseClass):

    def __init__(
        self,
        segment_type,
        minimum_size: int = DEFAULT_MIN_SEGMENT_SIZE,
        minimum_metric_of_interest_threshold: float = 0.0,
        size_exponent: float = 0.25
    ):
        segment_name = InterestingSegment.Type.Name(segment_type)
        self.sign = -1 if segment_name.startswith("LOW") else 1
        super().__init__(
            segment_type, minimum_size, minimum_metric_of_interest_threshold,
            size_exponent
        )

    def __call__(
        self, sums: Sequence[Sequence[float]], szs: Sequence[int]
    ) -> float:
        if any([curr < self.minimum_size for curr in szs]):
            return -np.inf
        if len(sums) == 1:
            ret = self.sign * (sums[0][0] / szs[0])
            if ret < self.minimum_metric_of_interest_threshold:
                return -np.inf
            ret *= szs[0]**self.size_exponent
            return ret
        if len(sums) == 2:
            ret = self.sign * ((sums[0][0] / szs[0]) - (sums[1][0] / szs[1]))
            if ret < self.minimum_metric_of_interest_threshold:
                return -np.inf
            ret *= min(szs)**self.size_exponent
            return ret
        raise TruEraInvalidArgumentError(
            "Currently not supporting aggregators for more than two sets!"
        )


class NumeratorAndDenominatorAggregator(AggregatorBaseClass):

    def __init__(
        self,
        segment_type,
        minimum_size: int = DEFAULT_MIN_SEGMENT_SIZE,
        minimum_metric_of_interest_threshold: float = 0.0,
        size_exponent: float = 0.0
    ):
        segment_name = InterestingSegment.Type.Name(segment_type)
        self.sign = -1 if segment_name.startswith("LOW") else 1
        super().__init__(
            segment_type, minimum_size, minimum_metric_of_interest_threshold,
            size_exponent
        )

    def __call__(
        self, sums: Sequence[Sequence[float]], szs: Sequence[int]
    ) -> float:
        if any([curr < self.minimum_size for curr in szs]):
            return -np.inf
        if any([curr[1] == 0 for curr in sums]):
            return -np.inf
        if len(sums) == 1:
            ret = self.sign * (sums[0][0] / sums[0][1])
            if ret < self.minimum_metric_of_interest_threshold:
                return -np.inf
            ret *= szs[0]**self.size_exponent
            return ret
        if len(sums) == 2:
            ret = self.sign * (
                (sums[0][0] / sums[0][1]) - (sums[1][0] / sums[1][1])
            )
            if ret < self.minimum_metric_of_interest_threshold:
                return -np.inf
            ret *= min(szs)**self.size_exponent
            return ret
        raise TruEraInvalidArgumentError(
            "Currently not supporting aggregators for more than two sets!"
        )


class SegmentSizeAggregator(AggregatorBaseClass):

    def __init__(
        self,
        segment_type,
        minimum_size: int = None,
        minimum_metric_of_interest_threshold: float = 0.0,
        size_exponent: float = None
    ):
        super().__init__(
            segment_type, minimum_size, minimum_metric_of_interest_threshold,
            size_exponent
        )

    def __call__(
        self, sums: Sequence[Sequence[float]], szs: Sequence[int]
    ) -> float:
        if len(sums) == 2:
            ret = np.abs(sums[0][0] - sums[1][0])
            if ret < self.minimum_metric_of_interest_threshold:
                ret = -np.inf
            return ret
        raise TruEraInvalidArgumentError(
            "Under/oversampling aggregator requires two sets!"
        )
