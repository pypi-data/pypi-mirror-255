from typing import Mapping, Optional, Sequence, Tuple, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn import metrics

from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyResult  # pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyType  # pylint: disable=no-name-in-module
from truera.utils.truera_status import TruEraInvalidArgumentError

# Cast all integer types into this type.
INT = int  # python builtin int

# Cast all float types into this type.
FLOAT = float  # python builtin float


def accuracy_score(y_true, y_pred, sample_weight=None, binary=None) -> FLOAT:
    return FLOAT(
        metrics.accuracy_score(y_true, y_pred, sample_weight=sample_weight)
    )


def matthews_corrcoef(y_true, y_pred, sample_weight=None, binary=None) -> FLOAT:
    return FLOAT(
        metrics.matthews_corrcoef(y_true, y_pred, sample_weight=sample_weight)
    )


def roc_auc_score(y_true, y_pred, sample_weight=None, binary=False) -> FLOAT:
    if y_true.max() == 1 and len(y_pred.shape) != 1:
        if y_pred.shape[-1] == 1:
            # reshape into 1d array
            y_pred = np.squeeze(y_pred, axis=-1)
        elif y_pred.shape[-1] == 2:
            # sklearn.metrics requires y_pred is 1d array in binary classification case
            # For metrics.roc_auc_score, y_pred is logits anyway, so
            # y_pred can be collapsed into 1d array by taking logits of class 1
            y_pred = y_pred[..., 1]
        else:
            raise ValueError(
                f"For binary classification, roc_auc_score requires y_pred is a 1d array. Got {y_pred.shape} instead"
            )
    return FLOAT(
        metrics.roc_auc_score(
            y_true, y_pred, sample_weight=sample_weight, multi_class="ovr"
        )
    )


def average_precision_score(y_true,
                            y_pred,
                            sample_weight=None,
                            binary=False) -> Union[FLOAT, Mapping[INT, FLOAT]]:
    # Single float return if binary with one score, otherwise returns mapping.

    if len(y_pred.shape) == 1:
        labels = [0, 1]
        return FLOAT(
            metrics.average_precision_score(
                y_true, y_pred, sample_weight=sample_weight
            )
        )
    else:
        labels = np.arange(y_pred.shape[-1])
        return {
            INT(label):
                FLOAT(
                    metrics.average_precision_score(
                        y_true == label,
                        y_pred[:, i],
                        sample_weight=sample_weight
                    )
                ) for i, label in enumerate(labels)
        }


def precision_score(y_true, y_pred, sample_weight=None, binary=False) -> FLOAT:
    avg_mode = "binary" if binary else "micro"
    return FLOAT(
        metrics.precision_score(
            y_true, y_pred, sample_weight=sample_weight, average=avg_mode
        )
    )


def recall_score(y_true, y_pred, sample_weight=None, binary=False) -> FLOAT:
    avg_mode = "binary" if binary else "micro"
    return FLOAT(
        metrics.recall_score(
            y_true, y_pred, sample_weight=sample_weight, average=avg_mode
        )
    )


def f1_score(y_true, y_pred, sample_weight=None, binary=False) -> FLOAT:
    avg_mode = "binary" if binary else "micro"
    return FLOAT(
        metrics.f1_score(
            y_true, y_pred, sample_weight=sample_weight, average=avg_mode
        )
    )


def jaccard_score(y_true, y_pred, sample_weight=None, binary=False) -> FLOAT:
    avg_mode = "binary" if binary else "micro"
    return FLOAT(
        metrics.jaccard_score(
            y_true, y_pred, sample_weight=sample_weight, average=avg_mode
        )
    )


