import pprint

from h2o_engine_manager.clients.convert import quantity_convertor
from h2o_engine_manager.gen.model.v1_adjusted_dai_profile import V1AdjustedDAIProfile


class AdjustedDAIProfile:
    def __init__(
        self,
        name: str,
        display_name: str,
        cpu: int,
        adjusted_cpu_reason: str,
        gpu: int,
        adjusted_gpu_reason: str,
        memory_bytes: str,
        adjusted_memory_bytes_reason: str,
        storage_bytes: str,
        adjusted_storage_bytes_reason: str,
        order: int,

    ) -> None:
        self.name = name
        self.display_name = display_name
        self.cpu = cpu
        self.adjusted_cpu_reason = adjusted_cpu_reason
        self.gpu = gpu
        self.adjusted_gpu_reason = adjusted_gpu_reason
        self.memory_bytes = memory_bytes
        self.adjusted_memory_bytes_reason = adjusted_memory_bytes_reason
        self.storage_bytes = storage_bytes
        self.adjusted_storage_bytes_reason = adjusted_storage_bytes_reason
        self.order = order

        self.adjusted_dai_profile_id = ""
        if name:
            self.adjusted_dai_profile_id = self.name.split("/")[1]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)


def from_api_object(api_profile: V1AdjustedDAIProfile) -> AdjustedDAIProfile:
    return AdjustedDAIProfile(
        name=api_profile.name,
        display_name=api_profile.display_name,
        cpu=api_profile.cpu,
        adjusted_cpu_reason=api_profile.adjusted_cpu_reason,
        gpu=api_profile.gpu,
        adjusted_gpu_reason=api_profile.adjusted_gpu_reason,
        memory_bytes=quantity_convertor.number_str_to_quantity(api_profile.memory_bytes),
        adjusted_memory_bytes_reason=api_profile.adjusted_memory_bytes_reason,
        storage_bytes=quantity_convertor.number_str_to_quantity(api_profile.storage_bytes),
        adjusted_storage_bytes_reason=api_profile.adjusted_storage_bytes_reason,
        order=api_profile.order,
    )
