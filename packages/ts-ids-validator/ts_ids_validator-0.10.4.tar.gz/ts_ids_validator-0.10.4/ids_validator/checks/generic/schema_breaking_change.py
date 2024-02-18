from typing import Iterable, List

import deepdiff
import pydash
from deepdiff.operator import BaseOperator
from semver import Version

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.checks.constants import ROOT_PROPERTIES
from ids_validator.helpers.athena.constants import get_primitive_types
from ids_validator.ids_node import Node, NodePath
from ids_validator.utils import IdsIdentity, check_if_major_version_is_same

INCLUDED_SCHEMA_METADATA_KEYS = ["type", "const", "required"]


def check_version_bump_is_valid(previous: Version, current: Version) -> CheckResults:
    """Check that the previous and current versions are a valid version bump."""
    # Note previous == current is allowed for documentation-only releases.
    if (
        previous == current
        or previous.bump_major() == current
        or previous.bump_minor() == current
        or previous.bump_patch() == current
    ):
        return []

    return [
        CheckResult.critical(
            f"The current version number ({current}) is not valid compared to the previous version ({previous}). "
            "It must be a single major/minor/patch bump, or no bump for a documentation-only change."
        )
    ]


def all_types_are_primitive(property_types: Iterable) -> bool:
    """Check if all elements in the list is present in the list of primitives"""
    for property_type in property_types:
        if property_type not in get_primitive_types():
            return False
    return True


def as_list(obj: object) -> list:
    """Convert obj to list if it not a list, from primitive it would create a list with one element

    Args:
        obj: object to convert
    """
    return obj if isinstance(obj, List) else [obj]


class TypeValueComparator(BaseOperator):
    """DeepDiff operator class implementing special logic in comparing 'type' field"""

    def give_up_diffing(self, level, diff_instance) -> bool:
        """Validate if type field change is OK.

        Args:
            level:
            diff_instance:

        Returns:
            True - no further validation by DeepDiff is needed because there are no
                breaking changes
            False - let DeepDiff continue taking the diff of this level
        """
        # We need to work with names from deepDiff that means the following:
        # level.t1 - previous
        # level.t2 - new
        if isinstance(level.t1, List) or isinstance(level.t2, List):
            previous_types = set(as_list(level.t1))
            new_types = set(as_list(level.t2))

            # The new set may include an extra "null", don't count it in the difference
            difference = new_types - previous_types - set(["null"])
            if (
                all_types_are_primitive(previous_types)
                and all_types_are_primitive(new_types)
                and not difference
                and previous_types.issubset(new_types)
            ):
                # No breaking change - stop diffing
                return True
        return False


class RequiredValueComparator(BaseOperator):
    """DeepDiff operator class implementing special logic in comparing 'required' field"""

    def give_up_diffing(self, level, diff_instance) -> bool:
        """Validate if "Required" changes are allowed.

        Required fields may be reduced from one schema to the next without a breaking
        change.

        At this point in the validator, "required" is already validated to be a list of
        properties

        Returns:
            True - no further validation by DeepDiff needed
            False - need validation by DeepDiff
        """
        # We need to work with names from deepDiff that means the following:
        # level.t1 - previous
        # level.t2 - new
        previous_required = set(level.t1)

        new_required = set(level.t2)

        if new_required.issubset(previous_required):
            # 'required' is the same or has had properties removed: no breaking change
            return True

        return False


def compare_nodes(node: Node, previous_node_schema: dict) -> dict:
    """Compare the same IDS schema node from the previous and current IDS versions

    Returns a dict of differences, excluding differences which are allowed, such as
    removing properties from the "required" schema metadata.
    """

    # we are validating only properties section of schema that is located in root.properties
    if not node.path.has_prefix(ROOT_PROPERTIES):
        return {}

    if node.path == NodePath(("root", "properties", "@idsVersion")):
        return {}

    if node.path.in_properties:
        # we are tracking changes for all keys in 'properties' section
        return deepdiff.DeepDiff(
            previous_node_schema.keys(),
            node.data.keys(),
            ignore_order=True,
        ).to_dict()

    if "required" not in previous_node_schema:
        if "required" in node.data:
            previous_node_schema["required"] = []
    if "required" not in node.data:
        if "required" in previous_node_schema:
            node.data["required"] = []

    # if not properties section we are tracking only few from INCLUDED_SCHEMA_METADATA_KEYS
    return deepdiff.DeepDiff(
        previous_node_schema,
        node.data,
        ignore_order=True,
        include_paths=INCLUDED_SCHEMA_METADATA_KEYS,
        custom_operators=[
            TypeValueComparator(["^root\\['type'\\]$"]),
            RequiredValueComparator(["^root\\['required'\\]$"]),
        ],
    ).to_dict()


def format_failures(
    failures: List[CheckResult], previous_ids: IdsIdentity, current_ids: IdsIdentity
) -> CheckResult:
    """
    Format the resulting CheckResult instances produced by SchemaBreakingChangeChecker.run()
    into a single CheckResult instance for user readability.

    Args:
        failures: List of CheckResult instances produce by SchemaBreakingChangeChecker.run()
        previous_ids: Previous IDS IdsIdentity instance
        current_ids: Current IDS IdsIdentity instance

    Returns:
        Single CheckResult instance containing a single header with all failures included
    """
    failure_header = (
        f"The change(s) between the previous ({previous_ids.version}) and current ({current_ids.version}) IDSs violate "
        "IDS versioning requirements which enable Athena and other parts of TDP to function as intended.\n"
    )
    path_failures = "\n\n".join([failure.message for failure in failures])

    return CheckResult.critical(f"{failure_header}\n{path_failures}")


class SchemaBreakingChangeChecker(AbstractChecker):
    """Checks if there is no breaking changes introduced.
    Breaking changes:
    - add/remove field in properties section
    - change field type excluding adding 'null'
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if context.previous_artifact is None:
            # Can't check for breaking changes when there is no previous schema
            return logs

        previous_schema = context.previous_artifact.schema
        if node.path.parts == ("root",):
            logs += check_version_bump_is_valid(
                context.previous_artifact.identity.version_parts,
                context.artifact.identity.version_parts,
            )
        if not check_if_major_version_is_same(previous_schema, context.artifact.schema):
            return logs

        # Use a unique default value so that `None` is treated as a valid return value
        missing_value = object()
        previous_node_schema = pydash.get(
            obj=previous_schema,
            path=str(node.path).replace("root.", "", 1),
            default=missing_value,
        )
        if previous_node_schema is missing_value:
            # We would get here if we have key in new schema that is not exist in previous schema.
            # That would be identified with deepdiff on previous step of recursion, so we do not need to report it here.
            return logs

        current_vs_previous = compare_nodes(
            node=node, previous_node_schema=previous_node_schema
        )

        if current_vs_previous:
            logs += [
                CheckResult.critical(
                    f"\t'{node.path}' change requires a major version bump: \n\t\t{current_vs_previous}.".replace(
                        "root[", f"{node.path}["
                    )
                )
            ]
            return logs

        return logs
