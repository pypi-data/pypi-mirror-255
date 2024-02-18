import time
from typing import Dict
from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.internal_dai_version.client import CACHE_SYNC_SECONDS
from h2o_engine_manager.clients.internal_h2o_version.mapper import (
    build_internal_h2o_version_name,
)
from h2o_engine_manager.clients.internal_h2o_version.mapper import (
    from_api_internal_h2o_version_to_custom,
)
from h2o_engine_manager.clients.internal_h2o_version.mapper import from_api_objects
from h2o_engine_manager.clients.internal_h2o_version.mapper import (
    from_custom_internal_h2o_version_to_api_resource,
)
from h2o_engine_manager.clients.internal_h2o_version.page import InternalH2OVersionsPage
from h2o_engine_manager.clients.internal_h2o_version.version import InternalH2OVersion
from h2o_engine_manager.clients.internal_h2o_version.version_config import (
    InternalH2OVersionConfig,
)
from h2o_engine_manager.gen import ApiException as InternalH2OVersionApiException
from h2o_engine_manager.gen.api.internal_h2_o_version_service_api import (
    InternalH2OVersionServiceApi,
)
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_assign_internal_h2_o_version_aliases_request import (
    V1AssignInternalH2OVersionAliasesRequest,
)
from h2o_engine_manager.gen.model.v1_assign_internal_h2_o_version_aliases_response import (
    V1AssignInternalH2OVersionAliasesResponse,
)
from h2o_engine_manager.gen.model.v1_internal_h2_o_version import V1InternalH2OVersion
from h2o_engine_manager.gen.model.v1_list_internal_h2_o_versions_response import (
    V1ListInternalH2OVersionsResponse,
)


