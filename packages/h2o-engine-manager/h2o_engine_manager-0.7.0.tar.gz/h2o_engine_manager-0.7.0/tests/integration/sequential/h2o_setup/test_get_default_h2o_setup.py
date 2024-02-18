from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint


def test_get_default_h2o_setup(
    h2o_setup_client_super_admin,
    create_default_h2o_setup,
    delete_all_h2o_setups_after,
):
    default_h2o_setup = h2o_setup_client_super_admin.get_default_h2o_setup()
    assert default_h2o_setup.name == "defaultH2OSetup"
    assert default_h2o_setup.node_count_constraint == NumericConstraint(minimum="1", default="1")
    assert default_h2o_setup.cpu_constraint == NumericConstraint(minimum="1", default="1")
    assert default_h2o_setup.gpu_constraint == NumericConstraint(minimum="0", default="0")
    assert default_h2o_setup.memory_bytes_constraint == NumericConstraint(minimum="2Gi", default="4Gi")
    assert default_h2o_setup.max_idle_duration_constraint == DurationConstraint(
        minimum="0s", default="1h"
    )
    assert default_h2o_setup.max_running_duration_constraint == DurationConstraint(
        minimum="0s", default="4h"
    )
    assert default_h2o_setup.yaml_pod_template_spec == ""
    assert default_h2o_setup.yaml_gpu_tolerations == ""
