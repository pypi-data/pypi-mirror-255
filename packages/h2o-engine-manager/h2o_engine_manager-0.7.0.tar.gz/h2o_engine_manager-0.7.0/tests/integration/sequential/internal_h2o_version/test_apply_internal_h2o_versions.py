from typing import List

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.internal_h2o_version.version import InternalH2OVersion
from h2o_engine_manager.clients.internal_h2o_version.version_config import (
    InternalH2OVersionConfig,
)


def test_apply_internal_h2o_versions(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    v1 = InternalH2OVersionConfig(
        internal_h2o_version_id="3.40.0.4",
        image="h2o-3.40.0.4",
        aliases=["latest", "foo", "momma"],
    )
    v2 = InternalH2OVersionConfig(
        internal_h2o_version_id="3.38.0.4",
        image="h2o-3.38.0.4",
        aliases=["latest", "bar"]
    )
    v3 = InternalH2OVersionConfig(
        internal_h2o_version_id="3.36.1.5",
        image="h2o-3.36.1.5",
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets=["secret1", "secret2"],
        gpu_resource_name="whatever",
        annotations={"key1": "value1", "key2": "value2"},
        deprecated=True,
        aliases=["foo", "latest"],
    )

    configs = [v1, v2, v3]
    versions = internal_h2o_version_client.apply_internal_h2o_versions(version_configs=configs)
    want_versions = [
        InternalH2OVersion(
            name="internalH2OVersions/3.40.0.4",
            version="3.40.0.4",
            aliases=["momma"],
            deprecated=False,
            image="h2o-3.40.0.4",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=[],
            gpu_resource_name="nvidia.com/gpu",
            annotations={},
        ),
        InternalH2OVersion(
            name="internalH2OVersions/3.38.0.4",
            version="3.38.0.4",
            aliases=["bar"],
            deprecated=False,
            image="h2o-3.38.0.4",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=[],
            gpu_resource_name="nvidia.com/gpu",
            annotations={},
        ),
        InternalH2OVersion(
            name="internalH2OVersions/3.36.1.5",
            version="3.36.1.5",
            aliases=["foo", "latest"],
            deprecated=True,
            image="h2o-3.36.1.5",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
            image_pull_secrets=["secret1", "secret2"],
            gpu_resource_name="whatever",
            annotations={"key1": "value1", "key2": "value2"},
        ),
    ]

    assert_internal_h2o_versions_equal(want_versions=want_versions, versions=versions)


def assert_internal_h2o_versions_equal(want_versions: List[InternalH2OVersion], versions: List[InternalH2OVersion]):
    assert len(want_versions) == len(versions)

    for i in range(len(want_versions)):
        assert want_versions[i].name == versions[i].name
        assert want_versions[i].version == versions[i].version
        assert want_versions[i].aliases == versions[i].aliases
        assert want_versions[i].deprecated == versions[i].deprecated
        assert want_versions[i].image == versions[i].image
        assert want_versions[i].image_pull_policy == versions[i].image_pull_policy
        assert want_versions[i].image_pull_secrets == versions[i].image_pull_secrets
        assert want_versions[i].gpu_resource_name == versions[i].gpu_resource_name
        assert want_versions[i].annotations == versions[i].annotations
