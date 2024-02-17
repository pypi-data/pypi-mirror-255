# pylint: disable=no-name-in-module,no-member
from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb
from truera.protobuf.public.util import split_mode_pb2

# pylint: enable=no-name-in-module

DEFAULT_SAMPLE_STRATEGY = ds_messages_pb.SAMPLE_RANDOM
DEFAULT_APPROX_MAX_ROWS = 50_000
DEFAULT_SPLIT_TYPE = "all"
DEFAULT_MAX_TOKEN_LENGTH = 1000
DEFAULT_MAX_EMBEDDINGS_LENGTH = 2000
DEFAULT_SPLIT_MODE = split_mode_pb2.SplitMode.SPLIT_MODE_DATA_REQUIRED
DEFAULT_TIMEOUT_SECONDS = 900

NLP_INFLUENCE_COL_NAME = "__truera_influences__"

FEATURE_INFLUENCE_SUFFIX_TRUERA_QII = "_truera-qii_influence"
FEATURE_INFLUENCE_SUFFIX_SHAP = "_shap_influence"

PROD_DATA_SPLIT_TYPE = "prod"
PROD_DATA_SPLIT_NAME = "prod"
SPECIAL_COLUMN_NAMES = {
    "__truera_id__",
}
