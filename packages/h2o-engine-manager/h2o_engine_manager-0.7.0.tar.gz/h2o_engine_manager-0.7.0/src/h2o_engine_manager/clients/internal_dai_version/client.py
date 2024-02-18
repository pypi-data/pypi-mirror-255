import time
from typing import Dict
from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.internal_dai_version.mapper import (
    build_internal_dai_version_name,
)
from h2o_engine_manager.clients.internal_dai_version.mapper import (
    from_api_internal_dai_version_to_custom,
)
from h2o_engine_manager.clients.internal_dai_version.mapper import from_api_objects
from h2o_engine_manager.clients.internal_dai_version.mapper import (
    from_custom_internal_dai_version_to_api_resource,
)
from h2o_engine_manager.clients.internal_dai_version.page import InternalDAIVersionsPage
from h2o_engine_manager.clients.internal_dai_version.version import InternalDAIVersion
from h2o_engine_manager.clients.internal_dai_version.version_config import (
    InternalDAIVersionConfig,
)
from h2o_engine_manager.gen import ApiException as InternalDAIVersionApiException
from h2o_engine_manager.gen.api.internal_dai_version_service_api import (
    InternalDAIVersionServiceApi,
)
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_assign_internal_dai_version_aliases_request import (
    V1AssignInternalDAIVersionAliasesRequest,
)
from h2o_engine_manager.gen.model.v1_assign_internal_dai_version_aliases_response import (
    V1AssignInternalDAIVersionAliasesResponse,
)
from h2o_engine_manager.gen.model.v1_internal_dai_version import V1InternalDAIVersion
from h2o_engine_manager.gen.model.v1_list_internal_dai_versions_response import (
    V1ListInternalDAIVersionsResponse,
)

# Kubernetes cache needs to take some time to detect changes in k8s server.
CACHE_SYNC_SECONDS = 0.2