def confusion_matrix(
    y_true,
    y_pred,
    sample_weight=None,
    binary=False,
    return_matrix=False
) -> Union[Tuple[Sequence[INT], Sequence[INT]], npt.NDArray[INT]]:
    # Second return type option if return_matrix=True.

    labels = np.sort(np.unique(np.concatenate((y_true, y_pred)))).astype(INT)

    conf_matrix = metrics.confusion_matrix(
        y_true, y_pred, labels=labels, sample_weight=sample_weight
    ).astype(INT)

    if return_matrix:
        return conf_matrix

    elif len(labels) == 1:
        # returns tn, fp, fn, tp
        if int(labels[0]) == 0:
            return [np.diag(conf_matrix)[0], 0, 0, 0], labels
        return [0, 0, 0, np.diag(conf_matrix)[0]], labels
    elif len(labels) == 2:
        return list(conf_matrix.ravel()), labels
    else:
        tp = np.diag(conf_matrix)
        fp = conf_matrix.sum(axis=0) - tp
        fn = conf_matrix.sum(axis=1) - tp
        tn = conf_matrix.sum() - (fp + fn + tp)
        return [tn, fp, fn, tp], labels


def gini_score(y_true, y_pred, sample_weight=None, binary=False) -> FLOAT:
    return FLOAT(
        2 * roc_auc_score(
            y_true, y_pred, sample_weight=sample_weight, binary=binary
        ) - 1
    )


def accuracy_ratio_score(
    y_true, y_pred, sample_weight=None, binary=False
) -> FLOAT:
    return FLOAT(
        gini_score(y_true, y_pred, sample_weight=sample_weight, binary=binary) /
        (1 - np.mean(y_true))
    )


def segment_generalized_roc_auc_score(
    y_true,
    y_pred,
    all_y_true,
    all_y_pred,
    sample_weight=None,
    binary=False
) -> FLOAT:

    if y_true is all_y_true and y_pred is all_y_pred:
        return FLOAT(roc_auc_score(y_true, y_pred, sample_weight=sample_weight))

    if sample_weight is not None:
        raise TruEraInvalidArgumentError(
            "Segment generalized AUC cannot be computed with sample weights."
        )

    y_pred_0 = y_pred[y_true == 0]
    y_pred_1 = y_pred[y_true == 1]
    sorted_all_y_pred_0 = sorted(all_y_pred[all_y_true == 0])
    sorted_all_y_pred_1 = sorted(all_y_pred[all_y_true == 1])
    num_y_pred_0 = len(sorted_all_y_pred_0)
    num_y_pred_1 = len(sorted_all_y_pred_1)
    if num_y_pred_0 + num_y_pred_1 != len(all_y_pred):
        raise TruEraInvalidArgumentError(
            "Segment generalized AUC cannot be computed for non-binary labels."
        )
    if num_y_pred_0 == 0 or num_y_pred_1 == 0:
        raise TruEraInvalidArgumentError(
            "Segment generalized AUC cannot be computed for labels that only contain a single class."
        )
    pointwise_aucs = np.zeros(y_true.shape)
    idxs = (
        np.searchsorted(sorted_all_y_pred_1, y_pred_0, side="left") +
        np.searchsorted(sorted_all_y_pred_1, y_pred_0, side="right")
    ) / 2
    pointwise_aucs[y_true == 0] = (num_y_pred_1 - idxs) / num_y_pred_1
    idxs = (
        np.searchsorted(sorted_all_y_pred_0, y_pred_1, side="left") +
        np.searchsorted(sorted_all_y_pred_0, y_pred_1, side="right")
    ) / 2
    pointwise_aucs[y_true == 1] = idxs / num_y_pred_0

    return FLOAT(np.mean(pointwise_aucs))


def segment_generalized_gini_score(
    y_true,
    y_pred,
    all_y_true,
    all_y_pred,
    sample_weight=None,
    binary=False
) -> FLOAT:

    return FLOAT(
        2 * segment_generalized_roc_auc_score(
            y_true, y_pred, all_y_true, all_y_pred, sample_weight=sample_weight
        ) - 1
    )


def segment_generalized_accuracy_ratio_score(
    y_true,
    y_pred,
    all_y_true,
    all_y_pred,
    sample_weight=None,
    binary=False
) -> FLOAT:
    return FLOAT(
        segment_generalized_gini_score(
            y_true, y_pred, all_y_true, all_y_pred, sample_weight=sample_weight
        ) / (1 - np.mean(all_y_true))
    )


