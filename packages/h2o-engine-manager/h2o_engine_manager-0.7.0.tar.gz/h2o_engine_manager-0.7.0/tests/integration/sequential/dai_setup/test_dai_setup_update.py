import http
import json
import os

import pytest
import yaml
from deepdiff import DeepDiff

from h2o_engine_manager.clients.constraint.duration_constraint import DurationConstraint
from h2o_engine_manager.clients.constraint.numeric_constraint import NumericConstraint
from h2o_engine_manager.clients.dai_setup.client import DAISetupClient
from h2o_engine_manager.clients.dai_setup.setup import DAISetup
from h2o_engine_manager.clients.exception import CustomApiException


def dai_setup_equals(a: DAISetup, b: DAISetup) -> bool:
    return a.name == b.name and \
        a.cpu_constraint == b.cpu_constraint and \
        a.gpu_constraint == b.gpu_constraint and \
        a.memory_bytes_constraint == b.memory_bytes_constraint and \
        a.storage_bytes_constraint == b.storage_bytes_constraint and \
        a.max_idle_duration_constraint == b.max_idle_duration_constraint and \
        a.max_running_duration_constraint == b.max_running_duration_constraint and \
        a.max_non_interaction_duration == b.max_non_interaction_duration and \
        a.max_unused_duration == b.max_unused_duration and \
        a.configuration_override == b.configuration_override and \
        yaml_equal(yaml1=a.yaml_pod_template_spec, yaml2=b.yaml_pod_template_spec) and \
        yaml_equal(yaml1=a.yaml_gpu_tolerations, yaml2=b.yaml_gpu_tolerations) and \
        a.triton_enabled == b.triton_enabled


def yaml_equal(yaml1: str, yaml2: str) -> bool:
    """Return True when two string yaml structures are semantically equal (order of fields does not matter)"""
    dict1 = yaml.safe_load(yaml1)
    dict2 = yaml.safe_load(yaml2)
    diff = DeepDiff(t1=dict1, t2=dict2, ignore_order=True)
    return diff == {}


def assert_default_dai_setup_values(dai_setup_client: DAISetupClient, stp: DAISetup):
    default_dai_setup = dai_setup_client.get_default_dai_setup()

    assert stp.cpu_constraint == default_dai_setup.cpu_constraint
    assert stp.gpu_constraint == default_dai_setup.gpu_constraint
    assert stp.memory_bytes_constraint == default_dai_setup.memory_bytes_constraint
    assert stp.storage_bytes_constraint == default_dai_setup.storage_bytes_constraint
    assert stp.max_idle_duration_constraint == default_dai_setup.max_idle_duration_constraint
    assert stp.max_running_duration_constraint == default_dai_setup.max_running_duration_constraint
    assert stp.max_non_interaction_duration == default_dai_setup.max_non_interaction_duration
    assert stp.max_unused_duration == default_dai_setup.max_unused_duration
    assert stp.configuration_override == default_dai_setup.configuration_override
    assert stp.yaml_pod_template_spec == default_dai_setup.yaml_pod_template_spec
    assert stp.yaml_gpu_tolerations == default_dai_setup.yaml_gpu_tolerations
    assert stp.triton_enabled == default_dai_setup.triton_enabled


