import time
from typing import List

from h2o_engine_manager.clients.adjusted_dai_profile.adjusted_profile import (
    AdjustedDAIProfile,
)
from h2o_engine_manager.clients.adjusted_dai_profile.client import (
    AdjustedDAIProfileClient,
)
from tests.integration.conftest import CACHE_SYNC_SECONDS


def test_list_order(
    dai_profile_client,
    adjusted_dai_profile_client: AdjustedDAIProfileClient,
    create_default_dai_setup,
    delete_all_dai_setups_after,
    dai_profile_cleanup_after,
):
    # Create three profiles. Should be ordered in the order they were created.
    dai_profile_client.create_profile(
        profile_id="profile1", cpu=1, gpu=0, memory_bytes="10", storage_bytes="20"
    )
    dai_profile_client.create_profile(
        profile_id="profile2", cpu=1, gpu=0, memory_bytes="10", storage_bytes="20"
    )
    dai_profile_client.create_profile(
        profile_id="profile3", cpu=1, gpu=0, memory_bytes="10", storage_bytes="20"
    )
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = adjusted_dai_profile_client.list_all_adjusted_profiles(workspace_id="w1")
    assert_order(want_ids_order=["profile1", "profile2", "profile3"], profiles=profiles)

    # Create new profile and reorder it on the first position.
    dai_profile_client.create_profile(
        profile_id="profile4", cpu=1, gpu=0, memory_bytes="10", storage_bytes="20"
    )
    dai_profile_client.reorder_profile(profile_id="profile4", new_order=1)
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = adjusted_dai_profile_client.list_all_adjusted_profiles(workspace_id="w1")
    assert_order(want_ids_order=["profile4", "profile1", "profile2", "profile3"], profiles=profiles)

    # Delete profile. Profiles behind should be shifted to fill the gap.
    dai_profile_client.delete_profile(profile_id="profile1")
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = adjusted_dai_profile_client.list_all_adjusted_profiles(workspace_id="w1")
    assert_order(want_ids_order=["profile4", "profile2", "profile3"], profiles=profiles)

    # Move profile to the last position using zero.
    dai_profile_client.reorder_profile(profile_id="profile2", new_order=0)
    time.sleep(CACHE_SYNC_SECONDS)
    profiles = adjusted_dai_profile_client.list_all_adjusted_profiles(workspace_id="w1")
    assert_order(want_ids_order=["profile4", "profile3", "profile2"], profiles=profiles)


def assert_order(want_ids_order: List[str], profiles: List[AdjustedDAIProfile]):
    assert len(want_ids_order) == len(profiles)

    i = 1
    for profile in profiles:
        assert profile.adjusted_dai_profile_id == want_ids_order[i - 1]
        assert profile.order == i
        i = i + 1
