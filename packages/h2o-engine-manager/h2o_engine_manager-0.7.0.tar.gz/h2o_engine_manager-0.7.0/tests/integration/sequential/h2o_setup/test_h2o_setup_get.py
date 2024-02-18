import os

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.h2o_setup.setup import H2OSetup
from tests.integration.sequential.h2o_setup.test_h2o_setup_update import (
    assert_default_h2o_setup_values,
)
from tests.integration.sequential.h2o_setup.test_h2o_setup_update import (
    h2o_setup_equals,
)


def test_get_new_workspace(
    h2o_setup_client_super_admin,
    create_default_h2o_setup,
    delete_all_h2o_setups_after,
):
    stp = h2o_setup_client_super_admin.get_h2o_setup("whatever")

    assert stp.name == "workspaces/whatever/h2oSetup"
    assert_default_h2o_setup_values(h2o_setup_client=h2o_setup_client_super_admin, stp=stp)


def test_get_existing_workspace(
    h2o_setup_client_super_admin,
    create_default_h2o_setup,
    create_h2o_setup_workspace_h2o_setup,
    delete_all_h2o_setups_after
):
    stp = h2o_setup_client_super_admin.get_h2o_setup("h2o-setup")
    want_setup = H2OSetup(
        name="workspaces/h2o-setup/h2oSetup",
        node_count_constraint=NumericConstraint(minimum="1", default="1"),
        cpu_constraint=NumericConstraint(minimum="1", default="1"),
        gpu_constraint=NumericConstraint(minimum="0", default="0"),
        memory_bytes_constraint=NumericConstraint(minimum="1", default="1"),
        max_idle_duration_constraint=DurationConstraint(minimum="0s", default="2h"),
        max_running_duration_constraint=DurationConstraint(minimum="0s", default="2h"),
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        yaml_pod_template_spec="",
    )
    assert h2o_setup_equals(want_setup, stp)