def test_update_dai_setup(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="test-update-dai-setup")

    # Checking prerequisites.
    assert stp.name == "workspaces/test-update-dai-setup/daiSetup"
    assert_default_dai_setup_values(dai_setup_client=dai_setup_client_super_admin, stp=stp)

    # Update all fields (except name of course).
    stp.cpu_constraint = NumericConstraint(minimum="2", default="3", maximum="4")
    stp.gpu_constraint = NumericConstraint(minimum="3", default="4", maximum="5")
    stp.memory_bytes_constraint = NumericConstraint(minimum="2Gi", default="4Gi", maximum="6Ti")
    stp.storage_bytes_constraint = NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Ti")
    stp.max_idle_duration_constraint = DurationConstraint(minimum="1m", default="2h", maximum="20h")
    stp.max_running_duration_constraint = DurationConstraint(minimum="2m", default="2h", maximum="20h")
    stp.max_non_interaction_duration = "2d"
    stp.max_unused_duration = "1d"
    stp.configuration_override = {
        "a": "b",
        "c": "my-new-d",
    }
    stp.yaml_pod_template_spec = open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"),
                                      "r").read()
    stp.yaml_gpu_tolerations = open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read()
    stp.triton_enabled = False

    updated_dai_setup = dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)

    want_updated_dai_setup = DAISetup(
        name="workspaces/test-update-dai-setup/daiSetup",
        cpu_constraint=NumericConstraint(minimum="2", default="3", maximum="4"),
        gpu_constraint=NumericConstraint(minimum="3", default="4", maximum="5"),
        memory_bytes_constraint=NumericConstraint(minimum="2Gi", default="4Gi", maximum="6Ti"),
        storage_bytes_constraint=NumericConstraint(minimum="3Gi", default="6Gi", maximum="9Ti"),
        max_idle_duration_constraint=DurationConstraint(minimum="1m", default="2h", maximum="20h"),
        max_running_duration_constraint=DurationConstraint(minimum="2m", default="2h", maximum="20h"),
        max_non_interaction_duration="2d",
        max_unused_duration="1d",
        configuration_override={
            "a": "b",
            "c": "my-new-d",
        },
        yaml_pod_template_spec=open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read(),
        yaml_gpu_tolerations=open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read(),
        triton_enabled=False,
    )

    assert dai_setup_equals(updated_dai_setup, want_updated_dai_setup)


def test_update_with_minimal_values(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="test-update-with-minimal-values")

    # Checking prerequisites.
    assert stp.name == "workspaces/test-update-with-minimal-values/daiSetup"
    assert_default_dai_setup_values(dai_setup_client=dai_setup_client_super_admin, stp=stp)

    stp.cpu_constraint = NumericConstraint(minimum="0", default="1")
    stp.gpu_constraint = NumericConstraint(minimum="0", default="1")
    stp.storage_bytes_constraint = NumericConstraint(minimum="0", default="1")
    stp.memory_bytes_constraint = NumericConstraint(minimum="0", default="0")
    stp.max_idle_duration_constraint = DurationConstraint(minimum="12h", default="13h", )
    stp.max_running_duration_constraint = DurationConstraint(minimum="22h", default="23h")
    stp.yaml_gpu_tolerations = ""
    stp.yaml_pod_template_spec = ""
    stp.max_unused_duration = None
    stp.max_non_interaction_duration = None
    stp.configuration_override = {}
    stp.triton_enabled = False

    updated_stp = dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)

    assert updated_stp.name == "workspaces/test-update-with-minimal-values/daiSetup"
    assert updated_stp.cpu_constraint == NumericConstraint(minimum="0", default="1")
    assert updated_stp.gpu_constraint == NumericConstraint(minimum="0", default="1")
    assert updated_stp.storage_bytes_constraint == NumericConstraint(minimum="0", default="1")
    assert updated_stp.memory_bytes_constraint == NumericConstraint(minimum="0", default="0")
    assert updated_stp.max_idle_duration_constraint == DurationConstraint(minimum="12h", default="13h", )
    assert updated_stp.max_running_duration_constraint == DurationConstraint(minimum="22h", default="23h")
    assert updated_stp.yaml_gpu_tolerations == ""
    assert updated_stp.yaml_pod_template_spec == ""
    assert updated_stp.max_unused_duration is None
    assert updated_stp.max_non_interaction_duration is None
    assert updated_stp.configuration_override == {}
    assert updated_stp.triton_enabled == False


