from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node, NodePath


class V1ConventionVersionChecker(AbstractChecker):
    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        if node.path == NodePath(("root", "properties", "@idsConventionVersion")):
            convention_version = context.convention_version
            if node.get("const") != convention_version.value:
                logs.append(
                    CheckResult.critical(
                        f"'@idsConventionVersion must be '{convention_version}'"
                    )
                )
        return logs
