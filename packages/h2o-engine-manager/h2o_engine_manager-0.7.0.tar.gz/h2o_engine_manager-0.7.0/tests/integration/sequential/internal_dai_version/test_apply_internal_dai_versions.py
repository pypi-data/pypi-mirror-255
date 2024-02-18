from typing import List

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.internal_dai_version.version import InternalDAIVersion
from h2o_engine_manager.clients.internal_dai_version.version_config import (
    InternalDAIVersionConfig,
)


def test_apply_internal_dai_versions(internal_dai_version_client, internal_dai_versions_cleanup_after):
    v1 = InternalDAIVersionConfig(
        internal_dai_version_id="1.10.7",
        image="dai-1.10.7",
        aliases=["latest", "foo"],
    )
    v2 = InternalDAIVersionConfig(
        internal_dai_version_id="1.10.6.1",
        image="dai-1.10.6.1",
    )
    v3 = InternalDAIVersionConfig(
        internal_dai_version_id="1.10.6",
        image="dai-1.10.6",
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets=["secret1", "secret2"],
        gpu_resource_name="whatever",
        data_directory_storage_class="yolo",
        annotations={"key1": "value1", "key2": "value2"},
        deprecated=True,
        aliases=["foo"],
    )

    configs = [v1, v2, v3]
    versions = internal_dai_version_client.apply_internal_dai_versions(version_configs=configs)
    want_versions = [
        InternalDAIVersion(
            name="internalDAIVersions/1.10.7",
            version="1.10.7",
            aliases=["latest"],
            deprecated=False,
            image="dai-1.10.7",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=[],
            gpu_resource_name="nvidia.com/gpu",
            data_directory_storage_class="",
            annotations={},
        ),
        InternalDAIVersion(
            name="internalDAIVersions/1.10.6.1",
            version="1.10.6.1",
            aliases=[],
            deprecated=False,
            image="dai-1.10.6.1",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=[],
            gpu_resource_name="nvidia.com/gpu",
            data_directory_storage_class="",
            annotations={},
        ),
        InternalDAIVersion(
            name="internalDAIVersions/1.10.6",
            version="1.10.6",
            aliases=["foo"],
            deprecated=True,
            image="dai-1.10.6",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
            image_pull_secrets=["secret1", "secret2"],
            gpu_resource_name="whatever",
            data_directory_storage_class="yolo",
            annotations={"key1": "value1", "key2": "value2"},
        ),
    ]

    assert_internal_dai_versions_equal(want_versions=want_versions, versions=versions)

    # Apply again.
    v4 = InternalDAIVersionConfig(
        internal_dai_version_id="1.10.8",
        image="dai-1.10.8",
        aliases=["latest"]
    )
    v3 = InternalDAIVersionConfig(
        internal_dai_version_id="1.10.6",
        image="dai-1.10.6",
        aliases=["roland", "elvira"]
    )
    configs = [v4, v3]
    versions = internal_dai_version_client.apply_internal_dai_versions(version_configs=configs)
    want_versions = [
        InternalDAIVersion(
            name="internalDAIVersions/1.10.8",
            version="1.10.8",
            aliases=["latest"],
            deprecated=False,
            image="dai-1.10.8",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=[],
            gpu_resource_name="nvidia.com/gpu",
            data_directory_storage_class="",
            annotations={},
        ),
        InternalDAIVersion(
            name="internalDAIVersions/1.10.6",
            version="1.10.6",
            aliases=["roland", "elvira"],
            deprecated=False,
            image="dai-1.10.6",
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets=[],
            gpu_resource_name="nvidia.com/gpu",
            data_directory_storage_class="",
            annotations={},
        ),
    ]

    assert_internal_dai_versions_equal(want_versions=want_versions, versions=versions)


def assert_internal_dai_versions_equal(want_versions: List[InternalDAIVersion], versions: List[InternalDAIVersion]):
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
        assert want_versions[i].data_directory_storage_class == versions[i].data_directory_storage_class
        assert want_versions[i].annotations == versions[i].annotations
