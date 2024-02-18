import pprint

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.duration_constraint import (
    from_api_object as from_duration_constraint_api,
)
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import (
    from_api_object as from_numeric_constraint_api,
)
from h2o_engine_manager.gen.model.default_h2_o_setup_resource import (
    DefaultH2OSetupResource,
)
from h2o_engine_manager.gen.model.v1_default_h2_o_setup import V1DefaultH2OSetup


class DefaultH2OSetup:
    def __init__(
        self,
        name: str,
        node_count_constraint: NumericConstraint,
        cpu_constraint: NumericConstraint,
        gpu_constraint: NumericConstraint,
        memory_bytes_constraint: NumericConstraint,
        max_idle_duration_constraint: DurationConstraint,
        max_running_duration_constraint: DurationConstraint,
        yaml_pod_template_spec: str,
        yaml_gpu_tolerations: str,
    ):
        self.name = name
        self.node_count_constraint = node_count_constraint
        self.cpu_constraint = cpu_constraint
        self.gpu_constraint = gpu_constraint
        self.memory_bytes_constraint = memory_bytes_constraint
        self.max_idle_duration_constraint = max_idle_duration_constraint
        self.max_running_duration_constraint = max_running_duration_constraint
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.yaml_gpu_tolerations = yaml_gpu_tolerations

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> DefaultH2OSetupResource:
        return DefaultH2OSetupResource(
            name=self.name,
            node_count_constraint=self.node_count_constraint.to_api_object(),
            cpu_constraint=self.cpu_constraint.to_api_object(),
            gpu_constraint=self.gpu_constraint.to_api_object(),
            memory_bytes_constraint=self.memory_bytes_constraint.to_api_object(),
            max_idle_duration_constraint=self.max_idle_duration_constraint.to_api_object(),
            max_running_duration_constraint=self.max_running_duration_constraint.to_api_object(),
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            yaml_gpu_tolerations=self.yaml_gpu_tolerations,
        )


def from_api_object(api_object: V1DefaultH2OSetup) -> DefaultH2OSetup:
    return DefaultH2OSetup(
        name=api_object.name,
        node_count_constraint=from_numeric_constraint_api(api_object.node_count_constraint),
        cpu_constraint=from_numeric_constraint_api(api_object.cpu_constraint),
        gpu_constraint=from_numeric_constraint_api(api_object.gpu_constraint),
        memory_bytes_constraint=from_numeric_constraint_api(api_object.memory_bytes_constraint),
        max_idle_duration_constraint=from_duration_constraint_api(api_object.max_idle_duration_constraint),
        max_running_duration_constraint=from_duration_constraint_api(api_object.max_running_duration_constraint),
        yaml_pod_template_spec=api_object.yaml_pod_template_spec,
        yaml_gpu_tolerations=api_object.yaml_gpu_tolerations,
    )
