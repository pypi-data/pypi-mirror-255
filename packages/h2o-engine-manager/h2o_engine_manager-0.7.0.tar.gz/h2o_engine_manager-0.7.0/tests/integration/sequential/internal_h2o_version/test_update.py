import http
import json

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException


def test_update(internal_h2o_version_client, internal_h2o_versions_cleanup_after):
    v = internal_h2o_version_client.create_version(
        internal_h2o_version_id="3.40.0.3-update",
        image="h2o-3.40.0.3-update",
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets=["secret1", "secret2"],
        gpu_resource_name="amd.com/gpu",
        annotations={"key1": "value1", "key2": "value2"}
    )

    v.version = "will be ignored"
    v.image = "h2o-3.40.0.3-update-new-image"
    v.image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    v.image_pull_secrets = ["secret1", "secret3"]
    v.gpu_resource_name = "nvidia.com/gpu"
    v.annotations = {"key1": "value1-updated", "key2": "value2", "key3": "value3"}
    v.deprecated = False

    updated = internal_h2o_version_client.update_version(internal_h2o_version=v)

    assert updated.name == "internalH2OVersions/3.40.0.3-update"
    assert updated.version == "3.40.0.3-update"
    assert updated.image == "h2o-3.40.0.3-update-new-image"
    assert updated.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert updated.image_pull_secrets == ["secret1", "secret3"]
    assert updated.aliases == []
    assert updated.gpu_resource_name == "nvidia.com/gpu"
    assert updated.annotations == {"key1": "value1-updated", "key2": "value2", "key3": "value3"}
    assert updated.deprecated == False
