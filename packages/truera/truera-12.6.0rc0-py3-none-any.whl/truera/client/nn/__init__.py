from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Type, TypeVar
import warnings

from truera.client.nn.nn_utils import BaselineType
from truera.client.nn.nn_utils import Batch
from truera.client.nn.nn_utils import CUDA

logger = logging.getLogger(__name__)

# NN product version
__version__ = "0.0.1"
