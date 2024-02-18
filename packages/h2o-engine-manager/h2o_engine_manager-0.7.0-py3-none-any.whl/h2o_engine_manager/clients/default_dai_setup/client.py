from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.default_dai_setup.setup import DefaultDAISetup
from h2o_engine_manager.clients.default_dai_setup.setup import from_api_object
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.gen import ApiException as DefaultDAISetupApiException
from h2o_engine_manager.gen.api.default_dai_setup_service_api import (
    DefaultDAISetupServiceApi,
)
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_default_dai_setup import V1DefaultDAISetup


class DefaultDAISetupClient:
    """DefaultDAISetupClient manages DefaultDAISetup."""

    def __init__(
            self,
            connection_config: ConnectionConfig,
            verify_ssl: bool = True,
            ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes DAISetupClient.

        Args:
            connection_config (ConnectionConfig): AIEM connection configuration object.
            verify_ssl: Set to False to disable SSL certificate verification.
            ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
        """

        cfg = Configuration(
            host=connection_config.aiem_url
        )
        cfg.verify_ssl = verify_ssl
        cfg.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
                cfg, connection_config.token_provider
        ) as api_client:
            self.gen_api_client = DefaultDAISetupServiceApi(api_client)

    def get_default_dai_setup(self) -> DefaultDAISetup:
        """Returns DefaultDAISetup.

        Returns:
            DefaultDAISetup: global DefaultDAISetup.
        """
        api_default_dai_setup: V1DefaultDAISetup
        try:
            api_default_dai_setup = (
                self.gen_api_client.default_dai_setup_service_get_default_dai_setup(
                    name_5=f"defaultDAISetup"
                ).default_dai_setup
            )
        except DefaultDAISetupApiException as e:
            raise CustomApiException(e)

        return from_api_object(
            api_object=api_default_dai_setup
        )

    def update_default_dai_setup(self, default_dai_setup: DefaultDAISetup, update_mask: str = "*") -> DefaultDAISetup:
        """Updates the DefaultDAISetup.

        Args:
            default_dai_setup (DAISetup): The DefaultDAISetup to be updated.
            update_mask (str, optional): Comma separated paths referencing which fields to update.
                Update mask must be non-empty.

                Allowed field paths are: {"cpu_constraint", "gpu_constraint", "memory_bytes_constraint", "storage_bytes_constraint",
                "max_idle_duration_constraint", "max_running_duration_constraint", "max_non_interaction_duration",
                "max_unused_duration", "configuration_override", "yaml_pod_template_spec", "yaml_gpu_tolerations"}.

                Paths are case sensitive (must match exactly).
                Example - update only cpu constraint: update_mask="cpu_constraint"
                Example - update only cpu and gpu constraints: update_mask="cpu_constraint,gpu_constraint"

                To update all allowed fields, specify exactly one path with value "*", this is a default value.

        Returns:
            DefaultDAISetup: The updated DefaultDAISetup.
        """
        updated_default_dai_setup: V1DefaultDAISetup
        try:
            updated_default_dai_setup = self.gen_api_client.default_dai_setup_service_update_default_dai_setup(
                default_dai_setup_name=default_dai_setup.name,
                update_mask=update_mask,
                default_dai_setup=default_dai_setup.to_api_object(),
            ).default_dai_setup
        except DefaultDAISetupApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_default_dai_setup)
