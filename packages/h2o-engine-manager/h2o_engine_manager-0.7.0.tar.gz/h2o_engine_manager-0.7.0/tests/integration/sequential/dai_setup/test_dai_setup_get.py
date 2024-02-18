import os

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.dai_setup.setup import DAISetup
from tests.integration.sequential.dai_setup.test_dai_setup_update import (
    assert_default_dai_setup_values,
)
from tests.integration.sequential.dai_setup.test_dai_setup_update import (
    dai_setup_equals,
)


def test_get_new_workspace(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    stp = dai_setup_client_super_admin.get_dai_setup("whatever")

    assert stp.name == "workspaces/whatever/daiSetup"
    assert_default_dai_setup_values(dai_setup_client=dai_setup_client_super_admin, stp=stp)


def test_get_existing_workspace(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    create_dai_setup_workspace_dai_setup,
    delete_all_dai_setups_after
):
    stp = dai_setup_client_super_admin.get_dai_setup("dai-setup")
    want_setup = DAISetup(
        name="workspaces/dai-setup/daiSetup",
        cpu_constraint=NumericConstraint(minimum="1", default="1"),
        gpu_constraint=NumericConstraint(minimum="0", default="0"),
        memory_bytes_constraint=NumericConstraint(minimum="1", default="1"),
        storage_bytes_constraint=NumericConstraint(minimum="1", default="1"),
        max_idle_duration_constraint=DurationConstraint(minimum="0s", default="2h"),
        max_running_duration_constraint=DurationConstraint(minimum="0s", default="2h"),
        max_non_interaction_duration=None,
        max_unused_duration=None,
        configuration_override={
            "disk_limit_gb": "10",
            "my_new_config": "my-new-value",
        },
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
        triton_enabled=False,
    )
    assert dai_setup_equals(want_setup, stp)