def log_loss_score(
    y_true, y_pred, sample_weight=None, binary=False, eps=1e-15
) -> FLOAT:
    return FLOAT(np.mean(log_loss_score_pointwise(y_true, y_pred, eps)))


def true_positive_rate(y_true,
                       y_pred,
                       sample_weight=None,
                       binary=False) -> Union[FLOAT, Mapping[INT, FLOAT]]:
    [_, _, fn, tp], labels = confusion_matrix(
        y_true, y_pred, sample_weight=sample_weight, binary=binary
    )
    # tp, tn are single floats for binary cases and 1-d numpy arrays otherwise

    tpr = tp.astype(float) / (tp + fn).astype(float)

    if len(labels) <= 2:
        # in binary case, return raw value
        return FLOAT(tpr)

    # in multiclass case, return one-vs-rest TPR for each class
    return {INT(l): FLOAT(i) for l, i in zip(labels, tpr)}


def false_positive_rate(y_true,
                        y_pred,
                        sample_weight=None,
                        binary=False) -> Union[FLOAT, Mapping[INT, FLOAT]]:
    [tn, fp, _, _], labels = confusion_matrix(
        y_true, y_pred, sample_weight=sample_weight, binary=binary
    )
    # tn, fp are single floats for binary cases and 1-d numpy arrays otherwise

    fpr = fp.astype(float) / (fp + tn).astype(float)

    if len(labels) <= 2:
        # in binary case, return raw value
        return FLOAT(fpr)

    # in multiclass case, return one-vs-rest FPR for each class
    return {INT(l): FLOAT(i) for l, i in zip(labels, fpr)}


def false_negative_rate(y_true,
                        y_pred,
                        sample_weight=None,
                        binary=False) -> Union[FLOAT, Mapping[INT, FLOAT]]:
    tpr = true_positive_rate(
        y_true, y_pred, sample_weight=sample_weight, binary=binary
    )
    if isinstance(tpr, Mapping):
        # multiclass: compute one-vs-rest FNR for each class
        return {l: 1 - i for l, i in tpr.items()}

    return 1 - tpr


def true_negative_rate(y_true,
                       y_pred,
                       sample_weight=None,
                       binary=False) -> Union[FLOAT, Mapping[INT, FLOAT]]:
    fpr = false_positive_rate(
        y_true, y_pred, sample_weight=sample_weight, binary=binary
    )
    if isinstance(fpr, Mapping):
        # multiclass: compute one-vs-rest TNR for each class
        return {l: 1 - i for l, i in fpr.items()}
    return 1 - fpr


def negative_predictive_value(
    y_true,
    y_pred,
    sample_weight=None,
    binary=False
) -> Union[FLOAT, Mapping[INT, FLOAT]]:
    [tn, _, fn, _], labels = confusion_matrix(
        y_true, y_pred, sample_weight=sample_weight, binary=binary
    )
    # tn, fn are single floats for binary cases and 1-d numpy arrays otherwise

    npv = tn.astype(float) / (tn + fn).astype(float)

    if len(labels) <= 2:
        # return number in binary case
        return FLOAT(npv)

    return {INT(l): FLOAT(i) for l, i in zip(labels, npv)}


def rmse_score(y_true, y_pred, sample_weight=None) -> FLOAT:
    return FLOAT(
        np.sqrt(
            metrics.mean_squared_error(
                y_true, y_pred, sample_weight=sample_weight
            )
        )
    )


def mean_absolute_percentage_error(
    y_true, y_pred, sample_weight=None, eps=1e-8
) -> FLOAT:

    if sample_weight is None:
        sample_weight = 1
    nums = y_true - y_pred
    dens = np.maximum(y_true, eps)
    ret = np.sum(sample_weight * np.abs(nums / dens))
    ret *= 100 / len(y_true)

    return FLOAT(ret)


