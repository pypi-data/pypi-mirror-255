import os
import time

import pytest
from kubernetes import config

import h2o_engine_manager
from h2o_engine_manager.clients.dai_engine_constraint.client import (
    DAIEngineConstraintSetClient,
)
from h2o_engine_manager.clients.dai_setup.client import DAISetupClient
from h2o_engine_manager.clients.engine.client import EngineClient
from h2o_engine_manager.clients.h2o_engine_constraint.client import (
    H2OEngineConstraintSetClient,
)
from h2o_engine_manager.clients.h2o_setup.client import H2OSetupClient
from h2o_engine_manager.clients.internal_dai_version.client import (
    InternalDAIVersionClient,
)
from h2o_engine_manager.clients.internal_h2o_version.client import (
    InternalH2OVersionClient,
)
from testing.kubectl import kubectl_apply
from testing.kubectl import kubectl_delete_resource_all

# Kubernetes cache needs to take some time to detect changes in k8s server.
CACHE_SYNC_SECONDS = 0.2

# To have control over the provisioned test resources, a workspace with related DAISetup is used.
DAI_SETUP_WORKSPACE = "dai-setup"
DAI_LIFECYCLE_WORKSPACE = "dai-lifecycle"
DAI_CONNECT_WORKSPACE = "dai-connect"

H2O_SETUP_WORKSPACE = "h2o-setup"

# Non-mocked version of DAI.
NON_MOCKED_DAI_VERSION = "1.10.4"


@pytest.fixture(scope="session")
def system_namespace():
    return os.getenv("TEST_K8S_SYSTEM_NAMESPACE")


@pytest.fixture(scope="session")
def load_kube_config():
    config.load_config()


@pytest.fixture(scope="function")
def sync_cache():
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def create_default_dai_setup(load_kube_config, system_namespace):
    """Create DefaultDAISetup"""
    kubectl_apply(
        path=(os.path.join(os.path.dirname(__file__), "test_data", "dai_setups", "system.default.yaml")),
        namespace=system_namespace,
    )

    # Created default DAISetup is almost always used in tests via API
    # that uses cache. Wait a short while so the cache is synced in tests
    # to avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def create_dai_setup_workspace_dai_setup(load_kube_config, system_namespace):
    """Create DAISetup for workspace dai-setup"""
    kubectl_apply(
        path=(os.path.join(os.path.dirname(__file__), "test_data", "dai_setups", "dai-setup.yaml")),
        namespace=system_namespace,
    )

    # To avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def create_dai_setup_workspace_adjusted_dai_profiles(load_kube_config, system_namespace):
    """Create DAISetup for workspace adjusted-dai-profiles"""
    kubectl_apply(
        path=(os.path.join(os.path.dirname(__file__), "test_data", "dai_setups", "adjusted-dai-profiles.yaml")),
        namespace=system_namespace,
    )

    # To avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def delete_all_dai_setups_after(load_kube_config, system_namespace):
    """Delete all kube DAISetups after test."""
    yield

    kubectl_delete_resource_all(
        resource="daistp",
        namespace=system_namespace,
    )

    # To avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def create_default_h2o_setup(load_kube_config, system_namespace):
    """Create DefaultH2OSetup"""
    kubectl_apply(
        path=(os.path.join(os.path.dirname(__file__), "test_data", "h2o_setups", "system.default.yaml")),
        namespace=system_namespace,
    )

    # To avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def create_h2o_setup_workspace_h2o_setup(load_kube_config, system_namespace):
    """Create DAISetup for workspace dai-setup"""
    kubectl_apply(
        path=(os.path.join(os.path.dirname(__file__), "test_data", "h2o_setups", "h2o-setup.yaml")),
        namespace=system_namespace,
    )

    # To avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="function")
def delete_all_h2o_setups_after(load_kube_config, system_namespace):
    """Delete all kube H2OSetups after test."""
    yield

    kubectl_delete_resource_all(
        resource="h2ostp",
        namespace=system_namespace,
    )

    # To avoid race conditions.
    time.sleep(CACHE_SYNC_SECONDS)


