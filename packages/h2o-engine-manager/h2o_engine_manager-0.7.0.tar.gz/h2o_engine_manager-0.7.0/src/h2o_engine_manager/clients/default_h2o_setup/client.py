from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.default_h2o_setup.setup import DefaultH2OSetup
from h2o_engine_manager.clients.default_h2o_setup.setup import from_api_object
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.gen import ApiException as DefaultH2OSetupApiException
from h2o_engine_manager.gen.api.default_h2_o_setup_service_api import (
    DefaultH2OSetupServiceApi,
)
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_default_h2_o_setup import V1DefaultH2OSetup


class DefaultH2OSetupClient:
    """DefaultH2OSetupClient manages DefaultH2OSetup."""

    def __init__(
            self,
            connection_config: ConnectionConfig,
            verify_ssl: bool = True,
            ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes H2OSetupClient.

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
            self.gen_api_client = DefaultH2OSetupServiceApi(api_client)

    def get_default_h2o_setup(self) -> DefaultH2OSetup:
        """Returns DefaultH2OSetup.

        Returns:
            DefaultH2OSetup: global DefaultH2OSetup.
        """
        api_default_h2o_setup: V1DefaultH2OSetup
        try:
            api_default_h2o_setup = (
                self.gen_api_client.default_h2_o_setup_service_get_default_h2_o_setup(
                    name_6=f"defaultH2OSetup"
                ).default_h2o_setup
            )
        except DefaultH2OSetupApiException as e:
            raise CustomApiException(e)

        return from_api_object(
            api_object=api_default_h2o_setup
        )

    def update_default_h2o_setup(self, default_h2o_setup: DefaultH2OSetup, update_mask: str = "*") -> DefaultH2OSetup:
        """Updates the DefaultH2OSetup.

        Args:
            default_h2o_setup (H2OSetup): The DefaultH2OSetup to be updated.
            update_mask (str, optional): Comma separated paths referencing which fields to update.
                Update mask must be non-empty.

                Allowed field paths are: {"node_count_constraint", "cpu_constraint", "gpu_constraint", "memory_bytes_constraint",
                "max_idle_duration_constraint", "max_running_duration_constraint", "yaml_pod_template_spec", "yaml_gpu_tolerations"}.

                Paths are case sensitive (must match exactly).
                Example - update only cpu constraint: update_mask="cpu_constraint"
                Example - update only cpu and gpu constraints: update_mask="cpu_constraint,gpu_constraint"

                To update all allowed fields, specify exactly one path with value "*", this is a default value.

        Returns:
            DefaultH2OSetup: The updated DefaultH2OSetup.
        """
        updated_default_h2o_setup: V1DefaultH2OSetup
        try:
            updated_default_h2o_setup = self.gen_api_client.default_h2_o_setup_service_update_default_h2_o_setup(
                default_h2o_setup_name=default_h2o_setup.name,
                update_mask=update_mask,
                default_h2o_setup=default_h2o_setup.to_api_object(),
            ).default_h2o_setup
        except DefaultH2OSetupApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_default_h2o_setup)
