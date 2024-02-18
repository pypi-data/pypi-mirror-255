import pprint

from h2o_engine_manager.clients.internal_dai_version.mapper import from_api_objects
from h2o_engine_manager.gen.model.v1_list_internal_dai_versions_response import (
    V1ListInternalDAIVersionsResponse,
)


class InternalDAIVersionsPage:
    """Class represents a list of InternalDAIVersions together with a next_page_token
    and a total_size for listing all InternalDAIVersions."""

    def __init__(self, list_api_response: V1ListInternalDAIVersionsResponse) -> None:
        self.internal_dai_versions = from_api_objects(api_versions=list_api_response.internal_dai_versions)
        self.next_page_token = list_api_response.next_page_token
        self.total_size = list_api_response.total_size

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