def weighted_mean_absolute_percentage_error(
    y_true, y_pred, sample_weight=None
) -> FLOAT:

    if sample_weight is None:
        sample_weight = 1
    num = np.sum(sample_weight * np.abs(y_true - y_pred))
    den = np.sum(sample_weight * np.abs(y_true))

    return FLOAT(num / den)


def mean_percentage_error(y_true, y_pred, sample_weight=None) -> FLOAT:
    if sample_weight is None:
        sample_weight = 1
    return FLOAT(
        np.sum(sample_weight * (y_true - y_pred) / y_true) / len(y_true)
    )


def normalized_mean_bias(y_true, y_pred, sample_weight=None) -> FLOAT:
    if sample_weight is None:
        sample_weight = 1
    num = np.sum(sample_weight * (y_true - y_pred))
    den = np.sum(sample_weight * y_true)
    return FLOAT(num / den)


def mean_squared_log_error(y_true, y_pred, sample_weight=None) -> FLOAT:
    if np.any(y_pred < 0) or np.any(y_true < 0):
        raise TruEraInvalidArgumentError(
            "Mean Squared Logarithmic Error cannot be used when predictions or targets contain negative values."
        )
    return FLOAT(
        metrics.mean_squared_log_error(
            y_true, y_pred, sample_weight=sample_weight
        )
    )


def normalized_discounted_cumulative_gain(
    y_true: Sequence[FLOAT],
    y_pred: Sequence[FLOAT],
    groups: Sequence[Union[INT, str]],
    num_per_group: INT,
    sample_weight: Optional[Sequence[FLOAT]] = None
) -> FLOAT:
    if num_per_group is None or num_per_group <= 0:
        raise TruEraInvalidArgumentError(
            f"Normalized Discounted Cumulative Gain cannot be used without a valid `num_per_group` argument ('{num_per_group}' was provided)."
        )
    if groups is None or not (
        y_pred.shape[0] == groups.shape[0] == y_true.shape[0]
    ):
        raise TruEraInvalidArgumentError(
            f"Normalized Discounted Cumulative Gain cannot be used without a valid list of group IDs. Please check the `groups` argument."
        )

    joined_df = pd.DataFrame(
        {
            'preds': y_pred.flatten(),
            'labels': y_true.flatten(),
            'group_ids': groups.flatten()
        }
    )
    group_ids = joined_df["group_ids"].unique()
    joined_df = joined_df.groupby('group_ids')

    ndcg_list = []
    for group_id in group_ids:
        group_id_df = joined_df.get_group(group_id)
        if group_id_df.shape[0] >= num_per_group:  # group_count >= K
            preds = [group_id_df["preds"].to_list()]
            labels = [group_id_df["labels"].to_list()]
            ndcg_list.append(
                metrics.ndcg_score(
                    labels,
                    preds,
                    k=num_per_group,
                    sample_weight=sample_weight,
                    ignore_ties=True
                )
            )

    return np.mean(ndcg_list)


