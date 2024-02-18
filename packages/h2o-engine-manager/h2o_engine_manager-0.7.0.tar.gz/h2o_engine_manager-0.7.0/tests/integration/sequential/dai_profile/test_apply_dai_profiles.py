import time
from typing import List

from h2o_engine_manager.clients.dai_profile.profile import DAIProfile
from h2o_engine_manager.clients.dai_profile.profile_config import DAIProfileConfig
from tests.integration.conftest import CACHE_SYNC_SECONDS


def test_apply_dai_profiles(dai_profile_client, dai_profile_cleanup_after):
    p1 = DAIProfileConfig(
        dai_profile_id="small", cpu=1, gpu=0, memory_bytes="1Gi", storage_bytes="1Gi", display_name="Small",
    )
    p2 = DAIProfileConfig(
        dai_profile_id="medium", cpu=2, gpu=1, memory_bytes="2Gi", storage_bytes="2Gi", display_name="Medium",
    )
    p3 = DAIProfileConfig(
        dai_profile_id="large", cpu=3, gpu=2, memory_bytes="3Gi", storage_bytes="3Gi", display_name="Large",
    )
    configs = [p1, p2, p3]

    profiles = dai_profile_client.apply_dai_profiles(dai_profile_configs=configs)
    want_profiles = [
        DAIProfile(name="daiProfiles/small", display_name="Small", cpu=1, gpu=0,
                   memory_bytes="1Gi", storage_bytes="1Gi", order=1),
        DAIProfile(name="daiProfiles/medium", display_name="Medium", cpu=2, gpu=1,
                   memory_bytes="2Gi", storage_bytes="2Gi", order=2),
        DAIProfile(name="daiProfiles/large", display_name="Large", cpu=3, gpu=2,
                   memory_bytes="3Gi", storage_bytes="3Gi", order=3),
    ]
    assert_profiles_equal(want_profiles=want_profiles, profiles=profiles)

    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_equal(want_profiles=want_profiles, profiles=profiles)

    # Apply again.
    p4 = DAIProfileConfig(
        dai_profile_id="mega", cpu=10, gpu=10, memory_bytes="8Gi", storage_bytes="8Gi", display_name="Mega",
    )
    p3 = DAIProfileConfig(
        dai_profile_id="large", cpu=3, gpu=2, memory_bytes="3Gi", storage_bytes="3Gi", display_name="Large",
    )
    p2 = DAIProfileConfig(
        dai_profile_id="medium", cpu=5, gpu=5, memory_bytes="4Gi", storage_bytes="4Gi", display_name="Medium updated",
    )
    configs = [p4, p3, p2]
    profiles = dai_profile_client.apply_dai_profiles(dai_profile_configs=configs)
    want_profiles = [
        DAIProfile(name="daiProfiles/mega", display_name="Mega", cpu=10, gpu=10,
                   memory_bytes="8Gi", storage_bytes="8Gi", order=1),
        DAIProfile(name="daiProfiles/large", display_name="Large", cpu=3, gpu=2,
                   memory_bytes="3Gi", storage_bytes="3Gi", order=2),
        DAIProfile(name="daiProfiles/medium", display_name="Medium updated", cpu=5, gpu=5,
                   memory_bytes="4Gi", storage_bytes="4Gi", order=3),
    ]
    assert_profiles_equal(want_profiles=want_profiles, profiles=profiles)

    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    assert_profiles_equal(want_profiles=want_profiles, profiles=profiles)


def assert_profiles_equal(want_profiles: List[DAIProfile], profiles: List[DAIProfile]):
    assert len(want_profiles) == len(profiles)

    for i in range(len(want_profiles)):
        assert want_profiles[i].name == profiles[i].name
        assert want_profiles[i].dai_profile_id == profiles[i].dai_profile_id
        assert want_profiles[i].display_name == profiles[i].display_name
        assert want_profiles[i].cpu == profiles[i].cpu
        assert want_profiles[i].gpu == profiles[i].gpu
        assert want_profiles[i].memory_bytes == profiles[i].memory_bytes
        assert want_profiles[i].storage_bytes == profiles[i].storage_bytes
        assert want_profiles[i].order == profiles[i].order
