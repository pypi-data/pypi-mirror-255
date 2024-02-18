import os

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.default_h2o_setup.setup import DefaultH2OSetup
from tests.integration.sequential.h2o_setup.test_h2o_setup_update import yaml_equal


def assert_default_h2o_setup_equals(a: DefaultH2OSetup, b: DefaultH2OSetup):
    assert a.name == b.name
    assert a.node_count_constraint == b.node_count_constraint
    assert a.cpu_constraint == b.cpu_constraint
    assert a.gpu_constraint == b.gpu_constraint
    assert a.memory_bytes_constraint == b.memory_bytes_constraint
    assert a.max_idle_duration_constraint == b.max_idle_duration_constraint
    assert a.max_running_duration_constraint == b.max_running_duration_constraint
    assert yaml_equal(yaml1=a.yaml_pod_template_spec, yaml2=b.yaml_pod_template_spec)
    assert yaml_equal(yaml1=a.yaml_gpu_tolerations, yaml2=b.yaml_gpu_tolerations)


def test_default_h2o_setup_created(h2o_setup_client_super_admin):
    default_h2o_setup = h2o_setup_client_super_admin.get_default_h2o_setup()

    want_setup = DefaultH2OSetup(
        name="defaultH2OSetup",
        node_count_constraint=NumericConstraint(minimum="1", default="1", maximum="16"),
        cpu_constraint=NumericConstraint(minimum="1", default="1", maximum="30"),
        gpu_constraint=NumericConstraint(minimum="0", default="0", maximum="1"),
        memory_bytes_constraint=NumericConstraint(minimum="2Gi", default="4Gi", maximum="250Gi"),
        max_idle_duration_constraint=DurationConstraint(minimum="0s", default="1h"),
        max_running_duration_constraint=DurationConstraint(minimum="0s", default="2d"),
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
    )

    assert_default_h2o_setup_equals(want_setup, default_h2o_setup)
