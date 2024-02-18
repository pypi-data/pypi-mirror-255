import http
import time

import pytest

from h2o_engine_manager.clients.adjusted_dai_profile.adjusted_profile import (
    AdjustedDAIProfile,
)
from h2o_engine_manager.clients.exception import CustomApiException
from tests.integration.conftest import CACHE_SYNC_SECONDS
from tests.integration.sequential.dai_profile.create_profile_request import *


def create_test_profile(dai_profile_client) -> DAIProfile:
    req = CreateDAIProfileRequest(
        profile_id="my-profile",
        cpu=30,
        gpu=999,
        memory_bytes="1000Gi",
        storage_bytes="1000Gi",
    )
    profile = create_profile_from_request(dai_profile_client, req)

    time.sleep(CACHE_SYNC_SECONDS)

    return profile


def test_get_validation(
    adjusted_dai_profile_client,
    create_default_dai_setup,
    delete_all_dai_setups_after,
    dai_profile_cleanup_after,
):
    with pytest.raises(CustomApiException) as exc:
        adjusted_dai_profile_client.get_adjusted_profile(profile_id="notfound", workspace_id="notfound")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    with pytest.raises(CustomApiException) as exc:
        adjusted_dai_profile_client.get_adjusted_profile(profile_id="invalid profile id", workspace_id="notfound")
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST

    with pytest.raises(CustomApiException) as exc:
        adjusted_dai_profile_client.get_adjusted_profile(profile_id="notfound", workspace_id="invalid workspace id")
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_get(
    dai_profile_client,
    adjusted_dai_profile_client,
    dai_profile_cleanup_after,
    create_default_dai_setup,
    create_dai_setup_workspace_adjusted_dai_profiles,
    delete_all_dai_setups_after,
):
    # When
    create_test_profile(dai_profile_client)

    # Then
    p = adjusted_dai_profile_client.get_adjusted_profile(profile_id="my-profile", workspace_id="adjusted-dai-profiles")
    expected = AdjustedDAIProfile(
        cpu=20,
        adjusted_cpu_reason="Profile value of 30 CPU exceeds the workspace max constraint value of 20 CPU.",
        gpu=30,
        adjusted_gpu_reason="Profile value of 999 GPU exceeds the workspace max constraint value of 30 GPU.",
        memory_bytes="1000Gi",
        adjusted_memory_bytes_reason="",
        storage_bytes="1000Gi",
        adjusted_storage_bytes_reason="",
        name="daiProfiles/my-profile",
        display_name="",
        order=1,
    )
    assert p.__dict__ == expected.__dict__
