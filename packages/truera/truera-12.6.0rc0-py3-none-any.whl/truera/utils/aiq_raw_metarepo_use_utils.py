from typing import List

# pylint: disable=no-name-in-module
from truera.client.private.metarepo import DataSplit
from truera.protobuf.public.data.data_split_pb2 import \
    DataSplit as _PBDataSplit
from truera.protobuf.public.data.data_split_pb2 import DataSplitType
from truera.protobuf.public.metadata_message_types_pb2 import SplitStatus

# pylint: enable=no-name-in-module


def _filter_to_active_splits(splits_list: List[DataSplit]) -> List[DataSplit]:
    accept_statuses = [
        SplitStatus.SPLIT_STATUS_INVALID, SplitStatus.SPLIT_STATUS_ACTIVE
    ]
    return [s for s in splits_list if s.status in accept_statuses]


def check_if_split_not_prod_split(split: _PBDataSplit) -> bool:
    return split.split_type != DataSplitType.PROD_SPLIT


def filter_to_non_prod_splits(
    splits_list: List[_PBDataSplit]
) -> List[_PBDataSplit]:
    return [s for s in splits_list if check_if_split_not_prod_split(s)]