# pointwise metrics (i.e., non-aggregated metrics)
# should reflect behavior of corresponding aggregated metrics
def auc_pointwise(y_true, y_pred) -> npt.NDArray[FLOAT]:

    # TODO: have segment_generalized_roc_auc_score hook into here
    all_ys_pred_0 = y_pred[y_true == 0]
    all_ys_pred_1 = y_pred[y_true == 1]
    sorted_all_ys_pred_0 = sorted(all_ys_pred_0)
    sorted_all_ys_pred_1 = sorted(all_ys_pred_1)
    if len(all_ys_pred_0) + len(all_ys_pred_1) != len(y_pred):
        raise TruEraInvalidArgumentError(
            "Low pointwise-AUC segments cannot be computed for non-binary labels."
        )
    if len(all_ys_pred_0) == 0 or len(all_ys_pred_1) == 0:
        raise TruEraInvalidArgumentError(
            "Low pointwise-AUC segments cannot be computed for labels that only contain a single class."
        )
    pointwise_aucs = np.zeros(y_true.shape)
    idxs = (
        np.searchsorted(sorted_all_ys_pred_1, all_ys_pred_0, side="left") +
        np.searchsorted(sorted_all_ys_pred_1, all_ys_pred_0, side="right")
    ) / 2
    # idx has same shape as arr[y_true == 0]
    pointwise_aucs[y_true == 0
                  ] = (len(all_ys_pred_1) - idxs) / len(sorted_all_ys_pred_1)
    idxs = (
        np.searchsorted(sorted_all_ys_pred_0, all_ys_pred_1, side="left") +
        np.searchsorted(sorted_all_ys_pred_0, all_ys_pred_1, side="right")
    ) / 2
    # idx has same shape as arr[y_true == 1]
    pointwise_aucs[y_true == 1] = idxs / len(sorted_all_ys_pred_0)
    return pointwise_aucs.astype(FLOAT)


def classification_accuracy_pointwise(y_true, y_pred) -> npt.NDArray[FLOAT]:
    # NOTE: np.abs returns Series here
    return np.abs(y_true == y_pred).to_numpy().astype(FLOAT)


def confusion_matrix_pointwise(
    y_true: pd.Series, y_pred: pd.Series, quadrants: Sequence[str]
) -> pd.Series:
    """
    Returns a pandas series of bools indicating which points belong to one of
    the confusion matrix quadrants included in the `quadrants` list.
    """

    ret = None

    for quadrant in quadrants:
        if quadrant == "TP":
            curr = ((y_true == y_pred) & (y_pred == 1))
        elif quadrant == "FP":
            curr = ((y_true != y_pred) & (y_pred == 1))
        elif quadrant == "TN":
            curr = ((y_true == y_pred) & (y_pred == 0))
        elif quadrant == "FN":
            curr = ((y_true != y_pred) & (y_pred == 0))
        else:
            raise ValueError(f"Invalid quadrant: {quadrant}!")
        ret = curr if ret is None else (ret | curr)

    return ret


def absolute_error_pointwise(y_true, y_pred) -> npt.NDArray[FLOAT]:
    return np.abs(y_true - y_pred).to_numpy().astype(FLOAT)


def squared_error_pointwise(y_true, y_pred) -> npt.NDArray[FLOAT]:
    return np.power(y_true - y_pred, 2).to_numpy().astype(FLOAT)


def squared_log_error_pointwise(y_true, y_pred) -> npt.NDArray[FLOAT]:
    if np.any(y_true < 0) or np.any(y_pred < 0):
        raise ValueError(
            "Mean Squared Logarithmic Error cannot be used when "
            "targets contain negative values."
        )
    return squared_error_pointwise(np.log1p(y_true), np.log1p(y_pred))


def log_loss_score_pointwise(y_true, y_pred, eps=1e-15) -> npt.NDArray[FLOAT]:
    # We don't use sklearn.metrics.log_loss as it enforces y_true to have exactly two values. We do assume y_true is a subset of {0, 1} though.
    y_true = y_true.astype(float)
    y_pred = y_pred.astype(float)
    y_pred = np.clip(y_pred, eps, 1 - eps)
    return (-y_true * np.log(y_pred) -
            (1 - y_true) * np.log(1 - y_pred)).astype(FLOAT)


