import pprint


class DAIProfileConfig:
    """
    DAIProfile configuration used as input for apply method.
    """
    def __init__(
        self,
        dai_profile_id: str,
        cpu: int,
        gpu: int,
        memory_bytes: str,
        storage_bytes: str,
        display_name: str = "",

    ) -> None:
        self.dai_profile_id = dai_profile_id
        self.cpu = cpu
        self.gpu = gpu
        self.memory_bytes = memory_bytes
        self.storage_bytes = storage_bytes
        self.display_name = display_name

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
