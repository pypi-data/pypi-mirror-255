import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import jsonref
import pydash

from ids_validator.convention_versions import Conventions
from ids_validator.ids_node import Node
from ids_validator.utils import IdsIdentity, get_ids_identity


@dataclass()
class IdsArtifact:
    schema: dict = field(default_factory=dict)
    athena: dict = field(default_factory=dict)
    elasticsearch: dict = field(default_factory=dict)
    expected: dict = field(default_factory=dict)
    path: Path = Path()

    def __post_init__(self) -> None:
        deref_schema: Dict[str, Any] = jsonref.replace_refs(
            self.schema, lazy_load=False
        )  # type: ignore
        self.schema = deref_schema

    @staticmethod
    def from_schema_path(schema_path: Path) -> "IdsArtifact":
        """Create validator parameters given the path to schema.json"""

        ids_folder_path = schema_path.parent
        athena_path = ids_folder_path.joinpath("athena.json")
        elasticsearch_path = ids_folder_path.joinpath("elasticsearch.json")
        expected_path = ids_folder_path.joinpath("expected.json")

        missing_files = tuple(
            file.name
            for file in (schema_path, athena_path, elasticsearch_path, expected_path)
            if not file.exists()
        )
        if missing_files:
            raise FileNotFoundError(
                "The following artifact files must exist but were not found: "
                f"{missing_files}. Check the previous artifact."
            )
        schema = json.loads(schema_path.read_text())
        athena = json.loads(athena_path.read_text())
        elasticsearch = json.loads(elasticsearch_path.read_text())
        expected = json.loads(expected_path.read_text())

        return IdsArtifact(
            schema=schema,
            athena=athena,
            elasticsearch=elasticsearch,
            expected=expected,
            path=ids_folder_path,
        )

    @staticmethod
    def from_ids_folder(ids_path: Path) -> "IdsArtifact":
        """Create validator parameters given the path to schema.json"""
        return IdsArtifact.from_schema_path(ids_path.joinpath("schema.json"))

    def get_identity(self) -> IdsIdentity:
        """Populate the IDS identity from the schema."""
        return get_ids_identity(self.schema)

    @property
    def identity(self) -> IdsIdentity:
        """IDS identity (namespace/slug/version) according to the schema."""
        return get_ids_identity(self.schema)

    def get_convention_type(self) -> Conventions:
        """Identify and return the validation convention version from schema.json

        An unrecognized `@idsConventionVersion` const value will raise an error.

        Returns:
            `Conventions` Enum value
        """
        convention = pydash.get(
            self.schema, "properties.@idsConventionVersion.const", None
        )
        if convention is None:
            return Conventions.GENERIC

        convention_enum_value = Conventions.get_by_value(convention)

        if convention_enum_value is None:
            raise ValueError(
                "In schema.json, the property `@idsConventionVersion` is defined but "
                "does not have the supported 'const' value of 'v1.0.0'. "
                f"The validator cannot run with the specified value: {convention}"
            )

        return convention_enum_value


@dataclass
class ValidatorParameters:
    """Class for keeping all parameters that could/would be used by validator"""

    artifact: IdsArtifact = field(default_factory=IdsArtifact)
    previous_artifact: Optional[IdsArtifact] = None
    convention_version: Conventions = Conventions.GENERIC

    def __post_init__(self):
        """Get the validator convention by checking for `@idsConventionVersion`."""
        self.convention_version = self.artifact.get_convention_type()

    @staticmethod
    def from_comparative_schema_paths(
        schema_path: Path, previous_schema_path: Path
    ) -> "ValidatorParameters":
        return ValidatorParameters(
            artifact=IdsArtifact.from_schema_path(schema_path),
            previous_artifact=IdsArtifact.from_schema_path(previous_schema_path),
        )

    def root_node(self) -> Node:
        return Node(schema=self.artifact.schema)
