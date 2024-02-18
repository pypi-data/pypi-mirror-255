from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
    ValidatorParameters,
)
from ids_validator.ids_node import Node


class V1ChildNameChecker(AbstractChecker):
    """Checks if child name starts with parent's name"""

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:
        logs: CheckResults = []
        properties = node.properties_list or []
        child_start_with_parent_name = [
            prop.lower().startswith(node.name.lower()) for prop in properties
        ]
        if any(child_start_with_parent_name):
            logs += [
                CheckResult.warning(
                    f"Child property prefix uses the same name as the parent property "
                    f"'{node.name}'"
                )
            ]
        return logs
