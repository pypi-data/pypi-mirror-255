import http

import pytest

from h2o_engine_manager.clients.dai_setup.client import DAISetupClient
from h2o_engine_manager.clients.exception import CustomApiException


def test_get_unauthorized(
    dai_setup_client_standard_user: DAISetupClient,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    with pytest.raises(CustomApiException) as exc:
        dai_setup_client_standard_user.get_dai_setup("whatever")
    assert exc.value.status == http.HTTPStatus.FORBIDDEN


def test_update_unauthorized(
    dai_setup_client_standard_user: DAISetupClient,
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="dai-setup-unauthorized")
    with pytest.raises(CustomApiException) as exc:
        dai_setup_client_standard_user.update_dai_setup(dai_setup=stp)
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
