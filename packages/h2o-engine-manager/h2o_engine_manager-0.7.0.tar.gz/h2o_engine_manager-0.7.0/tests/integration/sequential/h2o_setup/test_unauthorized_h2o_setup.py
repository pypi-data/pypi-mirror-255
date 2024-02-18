import http

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.h2o_setup.client import H2OSetupClient


def test_get_unauthorized(
    h2o_setup_client_standard_user: H2OSetupClient,
    create_default_h2o_setup,
    delete_all_h2o_setups_after,
):
    with pytest.raises(CustomApiException) as exc:
        h2o_setup_client_standard_user.get_h2o_setup("whatever")
    assert exc.value.status == http.HTTPStatus.FORBIDDEN


def test_update_unauthorized(
    h2o_setup_client_standard_user: H2OSetupClient,
    h2o_setup_client_super_admin,
    create_default_h2o_setup,
    delete_all_h2o_setups_after,
):
    stp = h2o_setup_client_super_admin.get_h2o_setup(workspace_id="h2o-setup-unauthorized")
    with pytest.raises(CustomApiException) as exc:
        h2o_setup_client_standard_user.update_h2o_setup(h2o_setup=stp)
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
