import os

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.default_dai_setup.setup import DefaultDAISetup
from tests.integration.sequential.dai_setup.test_dai_setup_update import yaml_equal


def assert_default_dai_setup_equals(a: DefaultDAISetup, b: DefaultDAISetup):
    assert a.name == b.name
    assert a.cpu_constraint == b.cpu_constraint
    assert a.gpu_constraint == b.gpu_constraint
    assert a.memory_bytes_constraint == b.memory_bytes_constraint
    assert a.storage_bytes_constraint == b.storage_bytes_constraint
    assert a.max_idle_duration_constraint == b.max_idle_duration_constraint
    assert a.max_running_duration_constraint == b.max_running_duration_constraint
    assert a.max_non_interaction_duration == b.max_non_interaction_duration
    assert a.max_unused_duration == b.max_unused_duration
    assert a.configuration_override == b.configuration_override
    assert yaml_equal(yaml1=a.yaml_pod_template_spec, yaml2=b.yaml_pod_template_spec)
    assert yaml_equal(yaml1=a.yaml_gpu_tolerations, yaml2=b.yaml_gpu_tolerations)
    assert a.triton_enabled == b.triton_enabled


def test_default_dai_setup_created(dai_setup_client_super_admin):
    """DAISetup is a singleton. Testing that it does not fail when we want to fetch it.
    Indirectly testing, that a DAISetup exists (that it was created during application startup) even when it wasn't
    created manually via kubectl.
    """
    default_dai_setup = dai_setup_client_super_admin.get_default_dai_setup()

    want_setup = DefaultDAISetup(
        name="defaultDAISetup",
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

    assert_default_dai_setup_equals(want_setup, default_dai_setup)