class InternalH2OVersionClient:
    """InternalH2OVersionClient manages InternalH2OVersions."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes InternalH2OVersionClient.

        Args:
            connection_config (ConnectionConfig): AIEM connection configuration object.
            verify_ssl: Set to False to disable SSL certificate verification.
            ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
        """

        configuration_internal_h2o_version = Configuration(
            host=connection_config.aiem_url
        )
        configuration_internal_h2o_version.verify_ssl = verify_ssl
        configuration_internal_h2o_version.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
            configuration_internal_h2o_version, connection_config.token_provider
        ) as api_h2o_version_client:
            self.gen_api_client = InternalH2OVersionServiceApi(api_h2o_version_client)

    def create_version(
        self,
        internal_h2o_version_id: str,
        image: str,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: List[str] = [],
        gpu_resource_name: str = "",
        annotations: Dict[str, str] = {},
        deprecated: bool = False,
    ) -> InternalH2OVersion:
        """
        Create InternalH2OVersion.

        Args:
            internal_h2o_version_id: version identifier. Must be in semver format.
                More than three segments are supported. For example "3.42.0.3".
            image: Name of the Docker image when using this version.
            image_pull_policy: Image pull policy applied when using this version.
            image_pull_secrets: List of references to k8s secrets that can be used for pulling
                an image of this version from a private container image registry or repository.
            gpu_resource_name: K8s GPU resource name. For example: "nvidia.com/gpu" or "amd.com/gpu".
            annotations: Additional arbitrary metadata associated with this version.
            deprecated: Indicates whether this version is deprecated.

        Returns:
            Created InternalH2OVersion.
        """

        api_version = V1InternalH2OVersion(
            image=image,
            image_pull_policy=image_pull_policy.to_ih2ov_api_image_pull_policy(),
            image_pull_secrets=image_pull_secrets,
            gpu_resource_name=gpu_resource_name,
            annotations=annotations,
            deprecated=deprecated,
        )

        created_api_version: V1InternalH2OVersion

        try:
            created_api_version = self.gen_api_client.internal_h2_o_version_service_create_internal_h2_o_version(
                internal_h2o_version_id=internal_h2o_version_id,
                internal_h2o_version=api_version,
            ).internal_h2o_version
        except InternalH2OVersionApiException as e:
            raise CustomApiException(e)

        return from_api_internal_h2o_version_to_custom(api_internal_h2o_version=created_api_version)

    def get_version(self, internal_h2o_version_id: str) -> InternalH2OVersion:
        """
        Get InternalH2OVersion.

        Args:
            internal_h2o_version_id: resource ID of InternalH2OVersion

        Returns:
            InternalH2OVersion
        """
        api_version: V1InternalH2OVersion

        try:
            api_version = self.gen_api_client.internal_h2_o_version_service_get_internal_h2_o_version(
                name_11=build_internal_h2o_version_name(internal_h2o_version_id=internal_h2o_version_id),
            ).internal_h2o_version
        except InternalH2OVersionApiException as e:
            raise CustomApiException(e)

        return from_api_internal_h2o_version_to_custom(api_internal_h2o_version=api_version)

    def list_versions(
        self,
        page_size: int = 0,
        page_token: str = "",
    ) -> InternalH2OVersionsPage:
        """
        List InternalH2OVersions.

        Args:
            page_size: Maximum number of InternalH2OVersions to return in a response.
                If unspecified (or set to 0), at most 50 InternalH2OVersions will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token: Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the InternalH2OVersionsPage.

        Returns:
            Page of InternalH2OVersions
        """
        list_response: V1ListInternalH2OVersionsResponse

        try:
            list_response = (
                self.gen_api_client.internal_h2_o_version_service_list_internal_h2_o_versions(
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except InternalH2OVersionApiException as e:
            raise CustomApiException(e)

        return InternalH2OVersionsPage(list_response)

    def list_all_versions(self) -> List[InternalH2OVersion]:
        """
        List all InternalH2OVersions.

        Returns:
            InternalH2OVersions
        """
        all_versions: List[InternalH2OVersion] = []
        next_page_token = ""
        while True:
            versions_list = self.list_versions(
                page_size=0,
                page_token=next_page_token,
            )
            all_versions = all_versions + versions_list.internal_h2o_versions
            next_page_token = versions_list.next_page_token
            if next_page_token == "":
                break

        return all_versions

    def update_version(
        self,
        internal_h2o_version: InternalH2OVersion,
        update_mask: str = "*"
    ) -> InternalH2OVersion:
        """
        Update InternalH2OVersion.

        Args:
            internal_h2o_version: InternalH2OVersion with to-be-updated values.
            update_mask: Comma separated paths referencing which fields to update.
                Update mask must be non-empty.
                Allowed field paths are: {"aliases", "deprecated", "image", "image_pull_policy", "image_pull_secrets",
                "gpu_resource_name", "data_directory_storage_class", "annotations"}.

        Returns:
            Updated InternalH2OVersion
        """
        updated_api_version: V1InternalH2OVersion

        try:
            updated_api_version = self.gen_api_client.internal_h2_o_version_service_update_internal_h2_o_version(
                internal_h2o_version_name=internal_h2o_version.name,
                update_mask=update_mask,
                internal_h2o_version=from_custom_internal_h2o_version_to_api_resource(internal_h2o_version),
            ).internal_h2o_version
        except InternalH2OVersionApiException as e:
            raise CustomApiException(e)

        return from_api_internal_h2o_version_to_custom(api_internal_h2o_version=updated_api_version)

    def delete_version(self, internal_h2o_version_id: str) -> None:
        """
        Delete InternalH2OVersion.

        Args:
            internal_h2o_version_id: ID of to-be-deleted InternalH2OVersion
        """
        try:
            self.gen_api_client.internal_h2_o_version_service_delete_internal_h2_o_version(
                name_4=build_internal_h2o_version_name(internal_h2o_version_id=internal_h2o_version_id)
            )
        except InternalH2OVersionApiException as e:
            raise CustomApiException(e)

    def delete_all_internal_h2o_versions(self) -> None:
        """Help function for deleting all InternalH2OVersions."""
        versions = self.list_all_versions()
        for version in versions:
            self.delete_version(internal_h2o_version_id=version.internal_h2o_version_id)

    def assign_aliases(self, internal_h2o_version_id: str, aliases: List[str]) -> List[InternalH2OVersion]:
        """
        Assign new set of aliases to InternalH2OVersion.
        For more detailed info see InternalDAIVersion assign_aliases description, it uses the same logic.

        Args:
            internal_h2o_version_id: ID of the InternalH2OVersion
            aliases: new aliases to assign to the InternalH2OVersion

        Returns:
            all InternalH2OVersions after applying the new aliases
        """
        name = build_internal_h2o_version_name(internal_h2o_version_id=internal_h2o_version_id)
        response: V1AssignInternalH2OVersionAliasesResponse

        try:
            response = self.gen_api_client.internal_h2_o_version_service_assign_internal_h2_o_version_aliases(
                body=V1AssignInternalH2OVersionAliasesRequest(internal_h2o_version=name, aliases=aliases)
            )
        except InternalH2OVersionApiException as e:
            raise CustomApiException(e)

        return from_api_objects(api_versions=response.internal_h2o_versions)

    def apply_internal_h2o_versions(self, version_configs: List[InternalH2OVersionConfig]) -> List[InternalH2OVersion]:
        """
        Same behaviour as apply_internal_dai_versions. See that for more info.

        Args:
            version_configs: configuration of InternalH2OVersions that should be applied

        Returns: applied InternalH2OVersions.
        """
        time.sleep(CACHE_SYNC_SECONDS)
        self.delete_all_internal_h2o_versions()

        for cfg in version_configs:
            self.create_version(
                internal_h2o_version_id=cfg.internal_h2o_version_id,
                image=cfg.image,
                image_pull_policy=cfg.image_pull_policy,
                image_pull_secrets=cfg.image_pull_secrets,
                gpu_resource_name=cfg.gpu_resource_name,
                annotations=cfg.annotations,
                deprecated=cfg.deprecated,
            )

        for cfg in version_configs:
            if len(cfg.aliases) > 0:
                self.assign_aliases(internal_h2o_version_id=cfg.internal_h2o_version_id, aliases=cfg.aliases)

        time.sleep(CACHE_SYNC_SECONDS)
        return self.list_all_versions()
