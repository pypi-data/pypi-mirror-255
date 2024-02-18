import os
import time

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.dai_setup.setup import DAISetup
from tests.integration.conftest import CACHE_SYNC_SECONDS
from tests.integration.sequential.dai_setup.test_dai_setup_update import (
    dai_setup_equals,
)


def test_get_default_dai_setup(dai_setup_client_super_admin):
    dai_setup = dai_setup_client_super_admin.get_dai_setup(workspace_id="whatever")

    want_setup = DAISetup(
        name="workspaces/whatever/daiSetup",
        cpu_constraint=NumericConstraint(minimum="1", default="2", maximum="30"),
        gpu_constraint=NumericConstraint(minimum="0", default="0", maximum="1"),
        memory_bytes_constraint=NumericConstraint(minimum="4Gi", default="8Gi", maximum="250Gi"),
        storage_bytes_constraint=NumericConstraint(minimum="4Gi", default="8Gi"),
        max_idle_duration_constraint=DurationConstraint(minimum="0s", default="1h"),
        max_running_duration_constraint=DurationConstraint(minimum="0s", default="2d"),
        max_non_interaction_duration=None,
        max_unused_duration=None,
        configuration_override={},
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
        triton_enabled=False,
    )

    assert dai_setup_equals(want_setup, dai_setup)


def test_update_default_dai_setup(dai_setup_client_super_admin):
    dai_setup = dai_setup_client_super_admin.get_dai_setup(workspace_id="updated-dai-setup")
    dai_setup.memory_bytes_constraint = NumericConstraint(minimum="8Gi", default="16Gi", maximum="128Gi")
    dai_setup_client_super_admin.update_dai_setup(dai_setup=dai_setup)

    want_updated_setup = DAISetup(
        name="workspaces/updated-dai-setup/daiSetup",
        cpu_constraint=NumericConstraint(minimum="1", default="2", maximum="30"),
        gpu_constraint=NumericConstraint(minimum="0", default="0", maximum="1"),
        memory_bytes_constraint=NumericConstraint(minimum="8Gi", default="16Gi", maximum="128Gi"),
        storage_bytes_constraint=NumericConstraint(minimum="4Gi", default="8Gi"),
        max_idle_duration_constraint=DurationConstraint(minimum="0s", default="1h"),
        max_running_duration_constraint=DurationConstraint(minimum="0s", default="2d"),
        max_non_interaction_duration=None,
        max_unused_duration=None,
        configuration_override={},
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
        triton_enabled=False,
    )

    assert dai_setup_equals(want_updated_setup, dai_setup)

    # Double check that update was successful
    time.sleep(CACHE_SYNC_SECONDS)

    got_dai_setup = dai_setup_client_super_admin.get_dai_setup(workspace_id="updated-dai-setup")
    assert dai_setup_equals(want_updated_setup, got_dai_setup)