@pytest.mark.parametrize(
    "minimum,default,maximum",
    [
        ("10", "9", "10"),
        ("1", "3", "2"),
        ("3", "1", "2"),
    ],
)
def test_update_cpu_constraint_validation(
    dai_setup_client_super_admin: DAISetupClient,
    create_default_dai_setup,
    delete_all_dai_setups_after,
    minimum,
    default,
    maximum,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="invalid-numeric-constraint")
    stp.cpu_constraint = NumericConstraint(minimum=minimum, default=default, maximum=maximum)

    with pytest.raises(CustomApiException) as exc:
        dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    "minimum,default,maximum",
    [
        ("10h", "9h", "10h"),
        ("1d", "3d", "2d"),
        ("3s", "1s", "2s"),
    ],
)
def test_update_max_running_duration_constraint_validation(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
    minimum,
    default,
    maximum,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="invalid-duration-constraint")
    stp.max_running_duration_constraint = DurationConstraint(minimum=minimum, default=default, maximum=maximum)

    with pytest.raises(CustomApiException) as exc:
        dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    "yaml_spec,err_msg",
    [
        ("    ", "validation error: invalid yamlPodTemplateSpec: missing containers"),
        (open(os.path.join(os.path.dirname(__file__), "pod_template_spec_missing_containers.yaml"), "r").read(),
         "validation error: invalid yamlPodTemplateSpec: missing containers"),
        (open(os.path.join(os.path.dirname(__file__), "pod_template_spec_unknown_field.yaml"), "r").read(),
         "validation error: invalid yamlPodTemplateSpec: error unmarshaling JSON: while decoding JSON: json: unknown field \"foo\""),
        ("aaa",
         'validation error: invalid yamlPodTemplateSpec: error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go value of type v1.PodTemplateSpec')
    ],
)
def test_update_pod_template_spec_validation(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
    yaml_spec,
    err_msg,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="invalid-pod-template-spec")
    stp.yaml_pod_template_spec = yaml_spec

    with pytest.raises(CustomApiException) as exc:
        dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert err_msg == json.loads(exc.value.body)["message"]


@pytest.mark.parametrize(
    "yaml_tolerations,err_msg",
    [
        (open(os.path.join(os.path.dirname(__file__), "gpu_tolerations_invalid.yaml"), "r").read(),
         "validation error: invalid yamlGpuTolerations: error unmarshaling JSON: while decoding JSON: json: unknown field \"foooo\""),
        ("aaaa",
         'validation error: invalid yamlGpuTolerations: error unmarshaling JSON: while decoding JSON: json: cannot unmarshal string into Go value of type []v1.Toleration'),
    ],
)
def test_gpu_tolerations_validation(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
    yaml_tolerations,
    err_msg,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="invalid-gpu-tolerations")
    stp.yaml_gpu_tolerations = yaml_tolerations

    with pytest.raises(CustomApiException) as exc:
        dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert err_msg == json.loads(exc.value.body)["message"]


def test_gpu_tolerations_brackets(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="gpu-tolerations-brackets")
    assert stp.yaml_gpu_tolerations == ""

    # Test that another form of YAML file is accepted by server (using brackets for array)
    stp.yaml_gpu_tolerations = open(
        os.path.join(os.path.dirname(__file__), "gpu_tolerations_with_brackets.yaml"), "r"
    ).read()
    updated_stp = dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)

    # Test that the updated value is equivalent (when not using brackets for array).
    # Convert YAML content into dictionaries and compare these two dictionaries.
    dict1 = yaml.safe_load(updated_stp.yaml_gpu_tolerations)
    dict2 = yaml.safe_load(open(
        os.path.join(os.path.dirname(__file__), "gpu_tolerations_without_brackets.yaml"), "r"
    ).read())
    diff = DeepDiff(t1=dict1, t2=dict2, ignore_order=True)

    # No difference found.
    assert diff == {}


def test_set_unset_yaml_specs(
    dai_setup_client_super_admin,
    create_default_dai_setup,
    delete_all_dai_setups_after,
):
    stp = dai_setup_client_super_admin.get_dai_setup(workspace_id="set-unset-yaml-specs")

    assert stp.yaml_pod_template_spec == ""
    assert stp.yaml_gpu_tolerations == ""

    # Set yaml specs with some valid values.
    stp.yaml_pod_template_spec = open(os.path.join(os.path.dirname(__file__), "pod_template_spec.yaml"), "r").read()
    stp.yaml_gpu_tolerations = open(os.path.join(os.path.dirname(__file__), "gpu_tolerations.yaml"), "r").read()
    dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)

    assert stp.yaml_pod_template_spec != ""
    assert stp.yaml_gpu_tolerations != ""

    # Unset yaml specs.
    stp.yaml_pod_template_spec = ""
    stp.yaml_gpu_tolerations = ""
    dai_setup_client_super_admin.update_dai_setup(dai_setup=stp)

    assert stp.yaml_pod_template_spec == ""
    assert stp.yaml_gpu_tolerations == ""
