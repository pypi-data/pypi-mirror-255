import http
import json
import time
from typing import List

import pytest

from h2o_engine_manager.clients.dai_profile.profile import DAIProfile
from h2o_engine_manager.clients.exception import CustomApiException
from tests.integration.conftest import CACHE_SYNC_SECONDS


def test_daiprofile_order(dai_profile_client, dai_profile_cleanup_after):
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_order(want_profile_ids_order=[], profiles=profiles)

    dai_profile_client.create_profile(
        profile_id="profile1", cpu=10, gpu=20, memory_bytes="200", storage_bytes="400"
    )
    dai_profile_client.create_profile(
        profile_id="profile2", cpu=5, gpu=10, memory_bytes="100", storage_bytes="200"
    )
    dai_profile_client.create_profile(
        profile_id="profile3", cpu=1, gpu=0, memory_bytes="10", storage_bytes="20"
    )

    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_order(want_profile_ids_order=["profile1", "profile2", "profile3"], profiles=profiles)

    with pytest.raises(CustomApiException) as exc:
        dai_profile_client.reorder_profile(profile_id="non-existing", new_order=1)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    with pytest.raises(CustomApiException) as exc:
        dai_profile_client.reorder_profile(profile_id="profile1", new_order=-1)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert f'validation error: new_order (-1) must be >= 0' in json.loads(exc.value.body)["message"]

    # profile3 is already on the last position, order=0 is equal to "last position"
    # This reorder should be no-op.
    profiles = dai_profile_client.reorder_profile(profile_id="profile3", new_order=0)
    assert_profiles_order(want_profile_ids_order=["profile1", "profile2", "profile3"], profiles=profiles)

    profiles = dai_profile_client.reorder_profile(profile_id="profile3", new_order=1)
    assert_profiles_order(want_profile_ids_order=["profile3", "profile1", "profile2"], profiles=profiles)

    dai_profile_client.create_profile(profile_id="profile4", cpu=2, gpu=2, memory_bytes="100", storage_bytes="200")
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_order(want_profile_ids_order=["profile3", "profile1", "profile2", "profile4"], profiles=profiles)

    profiles = dai_profile_client.reorder_profile(profile_id="profile3", new_order=2)
    assert_profiles_order(want_profile_ids_order=["profile1", "profile3", "profile2", "profile4"], profiles=profiles)

    dai_profile_client.delete_profile(profile_id="profile1")
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_order(want_profile_ids_order=["profile3", "profile2", "profile4"], profiles=profiles)

    dai_profile_client.delete_profile(profile_id="profile3")
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_order(want_profile_ids_order=["profile2", "profile4"], profiles=profiles)

    # No-op
    profiles = dai_profile_client.reorder_profile(profile_id="profile2", new_order=1)
    assert_profiles_order(want_profile_ids_order=["profile2", "profile4"], profiles=profiles)

    # Put on the last position when more than max
    profiles = dai_profile_client.reorder_profile(profile_id="profile2", new_order=50)
    assert_profiles_order(want_profile_ids_order=["profile4", "profile2"], profiles=profiles)

    dai_profile_client.delete_profile(profile_id="profile2")
    dai_profile_client.delete_profile(profile_id="profile4")

    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_order(want_profile_ids_order=[], profiles=profiles)


def assert_profiles_order(want_profile_ids_order: List[str], profiles: List[DAIProfile]):
    assert len(want_profile_ids_order) == len(profiles)

    i = 1
    for profile in profiles:
        assert profile.dai_profile_id == want_profile_ids_order[i - 1]
        assert profile.order == i
        i = i + 1
