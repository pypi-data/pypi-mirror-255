from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
import logging
from typing import Mapping, Optional, Sequence, Set

import numpy as np
import pandas as pd

from truera.protobuf.public.data.filter_pb2 import \
    FilterExpression  # pylint: disable=no-name-in-module
from truera.protobuf.public.data.filter_pb2 import \
    FilterExpressionOperator  # pylint: disable=no-name-in-module
from truera.protobuf.public.data.filter_pb2 import \
    FilterLeaf  # pylint: disable=no-name-in-module
from truera.protobuf.public.qoi_pb2 import \
    QuantityOfInterest  # pylint: disable=no-name-in-module
from truera.utils import filter_constants
from truera.utils.data_constants import NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME


# Logical representation of the data required to apply a filter.
@dataclass
class FilterRequirements:
    column_names: Set[str] = field(default_factory=set)
    segmentation_ids: Set[str] = field(default_factory=set)
    requires_ground_truth: bool = False
    requires_index: bool = False
    requires_ranking_group_id: bool = False
    model_ids_to_score_type: Mapping[str, Set[int]] = field(
        default_factory=lambda: defaultdict(set)
    )


def _extractValue(value):
    which_oneof = value.WhichOneof("kind")
    if which_oneof == "number_value":
        return value.number_value
    elif which_oneof == "string_value":
        return value.string_value
    assert False, "Not support value type: {}, value: {}".format(
        which_oneof, value
    )


def _stringify_extract_value(value):
    value = _extractValue(value)
    if isinstance(value, str):
        value = f"'{value}'"
    return value


