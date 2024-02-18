from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint


def test_get_default_dai_setup(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    default_dai_setup = dai_setup_client_super_admin.get_default_dai_setup()
    assert default_dai_setup.name == "defaultDAISetup"
    assert default_dai_setup.cpu_constraint == NumericConstraint(minimum="1", default="1")
    assert default_dai_setup.gpu_constraint == NumericConstraint(minimum="0", default="0")
    assert default_dai_setup.memory_bytes_constraint == NumericConstraint(minimum="1Gi", default="1Gi", maximum="1Ti")
    assert default_dai_setup.storage_bytes_constraint == NumericConstraint(minimum="1Gi", default="1Gi", maximum="1Ti")
    assert default_dai_setup.max_idle_duration_constraint == DurationConstraint(
        minimum="5m", default="4h", maximum="200h"
    )
    assert default_dai_setup.max_running_duration_constraint == DurationConstraint(
        minimum="5m", default="4h", maximum="200h"
    )
    assert default_dai_setup.max_non_interaction_duration is None
    assert default_dai_setup.max_unused_duration is None
    assert default_dai_setup.configuration_override == {}
    assert default_dai_setup.yaml_pod_template_spec == ""
    assert default_dai_setup.yaml_gpu_tolerations == ""
    assert default_dai_setup.triton_enabled == False