@pytest.fixture(scope="session")
def clients():
    return h2o_engine_manager.login_custom(
        endpoint=os.getenv("AIEM_SCHEME") + "://" + os.getenv("AIEM_HOST"),
        refresh_token=os.getenv("PLATFORM_TOKEN_USER"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def admin_clients():
    return h2o_engine_manager.login_custom(
        endpoint=os.getenv("AIEM_SCHEME") + "://" + os.getenv("AIEM_HOST"),
        refresh_token=os.getenv("PLATFORM_TOKEN_ADMIN"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def super_admin_clients():
    return h2o_engine_manager.login_custom(
        endpoint=os.getenv("AIEM_SCHEME") + "://" + os.getenv("AIEM_HOST"),
        refresh_token=os.getenv("PLATFORM_TOKEN_SUPER_ADMIN"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def dai_client(clients):
    return clients.dai_engine_client


@pytest.fixture(scope="session")
def dai_admin_client(admin_clients):
    return admin_clients.dai_engine_client


@pytest.fixture(scope="session")
def h2o_engine_client(clients):
    return clients.h2o_engine_client


@pytest.fixture(scope="session")
def engine_client():
    return EngineClient(
        url=os.getenv("AIEM_SCHEME") + "://" + os.getenv("AIEM_HOST"),
        platform_token=os.getenv("PLATFORM_TOKEN_USER"),
        platform_oidc_url=os.getenv("PLATFORM_OIDC_URL"),
        platform_oidc_client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def dai_engine_constraint_set_client():
    return DAIEngineConstraintSetClient(
        url=os.getenv("AIEM_SCHEME") + "://" + os.getenv("AIEM_HOST"),
        platform_token=os.getenv("PLATFORM_TOKEN_USER"),
        platform_oidc_url=os.getenv("PLATFORM_OIDC_URL"),
        platform_oidc_client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def h2o_engine_constraint_set_client():
    return H2OEngineConstraintSetClient(
        url=os.getenv("AIEM_SCHEME") + "://" + os.getenv("AIEM_HOST"),
        platform_token=os.getenv("PLATFORM_TOKEN_USER"),
        platform_oidc_url=os.getenv("PLATFORM_OIDC_URL"),
        platform_oidc_client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def dai_profile_client(super_admin_clients):
    return super_admin_clients.dai_profile_client


@pytest.fixture(scope="session")
def adjusted_dai_profile_client(dai_client):
    return dai_client.adjusted_profile_client


@pytest.fixture(scope="function")
def dai_profile_cleanup_after(dai_profile_client):
    yield

    time.sleep(CACHE_SYNC_SECONDS)
    profiles = dai_profile_client.list_all_profiles()
    for p in profiles:
        dai_profile_client.delete_profile(profile_id=p.dai_profile_id)


@pytest.fixture(scope="session")
def websocket_base_url() -> str:
    scheme = os.getenv("AIEM_SCHEME")
    host = os.getenv("AIEM_HOST")

    if scheme == "http":
        return f"ws://{host}"
    elif scheme == "https":
        return f"wss://{host}"

    raise ValueError(f"AIEM_SCHEME must be either http or https, got scheme: {scheme}")


@pytest.fixture(scope="session")
def internal_dai_version_client(super_admin_clients):
    return super_admin_clients.internal_dai_version_client


@pytest.fixture(scope="session")
def internal_dai_version_client_standard_user(clients) -> InternalDAIVersionClient:
    return clients.internal_dai_version_client


@pytest.fixture(scope="session")
def internal_dai_version_client_admin(admin_clients) -> InternalDAIVersionClient:
    return admin_clients.internal_dai_version_client


@pytest.fixture(scope="function")
def internal_dai_versions_cleanup_after(internal_dai_version_client):
    yield

    versions = internal_dai_version_client.list_all_versions()
    for v in versions:
        internal_dai_version_client.delete_version(internal_dai_version_id=v.internal_dai_version_id)


@pytest.fixture(scope="session")
def internal_h2o_version_client(super_admin_clients):
    return super_admin_clients.internal_h2o_version_client


@pytest.fixture(scope="session")
def internal_h2o_version_client_standard_user(clients) -> InternalH2OVersionClient:
    return clients.internal_h2o_version_client


@pytest.fixture(scope="session")
def internal_h2o_version_client_admin(admin_clients) -> InternalH2OVersionClient:
    return admin_clients.internal_h2o_version_client


@pytest.fixture(scope="session")
def dai_setup_client_standard_user(clients) -> DAISetupClient:
    return clients.dai_setup_client


@pytest.fixture(scope="session")
def dai_setup_client_super_admin(super_admin_clients) -> DAISetupClient:
    return super_admin_clients.dai_setup_client


@pytest.fixture(scope="session")
def h2o_setup_client_standard_user(clients) -> H2OSetupClient:
    return clients.h2o_setup_client


@pytest.fixture(scope="session")
def h2o_setup_client_super_admin(super_admin_clients) -> H2OSetupClient:
    return super_admin_clients.h2o_setup_client


@pytest.fixture(scope="function")
def internal_h2o_versions_cleanup_after(internal_h2o_version_client):
    yield

    versions = internal_h2o_version_client.list_all_versions()
    for v in versions:
        internal_h2o_version_client.delete_version(internal_h2o_version_id=v.internal_h2o_version_id)