class FilterProcessor(object):
    INDEX_LABEL = "_truera_index"
    logger = logging.getLogger(__name__)

    # Tells what kind of data is required to apply this filter.
    @classmethod
    def get_filter_requirements(
        cls,
        filter_exp: FilterExpression,
        filter_requirements: Optional[FilterRequirements] = None
    ) -> FilterRequirements:
        if not filter_requirements:
            filter_requirements = FilterRequirements()
        if filter_exp.WhichOneof("value") == "filter_leaf":
            if filter_exp.filter_leaf.value_type == FilterLeaf.FilterLeafValueType.COLUMN_VALUE:
                filter_requirements.column_names.add(
                    filter_exp.filter_leaf.column_name
                )
            if filter_exp.filter_leaf.value_type == FilterLeaf.FilterLeafValueType.SEGMENT:
                filter_requirements.segmentation_ids.add(
                    filter_exp.filter_leaf.segmentation_id
                )
            if filter_exp.filter_leaf.value_type in [
                FilterLeaf.FilterLeafValueType.OUTPUT,
                FilterLeaf.FilterLeafValueType.RANKING_GROUP_ID
            ]:
                model_id = filter_exp.filter_leaf.model_id if filter_exp.filter_leaf.model_id else filter_constants.GENERIC_MODEL_ID
                filter_requirements.model_ids_to_score_type[model_id].add(
                    filter_exp.filter_leaf.score_type
                )
                if filter_exp.filter_leaf.value_type == FilterLeaf.FilterLeafValueType.RANKING_GROUP_ID:
                    filter_requirements.requires_ranking_group_id = True
            if filter_exp.filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH:
                filter_requirements.requires_ground_truth = True
            if filter_exp.filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH_CONFORMANCE:
                filter_requirements.requires_ground_truth = True
            if filter_exp.filter_leaf.value_type == FilterLeaf.FilterLeafValueType.INDEX:
                filter_requirements.requires_index = True
        else:
            for sub_filter in filter_exp.sub_expressions:
                FilterProcessor.get_filter_requirements(
                    sub_filter, filter_requirements=filter_requirements
                )
        return filter_requirements

    # Data should contain all the series required to allow filtering, as indicated by get_filter_requirements.
    @classmethod
    def filter(
        cls, data: pd.DataFrame, filter_exp: FilterExpression
    ) -> np.ndarray:
        if filter_exp.HasField("filter_leaf"):
            return FilterProcessor._filterLeaf(data, filter_exp.filter_leaf)
        else:
            assert len(
                filter_exp.sub_expressions
            ) > 0, "No sub expressions for filter operator"
            op_type = filter_exp.operator
            sub_filter_results = [
                FilterProcessor.filter(data, sub_filter)
                for sub_filter in filter_exp.sub_expressions
            ]
            if op_type == FilterExpressionOperator.FEO_NOT:
                assert len(sub_filter_results
                          ) == 1, "Length of sub_filter_results is {}".format(
                              len(sub_filter_results)
                          )
                return np.logical_not(sub_filter_results[0])
            else:  # OR, AND operators
                default_value = op_type == FilterExpressionOperator.FEO_AND
                return_val = np.full_like(sub_filter_results[0], default_value)
                combiner = np.logical_and if op_type == FilterExpressionOperator.FEO_AND else np.logical_or
                for sub_filter_result in sub_filter_results:
                    return_val = combiner(return_val, sub_filter_result)
                return return_val

    @classmethod
    def _filterLeaf(
        cls, data: pd.DataFrame, filter_leaf: FilterLeaf
    ) -> np.ndarray:
        column_data: pd.Series = pd.Series()
        if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.COLUMN_VALUE:
            column_data = data[filter_leaf.column_name]
        elif filter_leaf.value_type == FilterLeaf.FilterLeafValueType.SEGMENT:
            column_data = data[filter_leaf.segmentation_id]
        elif filter_leaf.value_type == FilterLeaf.FilterLeafValueType.OUTPUT:
            model_output_column_name = filter_constants.get_filter_column_name_for_model_output(
                filter_leaf.score_type, filter_leaf.model_id
            )
            column_data = data[model_output_column_name]
        elif filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH_CONFORMANCE:
            column_data1: pd.Series = data[
                filter_constants.get_filter_column_name_for_model_output(
                    filter_leaf.score_type, filter_leaf.model_id
                )]
            column_data2: pd.Series = data[
                filter_constants.FILTER_GROUND_TRUTH_NAME]
            column_data = (column_data1 == column_data2)
        elif filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH:
            column_data = data[filter_constants.FILTER_GROUND_TRUTH_NAME]
        elif filter_leaf.value_type == FilterLeaf.FilterLeafValueType.INDEX:
            column_data = data[FilterProcessor.INDEX_LABEL]
        elif filter_leaf.value_type == FilterLeaf.FilterLeafValueType.RANKING_GROUP_ID:
            # locally, just use the normalized ranking group id
            column_data = data[NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME]
        extracted_values = [
            _extractValue(value) for value in filter_leaf.values
        ]
        cls.logger.debug(
            "Values: %s, %s", type(extracted_values[0]), extracted_values
        )

        filter_series_value = None
        filter_type = filter_leaf.filter_type
        if filter_type == FilterLeaf.FilterLeafComparisonType.EQUALS:
            if np.isreal(extracted_values[0]) and np.isnan(extracted_values[0]):
                filter_series_value = np.isnan(column_data)
            else:
                filter_series_value = column_data == extracted_values[0]
        elif filter_type == FilterLeaf.FilterLeafComparisonType.NOT_EQUALS:
            if np.isreal(extracted_values[0]) and np.isnan(extracted_values[0]):
                filter_series_value = ~np.isnan(column_data)
            else:
                filter_series_value = column_data != extracted_values[0]
        elif filter_type == FilterLeaf.FilterLeafComparisonType.LESS_THAN:
            filter_series_value = column_data < extracted_values[0]
        elif filter_type == FilterLeaf.FilterLeafComparisonType.LESS_THAN_EQUAL_TO:
            filter_series_value = column_data <= extracted_values[0]
        elif filter_type == FilterLeaf.FilterLeafComparisonType.GREATER_THAN:
            filter_series_value = column_data > extracted_values[0]
        elif filter_type == FilterLeaf.FilterLeafComparisonType.GREATER_THAN_EQUAL_TO:
            filter_series_value = column_data >= extracted_values[0]
        elif filter_type == FilterLeaf.FilterLeafComparisonType.IN_LIST:
            # TODO(apoorv) Handle nan values.
            filter_series_value = column_data.isin(extracted_values)
        elif filter_type == FilterLeaf.FilterLeafComparisonType.NOT_IN_LIST:
            filter_series_value = ~column_data.isin(extracted_values)
        elif filter_type == FilterLeaf.FilterLeafComparisonType.IN_RANGE or \
                filter_type == FilterLeaf.FilterLeafComparisonType.NOT_IN_RANGE:
            assert len(extracted_values
                      ) == 2, "RANGE filter supports 2 values. Got={}".format(
                          len(extracted_values)
                      )
            left_operation = column_data.gt(extracted_values[0]) if filter_leaf.range_options.lowerStrict \
                else column_data.ge(extracted_values[0])
            right_operation = column_data.lt(extracted_values[1]) if filter_leaf.range_options.upperStrict \
                else column_data.le(extracted_values[1])
            filter_series_value = left_operation & right_operation
            if filter_type == FilterLeaf.FilterLeafComparisonType.NOT_IN_RANGE:
                filter_series_value = ~(left_operation & right_operation)

        return filter_series_value

    @classmethod
    def stringify_filter(
        cls, filter_exp: FilterExpression, ingestable: bool = False
    ) -> str:
        if filter_exp.HasField("filter_leaf"):
            return cls._stringify_filter_leaf(
                filter_exp.filter_leaf, ingestable
            )
        else:
            assert len(
                filter_exp.sub_expressions
            ) > 0, "No sub expressions for filter operator"
            sub_filter_results = sorted(
                [
                    cls.stringify_filter(sub_filter, ingestable)
                    for sub_filter in filter_exp.sub_expressions
                ]
            )
            return cls._stringify_filter_op(
                filter_exp.operator, sub_filter_results
            )

    @classmethod
    def _stringify_filter_op(
        cls, op_type: FilterExpressionOperator,
        sub_filters: Sequence[FilterExpression]
    ) -> str:
        if op_type == FilterExpressionOperator.FEO_NOT:
            if len(sub_filters) == 1:
                sub_filters = sub_filters[0]
            return f"NOT {sub_filters}"
        if op_type == FilterExpressionOperator.FEO_AND:
            return " AND ".join(sub_filters)
        if op_type == FilterExpressionOperator.FEO_OR:
            return " OR ".join(sub_filters)
        raise ValueError(f"Unknown filter operation type {op_type}")

    @classmethod
    def _stringify_filter_leaf(
        cls, filter_leaf: FilterLeaf, ingestable: bool
    ) -> str:
        value_type = cls._stringify_filter_value_type(filter_leaf, ingestable)
        filter_type = cls._stringify_filter_type(filter_leaf)
        values = [
            _stringify_extract_value(value) for value in filter_leaf.values
        ]
        if len(values) == 1:
            values = values[0]
        return f"{value_type} {filter_type} {values}"

    @classmethod
    def _stringify_filter_value_type(
        cls, filter_leaf: FilterLeaf, ingestable: bool
    ) -> str:
        if ingestable:
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.COLUMN_VALUE:
                if " " in filter_leaf.column_name:
                    return f'"{filter_leaf.column_name}"'
                return filter_leaf.column_name
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.OUTPUT:
                stringified_value = filter_constants.get_filter_column_name_for_model_output(
                    filter_leaf.score_type, filter_leaf.model_id
                )
                if " " in stringified_value:
                    return f'"{stringified_value}"'
                return stringified_value
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH:
                return filter_constants.FILTER_GROUND_TRUTH_NAME
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.RANKING_GROUP_ID:
                return filter_constants.FILTER_RANKING_GROUP_ID_NAME
        else:
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.COLUMN_VALUE:
                return f"COLUMN: {filter_leaf.column_name}"
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.SEGMENT:
                return f"SEGMENT: {filter_leaf.segmentation_id}"
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.OUTPUT:
                return f"MODEL SCORE TYPE: {QuantityOfInterest.Name(filter_leaf.score_type)}"
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH:
                return "GROUND TRUTH"
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.GROUND_TRUTH_CONFORMANCE:
                return "GROUND TRUTH CONFORMANCE"
            if filter_leaf.value_type == FilterLeaf.FilterLeafValueType.INDEX:
                return "ROW INDEX"
        raise ValueError(f"Unknown filter value type {filter_leaf.value_type}")

    @classmethod
    def _stringify_filter_type(cls, filter_leaf: FilterLeaf) -> str:
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.EQUALS:
            return '='
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.NOT_EQUALS:
            return "!="
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.LESS_THAN:
            return "<"
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.LESS_THAN_EQUAL_TO:
            return "<="
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.GREATER_THAN:
            return ">"
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.GREATER_THAN_EQUAL_TO:
            return ">="
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.IN_LIST:
            return "in"
        if filter_leaf.filter_type == FilterLeaf.FilterLeafComparisonType.IN_RANGE:
            return "in_range"
        raise ValueError(f"Unknown filter type {filter_leaf.filter_type}")

    @classmethod
    def _convert_nan_features_to_float_in_filter_expression(
        cls, filter_expression: FilterExpression
    ):
        if filter_expression.WhichOneof("value") == "filter_leaf":
            # base case; sets number_value, unsets string_value
            if filter_expression.filter_leaf.values[0].string_value == "NaN":
                filter_expression.filter_leaf.values[0].number_value = np.nan
        else:
            # recursive case
            for inner_expression in filter_expression.sub_expressions:
                inner_expression = FilterProcessor._convert_nan_features_to_float_in_filter_expression(
                    inner_expression
                )
        return filter_expression

    @classmethod
    def _convert_nan_features_to_string_in_filter_expression(
        cls, filter_expression: FilterExpression
    ):
        if filter_expression.WhichOneof("value") == "filter_leaf":
            # base case; sets string_value, unsets number_value
            if np.isnan(filter_expression.filter_leaf.values[0].number_value):
                filter_expression.filter_leaf.values[0].string_value = "NaN"
        else:
            # recursive case
            for inner_expression in filter_expression.sub_expressions:
                inner_expression = FilterProcessor._convert_nan_features_to_string_in_filter_expression(
                    inner_expression
                )
        return filter_expression

    @classmethod
    def compile_filter_expression_from_segment_definition(
        cls, filter_expression: FilterExpression, segmentation_definitions: dict
    ) -> FilterExpression:
        operator = cls._get_filter_operator(filter_expression.operator)
        if operator == FilterExpressionOperator.UNKNOWN:
            if filter_expression.filter_leaf.value_type != FilterLeaf.FilterLeafValueType.SEGMENT:
                return filter_expression
            if len(filter_expression.filter_leaf.values) > 1:
                raise ValueError(
                    'Dont support filter with multiple segment values'
                )
            position = int(filter_expression.filter_leaf.values[0].number_value)
            segmentation_id = filter_expression.filter_leaf.segmentation_id
            ret = FilterExpression()
            ret.CopyFrom(
                segmentation_definitions[segmentation_id].segments[position].
                filter_expression
            )
            return ret
        else:
            return FilterExpression(
                operator=operator,
                sub_expressions=[
                    cls.compile_filter_expression_from_segment_definition(
                        sub_expression, segmentation_definitions
                    ) for sub_expression in filter_expression.sub_expressions
                ]
            )

    @classmethod
    def _get_filter_operator(cls, operator: int) -> FilterExpressionOperator:
        if FilterExpressionOperator.FEO_AND == operator:
            return FilterExpressionOperator.FEO_AND
        if FilterExpressionOperator.FEO_OR == operator:
            return FilterExpressionOperator.FEO_OR
        if FilterExpressionOperator.FEO_NOT == operator:
            return FilterExpressionOperator.FEO_NOT
        else:
            return FilterExpressionOperator.UNKNOWN
