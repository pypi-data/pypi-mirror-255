from typing import ClassVar, List

from ids_validator.checks.rules_checker import RuleBasedChecker
from ids_validator.checks.v1.rules.related_files import RULES as RELATED_FILES_RULES
from ids_validator.checks.v1.rules.samples import samples_rules
from ids_validator.checks.v1.rules.samples.samples_root import SAMPLES
from ids_validator.checks.v1.rules.systems import systems_rules
from ids_validator.checks.v1.rules.users import USERS, users_rules


class V1SystemNodeChecker(RuleBasedChecker):
    rules = systems_rules


class EnforcedNodeChecker(RuleBasedChecker):
    """
    Inherit from this class and set the class variables when you want to enforce
    that a schema contains a given set of nodes when @idsConventionVersion == v1.0.0.

    NOTE: Ensure that you add the subclass of this to ENFORCED_NODE_CHECKS in this module
    """

    # If specific nodes must exist in the schema provide a list of the nodes as
    # the string paths (e.g root.properties.foo) when subclassing RuleBasedChecker
    enforced_nodes: ClassVar[List[str]] = None
    reserved_root: str = None


class V1SampleNodeChecker(EnforcedNodeChecker):
    """The schema must contain the exact definition as samples defined here"""

    rules = samples_rules
    enforced_nodes = list(samples_rules)
    reserved_root = SAMPLES


class V1UserNodeChecker(EnforcedNodeChecker):
    """The schema definition must contain at least the defined nodes in users"""

    rules = users_rules
    enforced_nodes = list(users_rules)
    reserved_root = USERS


class V1RelatedFilesChecker(RuleBasedChecker):
    """
    Check that the related files schema matches the template from the schema conventions
    """

    rules = RELATED_FILES_RULES


ENFORCED_NODE_CHECKS = [V1SampleNodeChecker, V1UserNodeChecker]
