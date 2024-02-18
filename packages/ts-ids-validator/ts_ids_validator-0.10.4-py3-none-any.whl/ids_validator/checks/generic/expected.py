import jsonschema

from ids_validator.checks.abstract_checker import (
    AbstractChecker,
    CheckResult,
    CheckResults,
)
from ids_validator.ids_node import Node, NodePath
from ids_validator.models.validator_parameters import ValidatorParameters


class ExpectedChecker(AbstractChecker):
    """
    expected.json must be valid against schema.json when validated with a JSON Schema
    validator.
    """

    @classmethod
    def run(cls, node: Node, context: ValidatorParameters) -> CheckResults:

        if node.path != NodePath(("root",)):
            # This check will only run for the root node of the schema.
            return []

        validator = jsonschema.Draft7Validator(context.artifact.schema)
        try:
            validator.validate(context.artifact.expected)
        except jsonschema.ValidationError as exception:
            return [
                CheckResult.critical(
                    "expected.json is not valid against schema.json. "
                    f"JSON Schema validation failed:\n{exception}"
                )
            ]

        return []
