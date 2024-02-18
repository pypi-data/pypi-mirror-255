from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import jsonref
import pydash
from semver import Version


def read_schema(fname: Path) -> dict:
    """Reading schema from file"""
    with open(fname, "r") as f:
        schema = deepcopy(jsonref.load(f))
        return schema


def check_if_major_version_is_same(
    previous_schema: Dict[str, Any], new_schema: Dict[str, Any]
) -> bool:
    """
    Check if major version changed between IDSs.

    Args:
        previous_schema: version of ids schema before the change
        new_schema: current version of ids schema

    Returns:
        False   - if major versions are different
        True    - if major versions are the same

    """
    previous_identity = get_ids_identity(previous_schema)
    new_identity = get_ids_identity(new_schema)

    if previous_identity.namespace_slug() != new_identity.namespace_slug():
        raise ValueError(
            f"Previous slug and namespace '{previous_identity.namespace_slug()}' and current "
            f"'{new_identity.namespace_slug()}' do not match. Validation can only run for "
            "two versions of the same IDS namespace and slug."
        )
    return previous_identity.version_parts.major == new_identity.version_parts.major


def parse_prefixed_version(version: str) -> Version:
    """Parse a version string consisting of a 'v' followed by a semantic version."""
    if not version.startswith("v"):
        raise ValueError(
            "Version string must start with a 'v' followed by a semantic version. "
            f"Does not start with a 'v': '{version}'."
        )
    return Version.parse(version[1:])


@dataclass
class IdsIdentity:
    """The identity of an IDS: namespace, slug and version"""

    namespace: str
    slug: str
    version: str

    def namespace_slug(self) -> Tuple[str, str]:
        """The namespace and slug, excluding the version."""
        return (self.namespace, self.slug)

    @property
    def version_parts(self) -> Version:
        """Parse version into its parts."""
        return parse_prefixed_version(self.version)

    @property
    def id_uri(self) -> str:
        """A URI for the JSON Schema `$id` keyword."""
        return (
            f"https://ids.tetrascience.com/{self.namespace}/"
            f"{self.slug}/{self.version}/schema.json"
        )

    def __str__(self) -> str:
        return f"{self.namespace}/{self.slug}:{self.version}"


def get_ids_identity(schema: Dict[str, Any]) -> IdsIdentity:
    """
    Given an IDS JSON schema, return the namespace, slug and version
    """
    namespace = pydash.get(obj=schema, path="properties.@idsNamespace.const")
    slug = pydash.get(obj=schema, path="properties.@idsType.const")
    version = pydash.get(obj=schema, path="properties.@idsVersion.const")
    if namespace is None or slug is None or version is None:
        raise ValueError(
            "IDS must contain a namespace, slug and version in 'properties.@idsNamespace.const', "
            "'properties.@idsType.const' and 'properties.@idsVersion.const'."
        )

    return IdsIdentity(namespace, slug, version)
