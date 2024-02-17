from functools import lru_cache
from typing import TYPE_CHECKING

from truera.client.remote_truera_workspace import RemoteTrueraWorkspace
from truera.protobuf.public import metadata_message_types_pb2 as md_pb

if TYPE_CHECKING:
    from truera.client.truera_workspace import TrueraWorkspace


class MetadataCache:

    def __init__(self, remote: RemoteTrueraWorkspace):
        self.remote = remote

    @lru_cache(maxsize=1)
    def get_project_metadata(self, project_name: str) -> md_pb.ProjectMetadata:
        return self.remote.ar_client.get_project_metadata(
            project_id=project_name
        )

    @lru_cache(maxsize=5)
    def get_model_metadata(
        self, model_name: str, project_id: str
    ) -> md_pb.ModelMetadata:
        return self.remote.ar_client.get_model_metadata(
            project_id=project_id, model_name=model_name
        )

    @lru_cache(maxsize=1)
    def get_data_collection_metadata(
        self, data_collection_name: str, project_id: str
    ) -> md_pb.DataCollectionMetadata:
        return self.remote.ar_client.get_data_collection_metadata(
            project_id=project_id, data_collection_name=data_collection_name
        )

    def get_project_id(self, project_name: str) -> str:
        """Retrieve the project id based on project name."""
        return self.get_project_metadata(project_name).id

    def get_model_id(self, model_name: str, project_id: str) -> str:
        """Retrieve the model id based on model name."""
        return self.get_model_metadata(model_name, project_id).id

    def get_data_collection_id(
        self, data_collection_name: str, project_id: str
    ) -> str:
        """Retrieve the data collection id based on data collection name."""
        return self.get_data_collection_metadata(
            data_collection_name, project_id
        ).id

    def invalidate(self):
        self.get_project_metadata.cache_clear()
        self.get_model_metadata.cache_clear()
        self.get_data_collection_metadata.cache_clear()


def invalidates_cache(workspace_method):

    def f(self: 'TrueraWorkspace', *args, **kwargs):
        ret = workspace_method(self, *args, **kwargs)
        self.md_cache.invalidate()
        return ret

    return f
