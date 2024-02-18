import os
import time

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.default_h2o_setup.setup import DefaultH2OSetup
from tests.integration.conftest import CACHE_SYNC_SECONDS
from tests.integration.sequential.h2o_setup.test_h2o_setup_update import (
    h2o_setup_equals,
)
from tests.integration.sequential.h2o_setup.test_h2o_setup_update import yaml_equal


def test_update_h2o_setup(
    h2o_setup_client_super_admin,
    create_default_h2o_setup,
    delete_all_h2o_setups_after,
):
    default_h2o_setup = h2o_setup_client_super_admin.get_default_h2o_setup()

    # Update all fields (except name of course).
    default_h2o_setup.node_count_constraint = NumericConstraint(minimum="2", default="3", maximum="4")
    default_h2o_setup.cpu_constraint = NumericConstraint(minimum="2", default="3", maximum="4")
    default_h2o_setup.gpu_constraint = NumericConstraint(minimum="3", default="4", maximum="5")
    default_h2o_setup.memory_bytes_constraint = NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Gi")
    default_h2o_setup.max_idle_duration_constraint = DurationConstraint(minimum="1m", default="2h", maximum="20h")
    default_h2o_setup.max_running_duration_constraint = DurationConstraint(minimum="2m", default="2h", maximum="20h")
    default_h2o_setup.yaml_pod_template_spec = open(
        os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r"
    ).read()
    default_h2o_setup.yaml_gpu_tolerations = open(
        os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r"
    ).read()

    updated_default_h2o_setup = h2o_setup_client_super_admin.update_default_h2o_setup(
        default_h2o_setup=default_h2o_setup
    )

    want_updated_default_h2o_setup = DefaultH2OSetup(
        name="defaultH2OSetup",
        node_count_constraint=NumericConstraint(minimum="2", default="3", maximum="4"),
        cpu_constraint=NumericConstraint(minimum="2", default="3", maximum="4"),
        gpu_constraint=NumericConstraint(minimum="3", default="4", maximum="5"),
        memory_bytes_constraint=NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Gi"),
        max_idle_duration_constraint=DurationConstraint(minimum="1m", default="2h", maximum="20h"),
        max_running_duration_constraint=DurationConstraint(minimum="2m", default="2h", maximum="20h"),
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
    )

    assert h2o_setup_equals(updated_default_h2o_setup, want_updated_default_h2o_setup)

    # Extra check that workspace-scoped H2OSetup reflects these changes.
    time.sleep(CACHE_SYNC_SECONDS)

    random_h2o_setup = h2o_setup_client_super_admin.get_h2o_setup(
        workspace_id="whatever-workspace-just-please-do-not-have-foo"
    )

    assert random_h2o_setup.node_count_constraint == NumericConstraint(minimum="2", default="3", maximum="4")
    assert random_h2o_setup.cpu_constraint == NumericConstraint(minimum="2", default="3", maximum="4")
    assert random_h2o_setup.gpu_constraint == NumericConstraint(minimum="3", default="4", maximum="5")
    assert random_h2o_setup.memory_bytes_constraint == NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Gi")
    assert random_h2o_setup.max_idle_duration_constraint == DurationConstraint(
        minimum="1m", default="2h", maximum="20h"
    )
    assert random_h2o_setup.max_running_duration_constraint == DurationConstraint(
        minimum="2m", default="2h", maximum="20h"
    )
    assert yaml_equal(
        yaml1=random_h2o_setup.yaml_pod_template_spec,
        yaml2=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
    )

    assert yaml_equal(
        yaml1=random_h2o_setup.yaml_gpu_tolerations,
        yaml2=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
    )
