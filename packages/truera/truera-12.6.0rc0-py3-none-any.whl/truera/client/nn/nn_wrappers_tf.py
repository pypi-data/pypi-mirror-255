"""Deprecated"""

from truera.client.nn.wrappers import tf
from truera.client.nn.wrappers.tf import import_tf
from truera.client.util.func import Deprecate

Deprecate.module(
    name=__name__,
    message="Use truera.client.nn.wrappers.tf instead.",
    dep_version="0.0.1",
    remove_version="0.1.0"
)
