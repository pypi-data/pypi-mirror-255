from pydash import get

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node, NodePath

CONVENTION_VERSION_PATH = "properties.@idsConventionVersion"


class V1RootNodeChecker(AbstractChecker):
    """
    Root node checker for V1.0.0 convention, checks only
    for the presence and correctness of `@idsConventionVersion`.
    It must be used in conjunction with generic RootNodeCheck.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if node.path == NodePath(("roots",)):
            convention_version = get(node, CONVENTION_VERSION_PATH)
            checks = [
                get(convention_version, "type") == "string",
                get(convention_version, "const"),
            ]
            if not convention_version or not all(checks):
                logs.append(
                    CheckResult.critical(
                        f"'{CONVENTION_VERSION_PATH}' must be of type 'string' with "
                        f"non-empty 'const'"
                    )
                )

        return logs
