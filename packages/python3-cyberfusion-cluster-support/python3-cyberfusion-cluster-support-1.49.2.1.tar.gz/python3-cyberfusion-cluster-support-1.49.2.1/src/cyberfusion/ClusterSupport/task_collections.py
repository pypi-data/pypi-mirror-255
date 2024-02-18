"""Helper classes for scripts for cluster support packages."""

from enum import Enum
from typing import List, Optional

from cyberfusion.ClusterSupport._interfaces import (
    APIObjectInterface,
    sort_lists,
)
from cyberfusion.ClusterSupport.enums import ObjectModelName

ENDPOINT_TASK_COLLECTIONS = "task-collections"


class TaskCollectionType(str, Enum):
    """Task collection types."""

    ASYNCHRONOUS: str = "asynchronous"


class TaskCollection(APIObjectInterface):
    """Represents object."""

    _TABLE_HEADERS = [
        "ID",
        "Description",
        "Collection Type",
        "Object ID",
        "Object Type",
        "Cluster ID",
    ]
    _TABLE_HEADERS_DETAILED: List[str] = []

    _TABLE_FIELDS = [
        "id",
        "description",
        "collection_type",
        "object_id",
        "object_model_name",
        "cluster_id",
    ]
    _TABLE_FIELDS_DETAILED: List[str] = []

    @sort_lists  # type: ignore[misc]
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.id = obj["id"]
        self.uuid = obj["uuid"]
        self.description = obj["description"]
        self.collection_type = TaskCollectionType(obj["collection_type"]).value
        self.object_id = obj["object_id"]
        self.object_model_name = ObjectModelName(
            obj["object_model_name"]
        ).value
        self.cluster_id: Optional[int] = obj["cluster_id"]
        self.created_at = obj["created_at"]
        self.updated_at = obj["updated_at"]

    def retry(self) -> None:
        """Retry task collection."""
        url = f"/api/v1/{ENDPOINT_TASK_COLLECTIONS}/{self.uuid}/retry"
        data: dict = {}

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)
