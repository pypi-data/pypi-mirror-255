import http
import json

import pytest

from h2o_engine_manager.clients.exception import CustomApiException


def test_assign_internal_dai_version_aliases(internal_dai_version_client, internal_dai_versions_cleanup_after):
    internal_dai_version_client.create_version(
        internal_dai_version_id="1.10.6",
        image="dai-1.10.6",
    )
    internal_dai_version_client.create_version(
        internal_dai_version_id="1.10.7",
        image="dai-1.10.7",
    )
    internal_dai_version_client.create_version(
        internal_dai_version_id="1.10.8",
        image="dai-1.10.8",
    )

    internal_dai_version_client.assign_aliases(internal_dai_version_id="1.10.6", aliases=["foo"])
    internal_dai_version_client.assign_aliases(internal_dai_version_id="1.10.7", aliases=["bar", "baz"])
    versions = internal_dai_version_client.assign_aliases(
        internal_dai_version_id="1.10.8", aliases=["latest", "wow"],
    )

    assert len(versions) == 3
    assert versions[0].internal_dai_version_id == "1.10.8"
    assert versions[0].aliases == ["latest", "wow"]
    assert versions[1].internal_dai_version_id == "1.10.7"
    assert versions[1].aliases == ["bar", "baz"]
    assert versions[2].internal_dai_version_id == "1.10.6"
    assert versions[2].aliases == ["foo"]

    # Nothing will change when assigning the existing aliases.
    versions = internal_dai_version_client.assign_aliases(
        internal_dai_version_id="1.10.7", aliases=["bar", "baz"],
    )
    assert versions[0].internal_dai_version_id == "1.10.8"
    assert versions[0].aliases == ["latest", "wow"]
    assert versions[1].internal_dai_version_id == "1.10.7"
    assert versions[1].aliases == ["bar", "baz"]
    assert versions[2].internal_dai_version_id == "1.10.6"
    assert versions[2].aliases == ["foo"]

    # Remove alias "wow" by assigning reduced existing aliases.
    versions = internal_dai_version_client.assign_aliases(
        internal_dai_version_id="1.10.8", aliases=["latest"],
    )
    assert versions[0].internal_dai_version_id == "1.10.8"
    assert versions[0].aliases == ["latest"]
    assert versions[1].internal_dai_version_id == "1.10.7"
    assert versions[1].aliases == ["bar", "baz"]
    assert versions[2].internal_dai_version_id == "1.10.6"
    assert versions[2].aliases == ["foo"]

    # Move alias "latest" to another version
    versions = internal_dai_version_client.assign_aliases(
        internal_dai_version_id="1.10.7", aliases=["bar", "baz", "latest"],
    )
    assert versions[0].internal_dai_version_id == "1.10.8"
    assert versions[0].aliases == []
    assert versions[1].internal_dai_version_id == "1.10.7"
    assert versions[1].aliases == ["bar", "baz", "latest"]
    assert versions[2].internal_dai_version_id == "1.10.6"
    assert versions[2].aliases == ["foo"]

    # Add new alias
    versions = internal_dai_version_client.assign_aliases(
        internal_dai_version_id="1.10.6", aliases=["foo", "new-foo"],
    )
    assert versions[0].internal_dai_version_id == "1.10.8"
    assert versions[0].aliases == []
    assert versions[1].internal_dai_version_id == "1.10.7"
    assert versions[1].aliases == ["bar", "baz", "latest"]
    assert versions[2].internal_dai_version_id == "1.10.6"
    assert versions[2].aliases == ["foo", "new-foo"]

    # Delete all aliases from 1.10.7
    versions = internal_dai_version_client.assign_aliases(
        internal_dai_version_id="1.10.7", aliases=[],
    )
    assert versions[0].internal_dai_version_id == "1.10.8"
    assert versions[0].aliases == []
    assert versions[1].internal_dai_version_id == "1.10.7"
    assert versions[1].aliases == []
    assert versions[2].internal_dai_version_id == "1.10.6"
    assert versions[2].aliases == ["foo", "new-foo"]


def test_assign_internal_dai_version_alias_conflict(internal_dai_version_client, internal_dai_versions_cleanup_after):
    internal_dai_version_client.create_version(
        internal_dai_version_id="1.10.6",
        image="dai-1.10.6",
    )
    internal_dai_version_client.create_version(
        internal_dai_version_id="1.10.7",
        image="dai-1.10.7",
    )

    with pytest.raises(CustomApiException) as exc:
        internal_dai_version_client.assign_aliases(internal_dai_version_id="1.10.6", aliases=["1.10.7"])

    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'alias conflict: version 1.10.7 already exists, cannot assign the same named alias 1.10.7' \
           in json.loads(exc.value.body)["message"]


def test_assign_non_existing_version(internal_dai_version_client, internal_dai_versions_cleanup_after):
    with pytest.raises(CustomApiException) as exc:
        internal_dai_version_client.assign_aliases(internal_dai_version_id="non-existing", aliases=["1.10.7"])

    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_assign_invalid_version_name(internal_dai_version_client, internal_dai_versions_cleanup_after):
    # Server checks for correct InternalDAIVersion resource name format 'internalDAIVersions/*'.

    with pytest.raises(CustomApiException) as exc:
        internal_dai_version_client.assign_aliases(internal_dai_version_id="1.10.7/foo", aliases=["1.10.7"])

    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'invalid InternalDAIVersion name "internalDAIVersions/1.10.7/foo"'
