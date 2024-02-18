import os
import time

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.default_dai_setup.setup import DefaultDAISetup
from tests.integration.conftest import CACHE_SYNC_SECONDS
from tests.integration.sequential.dai_setup.test_dai_setup_update import (
    dai_setup_equals,
)
from tests.integration.sequential.dai_setup.test_dai_setup_update import yaml_equal


def test_update_dai_setup(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    default_dai_setup = dai_setup_client_super_admin.get_default_dai_setup()

    # Update all fields (except name of course).
    default_dai_setup.cpu_constraint = NumericConstraint(minimum="2", default="3", maximum="4")
    default_dai_setup.gpu_constraint = NumericConstraint(minimum="3", default="4", maximum="5")
    default_dai_setup.memory_bytes_constraint = NumericConstraint(minimum="2Gi", default="4Gi", maximum="6Gi")
    default_dai_setup.storage_bytes_constraint = NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Gi")
    default_dai_setup.max_idle_duration_constraint = DurationConstraint(minimum="1m", default="2h", maximum="20h")
    default_dai_setup.max_running_duration_constraint = DurationConstraint(minimum="2m", default="2h", maximum="20h")
    default_dai_setup.max_non_interaction_duration = "2d"
    default_dai_setup.max_unused_duration = "1d"
    default_dai_setup.configuration_override = {
        "a": "b",
        "c": "my-new-d",
    }
    default_dai_setup.yaml_pod_template_spec = open(
        os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r"
    ).read()
    default_dai_setup.yaml_gpu_tolerations = open(
        os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r"
    ).read()
    default_dai_setup.triton_enabled = False

    updated_default_dai_setup = dai_setup_client_super_admin.update_default_dai_setup(
        default_dai_setup=default_dai_setup
    )

    want_updated_default_dai_setup = DefaultDAISetup(
        name="defaultDAISetup",
        cpu_constraint=NumericConstraint(minimum="2", default="3", maximum="4"),
        gpu_constraint=NumericConstraint(minimum="3", default="4", maximum="5"),
        memory_bytes_constraint=NumericConstraint(minimum="2Gi", default="4Gi", maximum="6Gi"),
        storage_bytes_constraint=NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Gi"),
        max_idle_duration_constraint=DurationConstraint(minimum="1m", default="2h", maximum="20h"),
        max_running_duration_constraint=DurationConstraint(minimum="2m", default="2h", maximum="20h"),
        max_non_interaction_duration="2d",
        max_unused_duration="1d",
        configuration_override={
            "a": "b",
            "c": "my-new-d",
        },
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        triton_enabled=False,
    )

    assert dai_setup_equals(updated_default_dai_setup, want_updated_default_dai_setup)

    # Extra check that workspace-scoped DAISetup reflects these changes.
    time.sleep(CACHE_SYNC_SECONDS)

    random_dai_setup = dai_setup_client_super_admin.get_dai_setup(
        workspace_id="whatever-workspace-just-please-do-not-have-foo"
    )

    assert random_dai_setup.cpu_constraint == NumericConstraint(minimum="2", default="3", maximum="4")
    assert random_dai_setup.gpu_constraint == NumericConstraint(minimum="3", default="4", maximum="5")
    assert random_dai_setup.memory_bytes_constraint == NumericConstraint(minimum="2Gi", default="4Gi", maximum="6Gi")
    assert random_dai_setup.storage_bytes_constraint == NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Gi")
    assert random_dai_setup.max_idle_duration_constraint == DurationConstraint(
        minimum="1m", default="2h", maximum="20h"
    )
    assert random_dai_setup.max_running_duration_constraint == DurationConstraint(
        minimum="2m", default="2h", maximum="20h"
    )
    assert random_dai_setup.max_non_interaction_duration == "2d"
    assert random_dai_setup.max_unused_duration == "1d"
    assert random_dai_setup.configuration_override == {
        "a": "b",
        "c": "my-new-d",
    }

    assert yaml_equal(
        yaml1=random_dai_setup.yaml_pod_template_spec,
        yaml2=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
    )

    assert yaml_equal(
        yaml1=random_dai_setup.yaml_gpu_tolerations,
        yaml2=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
    )
    assert random_dai_setup.triton_enabled == default_dai_setup.triton_enabled
