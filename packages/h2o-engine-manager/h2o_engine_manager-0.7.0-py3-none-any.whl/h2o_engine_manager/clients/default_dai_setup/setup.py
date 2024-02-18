import pprint
from typing import Dict
from typing import Optional

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.duration_constraint import (
    from_api_object as from_duration_constraint_api,
)
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import (
    from_api_object as from_numeric_constraint_api,
)
from h2o_engine_manager.clients.convert import duration_convertor
from h2o_engine_manager.gen.model.default_dai_setup_resource import (
    DefaultDAISetupResource,
)
from h2o_engine_manager.gen.model.v1_default_dai_setup import V1DefaultDAISetup


class DefaultDAISetup:
    def __init__(
        self,
        name: str,
        cpu_constraint: NumericConstraint,
        gpu_constraint: NumericConstraint,
        memory_bytes_constraint: NumericConstraint,
        storage_bytes_constraint: NumericConstraint,
        max_idle_duration_constraint: DurationConstraint,
        max_running_duration_constraint: DurationConstraint,
        max_non_interaction_duration: Optional[str],
        max_unused_duration: Optional[str],
        configuration_override: Dict[str, str],
        yaml_pod_template_spec: str,
        yaml_gpu_tolerations: str,
        triton_enabled: bool,
    ):
        self.name = name
        self.cpu_constraint = cpu_constraint
        self.gpu_constraint = gpu_constraint
        self.memory_bytes_constraint = memory_bytes_constraint
        self.storage_bytes_constraint = storage_bytes_constraint
        self.max_idle_duration_constraint = max_idle_duration_constraint
        self.max_running_duration_constraint = max_running_duration_constraint
        self.max_non_interaction_duration = max_non_interaction_duration
        self.max_unused_duration = max_unused_duration
        self.configuration_override = configuration_override
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.yaml_gpu_tolerations = yaml_gpu_tolerations
        self.triton_enabled = triton_enabled

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> DefaultDAISetupResource:
        return DefaultDAISetupResource(
            name=self.name,
            cpu_constraint=self.cpu_constraint.to_api_object(),
            gpu_constraint=self.gpu_constraint.to_api_object(),
            memory_bytes_constraint=self.memory_bytes_constraint.to_api_object(),
            storage_bytes_constraint=self.storage_bytes_constraint.to_api_object(),
            max_idle_duration_constraint=self.max_idle_duration_constraint.to_api_object(),
            max_running_duration_constraint=self.max_running_duration_constraint.to_api_object(),
            max_non_interaction_duration=duration_convertor.none_duration_to_seconds(self.max_non_interaction_duration),
            max_unused_duration=duration_convertor.none_duration_to_seconds(self.max_unused_duration),
            configuration_override=self.configuration_override,
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            yaml_gpu_tolerations=self.yaml_gpu_tolerations,
            triton_enabled=self.triton_enabled,
        )


def from_api_object(api_object: V1DefaultDAISetup) -> DefaultDAISetup:
    return DefaultDAISetup(
        name=api_object.name,
        cpu_constraint=from_numeric_constraint_api(api_object.cpu_constraint),
        gpu_constraint=from_numeric_constraint_api(api_object.gpu_constraint),
        memory_bytes_constraint=from_numeric_constraint_api(api_object.memory_bytes_constraint),
        storage_bytes_constraint=from_numeric_constraint_api(api_object.storage_bytes_constraint),
        max_idle_duration_constraint=from_duration_constraint_api(api_object.max_idle_duration_constraint),
        max_running_duration_constraint=from_duration_constraint_api(api_object.max_running_duration_constraint),
        max_non_interaction_duration=duration_convertor.none_seconds_to_duration(
            api_object.max_non_interaction_duration),
        max_unused_duration=duration_convertor.none_seconds_to_duration(api_object.max_unused_duration),
        configuration_override=api_object.configuration_override,
        yaml_pod_template_spec=api_object.yaml_pod_template_spec,
        yaml_gpu_tolerations=api_object.yaml_gpu_tolerations,
        triton_enabled=api_object.triton_enabled,
    )
