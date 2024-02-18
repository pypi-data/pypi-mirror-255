from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.default_h2o_setup.client import DefaultH2OSetupClient
from h2o_engine_manager.clients.default_h2o_setup.setup import DefaultH2OSetup
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.h2o_setup.setup import H2OSetup
from h2o_engine_manager.clients.h2o_setup.setup import from_api_object
from h2o_engine_manager.gen import ApiException as H2OSetupApiException
from h2o_engine_manager.gen.api.h2_o_setup_service_api import H2OSetupServiceApi
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_h2_o_setup import V1H2OSetup


class H2OSetupClient:
    """H2OSetupClient manages H2OSetups."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        default_h2o_setup_client: DefaultH2OSetupClient,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes H2OSetupClient.

        Args:
            connection_config (ConnectionConfig): AIEM connection configuration object.
            default_h2o_setup_client: DefaultH2OSetupClient.
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
            self.gen_api_client = H2OSetupServiceApi(api_client)

        self.default_h2o_setup_client = default_h2o_setup_client

    def get_h2o_setup(self, workspace_id: str) -> H2OSetup:
        """Returns a H2OSetup.

        Args:
            workspace_id (str): The ID of a workspace.

        Returns:
            H2OSetup: H2OSetup associated with a given workspace.
        """
        api_h2o_setup: V1H2OSetup
        try:
            api_h2o_setup = (
                self.gen_api_client.h2_o_setup_service_get_h2_o_setup(
                    name_9=f"workspaces/{workspace_id}/h2oSetup"
                ).h2o_setup
            )
        except H2OSetupApiException as e:
            raise CustomApiException(e)

        return from_api_object(
            api_object=api_h2o_setup
        )

    def update_h2o_setup(self, h2o_setup: H2OSetup, update_mask: str = "*") -> H2OSetup:
        """Updates the H2OSetup.

        Args:
            h2o_setup (H2OSetup): The H2OSetup to be updated.
            update_mask (str, optional): Comma separated paths referencing which fields to update.
                Update mask must be non-empty.

                Allowed field paths are: {"node_count_constraint", "cpu_constraint", "gpu_constraint", "memory_bytes_constraint",
                "max_idle_duration_constraint", "max_running_duration_constraint", "yaml_pod_template_spec", "yaml_gpu_tolerations"}.

                Paths are case sensitive (must match exactly).
                Example - update only cpu constraint: update_mask="cpu_constraint"
                Example - update only cpu and gpu constraints: update_mask="cpu_constraint,gpu_constraint"

                To update all allowed fields, specify exactly one path with value "*", this is a default value.

        Returns:
            H2OSetup: An updated H2OSetup.
        """
        updated_h2o_setup: V1H2OSetup
        try:
            updated_h2o_setup = self.gen_api_client.h2_o_setup_service_update_h2_o_setup(
                h2o_setup_name=h2o_setup.name,
                update_mask=update_mask,
                h2o_setup=h2o_setup.to_api_object(),
            ).h2o_setup
        except H2OSetupApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_h2o_setup)

    def get_default_h2o_setup(self) -> DefaultH2OSetup:
        """Returns DefaultH2OSetup.

        Returns:
            DefaultH2OSetup: global DefaultH2OSetup.
        """
        return self.default_h2o_setup_client.get_default_h2o_setup()

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
        return self.default_h2o_setup_client.update_default_h2o_setup(
            default_h2o_setup=default_h2o_setup,
            update_mask=update_mask,
        )
