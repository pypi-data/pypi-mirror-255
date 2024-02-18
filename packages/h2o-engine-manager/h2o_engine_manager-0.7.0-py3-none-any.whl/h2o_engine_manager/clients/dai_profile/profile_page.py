import pprint

from h2o_engine_manager.clients.dai_profile.profile import from_api_objects
from h2o_engine_manager.gen.model.v1_list_dai_profiles_response import (
    V1ListDAIProfilesResponse,
)


class DAIProfilesPage:
    """Class represents a list of DAIProfile objects together with a
    next_page_token and a total_size used for listing DAI profiles."""

    def __init__(
        self, list_api_response: V1ListDAIProfilesResponse
    ) -> None:
        self.profiles = from_api_objects(api_profiles=list_api_response.dai_profiles)
        self.next_page_token = list_api_response.next_page_token
        self.total_size = list_api_response.total_size

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
