class InvalidSchemaDefinition(Exception):
    """Error to raise when an unexpected schema object definition is found"""


class MergeException(Exception):
    """Needed to catch particular merge Exception."""


class UnknownFieldType(Exception):
    """Needed to catch particular merge Exception."""