def get_what_if_metric(
    split_metric_val: float, segment_metric_val: float, split_size: int,
    segment_size: int
) -> FLOAT:
    """
    The "what if" metric assumes that the model can be retrained to improve the metric on the segment without impacting the metric outside of the segment. 

    Denote $M$ as a metric on a set of points and $N$ be the size of a set of points. The metric outside the segment, $M_{\neg\text{seg}}$ is estimated using

    $M_{\neg\text{seg}} = \frac{M_{\text{split}}N_{\text{split}} - M_{\text{seg}}N_{\text{seg}}}{N_{\neg\text{seg}}}$.

    Then, the "what if" metric, $M_{\text{what if}}$, for the split is calculated as follows,

    $M_{\text{what if}} = \frac{M_{\text{split}}N_{\text{seg}} + M_{\neg\text{seg}}N_{\neg\text{seg}}}{N_{\text{split}}}$.

    Args:
        split_metric_val: Average of metric within the split
        segment_metric_val: Average of metric within the segment
        split_size: Size of data split
        segment_size: Size of data segment (<= split_size)

    Returns:
        "What if" metric for the split if the segment's performance was brought up to the performance of the split
    """
    if segment_size < split_size:
        not_seg_size = split_size - segment_size
        not_seg_metric_val = (
            split_metric_val * split_size - segment_metric_val * segment_size
        ) / not_seg_size
        what_if_metric = (
            split_metric_val * segment_size + not_seg_metric_val * not_seg_size
        ) / split_size
        return FLOAT(what_if_metric)
    else:
        # when segment_size == split_size; fix for zero division error
        return FLOAT(split_metric_val)


REGRESSION_SCORE_ACCURACIES = [
    AccuracyType.Type.RMSE, AccuracyType.Type.MSE, AccuracyType.Type.MAE,
    AccuracyType.Type.MSLE, AccuracyType.Type.R_SQUARED,
    AccuracyType.Type.EXPLAINED_VARIANCE, AccuracyType.Type.MAPE,
    AccuracyType.Type.WMAPE, AccuracyType.Type.MEAN_PERCENTAGE_ERROR,
    AccuracyType.Type.NORMALIZED_MEAN_BIAS
]
REGRESSION_SCORE_ACCURACIES_STR = [
    AccuracyType.Type.Name(i) for i in REGRESSION_SCORE_ACCURACIES
]

RANKING_SCORE_ACCURACIES = [AccuracyType.Type.NDCG]
RANKING_SCORE_ACCURACIES_STR = [
    AccuracyType.Type.Name(i) for i in RANKING_SCORE_ACCURACIES
]

CLASSIFICATION_SCORE_ACCURACIES = [
    AccuracyType.Type.CLASSIFICATION_ACCURACY,
    AccuracyType.Type.MATTHEWS_CORRCOEF,
    AccuracyType.Type.JACCARD_INDEX,
]
CLASSIFICATION_SCORE_ACCURACIES_STR = [
    AccuracyType.Type.Name(i) for i in CLASSIFICATION_SCORE_ACCURACIES
]

BINARY_CLASSIFICATION_SCORE_ACCURACIES = [
    AccuracyType.Type.PRECISION,
    AccuracyType.Type.RECALL,
    AccuracyType.Type.F1,
    AccuracyType.Type.TRUE_POSITIVE_RATE,
    AccuracyType.Type.FALSE_POSITIVE_RATE,
    AccuracyType.Type.TRUE_NEGATIVE_RATE,
    AccuracyType.Type.FALSE_NEGATIVE_RATE,
    AccuracyType.Type.NEGATIVE_PREDICTIVE_VALUE,
]
BINARY_CLASSIFICATION_SCORE_ACCURACIES_STR = [
    AccuracyType.Type.Name(i) for i in BINARY_CLASSIFICATION_SCORE_ACCURACIES
]

MULTICLASS_CLASSIFICATION_SCORE_ACCURACIES = []
MULTICLASS_CLASSIFICATION_SCORE_ACCURACIES_STR = [
    AccuracyType.Type.Name(i)
    for i in MULTICLASS_CLASSIFICATION_SCORE_ACCURACIES
]

PROBITS_OR_LOGITS_SCORE_ACCURACIES = [
    AccuracyType.Type.AUC, AccuracyType.SEGMENT_GENERALIZED_AUC,
    AccuracyType.Type.GINI, AccuracyType.SEGMENT_GENERALIZED_GINI,
    AccuracyType.Type.AVERAGE_PRECISION, AccuracyType.Type.ACCURACY_RATIO,
    AccuracyType.Type.SEGMENT_GENERALIZED_ACCURACY_RATIO
]
PROBITS_OR_LOGITS_SCORE_ACCURACIES_STR = [
    AccuracyType.Type.Name(i) for i in PROBITS_OR_LOGITS_SCORE_ACCURACIES
]

