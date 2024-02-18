import pprint
from typing import Dict
from typing import List

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy


class InternalH2OVersionConfig:
    """
    InternalH2OVersion configuration used as input for apply method.
    """

    def __init__(
        self,
        internal_h2o_version_id: str,
        image: str,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: List[str] = [],
        gpu_resource_name: str = "",
        annotations: Dict[str, str] = {},
        deprecated: bool = False,
        aliases: List[str] = [],
    ) -> None:
        self.internal_h2o_version_id = internal_h2o_version_id
        self.image = image
        self.image_pull_policy = image_pull_policy
        self.image_pull_secrets = image_pull_secrets
        self.gpu_resource_name = gpu_resource_name
        self.annotations = annotations
        self.deprecated = deprecated
        self.aliases = aliases

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