class InternalDAIVersionClient:
    """InternalDAIVersionClient manages InternalDAIVersions."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes InternalDAIVersionClient.

        Args:
            connection_config (ConnectionConfig): AIEM connection configuration object.
            verify_ssl: Set to False to disable SSL certificate verification.
            ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
        """

        configuration_internal_dai_version = Configuration(
            host=connection_config.aiem_url
        )
        configuration_internal_dai_version.verify_ssl = verify_ssl
        configuration_internal_dai_version.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
            configuration_internal_dai_version, connection_config.token_provider
        ) as api_dai_version_client:
            self.gen_api_client = InternalDAIVersionServiceApi(api_dai_version_client)

    def create_version(
        self,
        internal_dai_version_id: str,
        image: str,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: List[str] = [],
        gpu_resource_name: str = "",
        data_directory_storage_class: str = "",
        annotations: Dict[str, str] = {},
        deprecated: bool = False,
    ) -> InternalDAIVersion:
        """
        Create InternalDAIVersion.

        Args:
            internal_dai_version_id: version identifier. Must be in semver format.
                More than three segments are supported. For example "1.10.3" or "1.10.3.1".
            image: Name of the Docker image when using this version.
            image_pull_policy: Image pull policy applied when using this version.
            image_pull_secrets: List of references to k8s secrets that can be used for pulling
                an image of this version from a private container image registry or repository.
            aliases: Aliases of this version. For example ["latest"].
            gpu_resource_name: K8s GPU resource name. For example: "nvidia.com/gpu" or "amd.com/gpu".
            data_directory_storage_class: Name of the storage class used by Driverless AI when using this version.
            annotations: Additional arbitrary metadata associated with this version.
            deprecated: Indicates whether this version is deprecated.

        Returns:
            Created InternalDAIVersion.
        """

        api_version = V1InternalDAIVersion(
            image=image,
            image_pull_policy=image_pull_policy.to_idaiv_api_image_pull_policy(),
            image_pull_secrets=image_pull_secrets,
            gpu_resource_name=gpu_resource_name,
            data_directory_storage_class=data_directory_storage_class,
            annotations=annotations,
            deprecated=deprecated,
        )
        created_api_version: V1InternalDAIVersion

        try:
            created_api_version = self.gen_api_client.internal_dai_version_service_create_internal_dai_version(
                internal_dai_version_id=internal_dai_version_id,
                internal_dai_version=api_version,
            ).internal_dai_version
        except InternalDAIVersionApiException as e:
            raise CustomApiException(e)

        return from_api_internal_dai_version_to_custom(api_internal_dai_version=created_api_version)

    def get_version(self, internal_dai_version_id: str) -> InternalDAIVersion:
        """
        Get InternalDAIVersion.

        Args:
            internal_dai_version_id: resource ID of InternalDAIVersion

        Returns:
            InternalDAIVersion
        """
        api_version: V1InternalDAIVersion

        try:
            api_version = self.gen_api_client.internal_dai_version_service_get_internal_dai_version(
                name_10=build_internal_dai_version_name(internal_dai_version_id=internal_dai_version_id),
            ).internal_dai_version
        except InternalDAIVersionApiException as e:
            raise CustomApiException(e)

        return from_api_internal_dai_version_to_custom(api_internal_dai_version=api_version)

    def list_versions(
        self,
        page_size: int = 0,
        page_token: str = "",
    ) -> InternalDAIVersionsPage:
        """
        List InternalDAIVersions.

        Args:
            page_size: Maximum number of InternalDAIVersions to return in a response.
                If unspecified (or set to 0), at most 50 InternalDAIVersions will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token: Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the InternalDAIVersionsPage.

        Returns:
            Page of InternalDAIVersions
        """
        list_response: V1ListInternalDAIVersionsResponse

        try:
            list_response = (
                self.gen_api_client.internal_dai_version_service_list_internal_dai_versions(
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except InternalDAIVersionApiException as e:
            raise CustomApiException(e)

        return InternalDAIVersionsPage(list_response)

    def list_all_versions(self) -> List[InternalDAIVersion]:
        """
        List all InternalDAIVersions.

        Returns:
            InternalDAIVersions
        """
        all_versions: List[InternalDAIVersion] = []
        next_page_token = ""
        while True:
            versions_list = self.list_versions(
                page_size=0,
                page_token=next_page_token,
            )
            all_versions = all_versions + versions_list.internal_dai_versions
            next_page_token = versions_list.next_page_token
            if next_page_token == "":
                break

        return all_versions

    def update_version(
        self,
        internal_dai_version: InternalDAIVersion,
        update_mask: str = "*"
    ) -> InternalDAIVersion:
        """
        Update InternalDAIVersion.

        Args:
            internal_dai_version: InternalDAIVersion with to-be-updated values.
            update_mask: Comma separated paths referencing which fields to update.
                Update mask must be non-empty.
                Allowed field paths are: {"aliases", "deprecated", "image", "image_pull_policy", "image_pull_secrets",
                "gpu_resource_name", "data_directory_storage_class", "annotations"}.

        Returns:
            Updated InternalDAIVersion
        """
        updated_api_version: V1InternalDAIVersion

        try:
            updated_api_version = self.gen_api_client.internal_dai_version_service_update_internal_dai_version(
                internal_dai_version_name=internal_dai_version.name,
                update_mask=update_mask,
                internal_dai_version=from_custom_internal_dai_version_to_api_resource(internal_dai_version),
            ).internal_dai_version
        except InternalDAIVersionApiException as e:
            raise CustomApiException(e)

        return from_api_internal_dai_version_to_custom(api_internal_dai_version=updated_api_version)

    def delete_version(self, internal_dai_version_id: str) -> None:
        """
        Delete InternalDAIVersion.

        Args:
            internal_dai_version_id: ID of to-be-deleted InternalDAIVersion
        """
        try:
            self.gen_api_client.internal_dai_version_service_delete_internal_dai_version(
                name_3=build_internal_dai_version_name(internal_dai_version_id=internal_dai_version_id)
            )
        except InternalDAIVersionApiException as e:
            raise CustomApiException(e)

    def delete_all_internal_dai_versions(self) -> None:
        """Help function for deleting all InternalDAIVersions."""
        versions = self.list_all_versions()
        for version in versions:
            self.delete_version(internal_dai_version_id=version.internal_dai_version_id)

    def assign_aliases(self, internal_dai_version_id: str, aliases: List[str]) -> List[InternalDAIVersion]:
        """

        Assign new set of aliases to InternalDAIVersion.
        This will replace existing InternalDAIVersion aliases with the new aliases.
        If there are other InternalDAIVersions with the same alias that we try to assign,
        they will be deleted from the other InternalDAIVersions.

        Example 1 - assign **only** alias latest to another InternalDAIVersion:

        - InternalDAIVersions: daiv1.aliases=["latest", "foo"], daiv2.aliases=["bar", "baz"], daiv3.aliases=["goo"]
        - AssignAliases(daiv3, aliases=["latest"])
        - InternalDAIVersions: daiv1.aliases=["foo"], daiv2.aliases=["bar", "baz"], daiv3.aliases=["latest"]
        Note that alias "latest" was deleted from daiv1 and alias "goo" was deleted from daiv3.

        Example 2 - add alias latest to another InternalDAIVersion:

        - InternalDAIVersions: daiv1.aliases=["latest", "foo"], daiv2.aliases=["bar", "baz"], daiv3.aliases=["goo"]
        - AssignAliases(daiv3, aliases=["goo", "latest"])
        - InternalDAIVersions: daiv1.aliases=["foo"], daiv2.aliases=["bar", "baz"], daiv3.aliases=["goo", "latest"]
        Note that alias "latest" was deleted from daiv1 and alias "goo" remained in the daiv3.

        Example 3 - assign multiple aliases which affects aliases of multiple InternalDAIVersions:

        - InternalDAIVersions: daiv1.aliases=["latest", "foo"], daiv2.aliases=["bar", "baz"], daiv3.aliases=["goo"]
        - AssignAliases(daiv3, aliases=["latest", "bar"])
        - InternalDAIVersions: daiv1.aliases=["foo"], daiv2.aliases=["baz"], daiv3.aliases=["latest", "bar"]
        Note that
        - alias "latest" was deleted from daiv1
        - alias "latest" was added to daiv3
        - alias "bar" was deleted from daiv2
        - alias "goo" was deleted from daiv3

        Args:
            internal_dai_version_id: ID of the InternalDAIVersion
            aliases: aliases to assign to the InternalDAIVersion

        Returns:
            all InternalDAIVersions after applying the new aliases
        """
        name = build_internal_dai_version_name(internal_dai_version_id=internal_dai_version_id)
        response: V1AssignInternalDAIVersionAliasesResponse

        try:
            response = self.gen_api_client.internal_dai_version_service_assign_internal_dai_version_aliases(
                body=V1AssignInternalDAIVersionAliasesRequest(internal_dai_version=name, aliases=aliases)
            )
        except InternalDAIVersionApiException as e:
            raise CustomApiException(e)

        return from_api_objects(api_versions=response.internal_dai_versions)

    def apply_internal_dai_versions(self, version_configs: List[InternalDAIVersionConfig]) -> List[InternalDAIVersion]:
        """
        Set all InternalDAIVersions to a state defined in the version_configs.
        InternalDAIVersions not specified in the version_configs will be deleted.
        InternalDAIVersions specified in the version_configs will be recreated with the new values.
        When multiple InternalDAIVersions are configured with the same alias,
        the latest one in the version_configs list will have this alias assigned (rest will have it removed).

        Args:
            version_configs: configuration of InternalDAIVersions that should be applied

        Returns: applied InternalDAIVersions

        """
        time.sleep(CACHE_SYNC_SECONDS)
        self.delete_all_internal_dai_versions()

        for cfg in version_configs:
            self.create_version(
                internal_dai_version_id=cfg.internal_dai_version_id,
                image=cfg.image,
                image_pull_policy=cfg.image_pull_policy,
                image_pull_secrets=cfg.image_pull_secrets,
                gpu_resource_name=cfg.gpu_resource_name,
                data_directory_storage_class=cfg.data_directory_storage_class,
                annotations=cfg.annotations,
                deprecated=cfg.deprecated,
            )

        for cfg in version_configs:
            if len(cfg.aliases) > 0:
                self.assign_aliases(internal_dai_version_id=cfg.internal_dai_version_id, aliases=cfg.aliases)

        time.sleep(CACHE_SYNC_SECONDS)
        return self.list_all_versions()