SEGMENT_GENERALIZED_METRICS = [
    AccuracyType.Type.SEGMENT_GENERALIZED_AUC,
    AccuracyType.Type.SEGMENT_GENERALIZED_GINI,
    AccuracyType.Type.SEGMENT_GENERALIZED_ACCURACY_RATIO
]

PROBITS_SCORE_ACCURACIES = [AccuracyType.Type.LOG_LOSS]

ACCURACY_METRIC_MAP = {
    AccuracyType.Type.AUC:
        (roc_auc_score, AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER),
    AccuracyType.Type.GINI:
        (gini_score, AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER),
    AccuracyType.Type.ACCURACY_RATIO:
        (
            accuracy_ratio_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.SEGMENT_GENERALIZED_AUC:
        (
            segment_generalized_roc_auc_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.SEGMENT_GENERALIZED_GINI:
        (
            segment_generalized_gini_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.SEGMENT_GENERALIZED_ACCURACY_RATIO:
        (
            segment_generalized_accuracy_ratio_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.LOG_LOSS:
        (log_loss_score, AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER),
    AccuracyType.Type.CLASSIFICATION_ACCURACY:
        (
            accuracy_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.PRECISION:
        (
            precision_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.RECALL:
        (recall_score, AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER),
    AccuracyType.Type.F1:
        (f1_score, AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER),
    AccuracyType.Type.TRUE_POSITIVE_RATE:
        (
            true_positive_rate,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.FALSE_POSITIVE_RATE:
        (
            false_positive_rate,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.TRUE_NEGATIVE_RATE:
        (
            true_negative_rate,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.FALSE_NEGATIVE_RATE:
        (
            false_negative_rate,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.NEGATIVE_PREDICTIVE_VALUE:
        (
            negative_predictive_value,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.MATTHEWS_CORRCOEF:
        (
            matthews_corrcoef,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.JACCARD_INDEX:
        (jaccard_score, AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER),
    AccuracyType.Type.AVERAGE_PRECISION:
        (
            average_precision_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.RMSE:
        (rmse_score, AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER),
    AccuracyType.Type.MSE:
        (
            metrics.mean_squared_error,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.MAE:
        (
            metrics.mean_absolute_error,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.MSLE:
        (
            mean_squared_log_error,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.R_SQUARED:
        (
            metrics.r2_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.EXPLAINED_VARIANCE:
        (
            metrics.explained_variance_score,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
    AccuracyType.Type.MAPE:
        (
            mean_absolute_percentage_error,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.WMAPE:
        (
            weighted_mean_absolute_percentage_error,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.MEAN_PERCENTAGE_ERROR:
        (
            mean_percentage_error,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.NORMALIZED_MEAN_BIAS:
        (
            normalized_mean_bias,
            AccuracyResult.AccuracyInterpretation.LOWER_IS_BETTER
        ),
    AccuracyType.Type.NDCG:
        (
            normalized_discounted_cumulative_gain,
            AccuracyResult.AccuracyInterpretation.HIGHER_IS_BETTER
        ),
}

# TODO: remove and use BINARY_CLASSIFICATION_SCORE_ACCURACIES once all metrics are supported/validated
SUPPORTED_ACCURACY_TYPES_FOR_THRESHOLDED_PREDS_AGG = [
    AccuracyType.Type.PRECISION,
    AccuracyType.Type.RECALL,
    AccuracyType.Type.TRUE_POSITIVE_RATE,
    AccuracyType.Type.FALSE_POSITIVE_RATE,
    AccuracyType.Type.TRUE_NEGATIVE_RATE,
    AccuracyType.Type.FALSE_NEGATIVE_RATE,
]
