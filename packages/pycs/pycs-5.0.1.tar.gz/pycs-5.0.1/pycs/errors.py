from __future__ import annotations


class ConfigError(Exception):
    pass


class ConfigUseError(ConfigError, ValueError):
    pass


class TypeMismatchError(ConfigError):
    """Wrong type is used"""


class NodeReassignmentError(ConfigError):
    """Assigning value to node item"""


class ModuleError(ConfigError):
    """Incorrectly specified config, can't import"""


class SchemaError(ConfigError):
    """Incorrectly specified schema"""


class SchemaFrozenError(SchemaError):
    """Trying to add new items after schema has been frozen"""


class SpecError(ConfigError):
    """Value which is assigned does not match leaf_spec"""


class SaveError(ConfigError):
    """Can't save"""


class ValidationError(ConfigError):
    """Config restrictions are not respected"""


class MissingRequiredError(ValidationError):
    pass
