from __future__ import annotations

import inspect
import logging
import warnings
from collections import UserDict
from copy import copy
from itertools import chain
from pathlib import Path, PosixPath
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Union

import yaml

from pycs.errors import (
    ConfigError,
    ConfigUseError,
    MissingRequiredError,
    NodeReassignmentError,
    SaveError,
    SchemaError,
    SchemaFrozenError,
    ValidationError,
)
from pycs.full_key_value import FullKeyParent
from pycs.interfaces import CfgSavable
from pycs.utils import add_yaml_str_representer, import_module, merge_cfg_module

from .leaf import CfgLeaf

LOGGER = logging.getLogger(__name__)


def _cfg_path_to_name(cfg_path: Path, root_name="configs"):
    """
    >>> _cfg_path_to_name(Path("some/deep/name.py"))
    'name'
    >>> _cfg_path_to_name(Path("some/configs/deep/name.py"))
    'deep/name'
    >>> _cfg_path_to_name(Path("some/test/abc/bcd.py"), 'test')
    'abc/bcd'
    """
    try:
        path_config_idx = cfg_path.parts.index(root_name)
    except ValueError:  # '... not in tuple'
        return cfg_path.stem
    rel_parts = cfg_path.parts[path_config_idx + 1 :]
    return str(Path(*rel_parts).with_suffix(""))


class CfgNode(UserDict, FullKeyParent):
    _BUILT_IN_ATTRS = (
        # FullKeyValue
        "_parent",
        "_key",
        "parent",
        "key",
        # CfgNode
        "_desc",
        "_root_name",
        "_schema_frozen",
        "_new_allowed",
        "_leaf_spec",
        "_validators",
        "_transforms",
        "_hooks",
        "_module",
        "_safe_save",
    )
    RESERVED_KEYS = (*_BUILT_IN_ATTRS, "data")

    def __init__(self, first: Any = None, *, schema_frozen=False, new_allowed=False, desc: str = None):
        super().__init__()
        # Have to repeat it here for correct interaction with __getattr__
        self._parent: CfgNode | None = None
        self._key: str | None = None

        if isinstance(first, dict):
            base, leaf_spec = first, None
        else:
            base, leaf_spec = None, first
        if leaf_spec is not None and not isinstance(leaf_spec, CfgLeaf):
            leaf_spec = CfgLeaf(None, leaf_spec)

        self._desc = desc
        self._root_name = "configs"

        self._schema_frozen = schema_frozen
        self._new_allowed = new_allowed
        self._leaf_spec = leaf_spec
        self._validators = []
        self._transforms = []
        self._hooks = []

        self._module: list[str] | None = None
        self._safe_save = True

        if self._leaf_spec is not None:
            self._new_allowed = True

        if base is not None:
            self._init_with_base(base)

    @property
    def schema_frozen(self) -> bool:
        return self._schema_frozen

    @property
    def new_allowed(self) -> bool:
        return self._new_allowed

    @property
    def leaf_spec(self) -> CfgLeaf | None:
        return self._leaf_spec

    @property
    def _default_key(self):
        return "cfg"

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            self._set_existing(key, value)
        else:
            self._set_new(key, value)

    def get_raw(self, key):
        if key not in self:
            raise KeyError(key)
        return super().__getitem__(key)

    def __getitem__(self, key: str) -> Any:
        attr = self.get_raw(key)
        if isinstance(attr, CfgLeaf):
            return attr.value
        return attr

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self.RESERVED_KEYS:
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __eq__(self, other: CfgNode) -> bool:
        return self.to_dict() == other.to_dict()

    def __str__(self) -> str:
        add_yaml_str_representer()
        attrs = self.to_dict()
        return yaml.dump(attrs)

    def propagate_changes(self) -> None:
        self.transform()
        self.validate()
        self.run_hooks()

    @staticmethod
    def load(cfg_path: Union[Path, str]) -> CfgNode:
        cfg_path = Path(cfg_path)
        module = import_module(cfg_path)
        cfg: CfgNode = module.cfg
        cfg._module = merge_cfg_module(module)  # noqa: SLF001 Same class

        if not cfg.schema_frozen:
            raise SchemaError(
                "Found cfg with unfrozen schema, please initialise config from schema: cfg = schema.init_cfg()",
            )
        if hasattr(cfg, "NAME"):
            cfg.NAME = cfg.NAME or _cfg_path_to_name(cfg_path, cfg._root_name)  # noqa: SLF001 Same class

        cfg.propagate_changes()
        return cfg

    @staticmethod
    def validate_required(cfg: CfgNode) -> None:
        if cfg.leaf_spec is not None and cfg.leaf_spec.required and len(cfg) == 0:
            raise MissingRequiredError(f"Missing required members for {cfg.leaf_spec} at key {cfg.full_key}")
        for _, attr in cfg.attrs:
            if isinstance(attr, CfgLeaf) and attr.required and attr.value is None:
                raise MissingRequiredError(f"Key {attr} is required, but was not provided.")

    def save(self, path: Union[Path, str]) -> None:
        path = Path(path)
        if not self._safe_save:
            raise SaveError("Config was updated in such a way that it can no longer be saved!")
        if not self._module:
            raise SaveError("Config was not loaded.")
        with path.open("w") as f:
            f.writelines(self._module)

    def clone(self) -> CfgNode:
        cfg = CfgNode()
        attrs_to_ignore = {"_parent", "_key", "parent", "key", "_schema_frozen"}

        for name in [attr for attr in self._BUILT_IN_ATTRS if attr not in attrs_to_ignore]:
            setattr(cfg, name, copy(getattr(self, name)))

        for key, value in self.attrs:
            if isinstance(value, (CfgNode, CfgLeaf)):
                value = value.clone()
            setattr(cfg, key, value)
        if self.schema_frozen:
            cfg.freeze_schema()
        return cfg

    def inherit(self) -> CfgNode:
        cfg = self.clone()
        cfg.unfreeze_schema()
        return cfg

    def transform(self) -> None:
        """
        Specify additional changes to be made after manual changes, run during loading from file
        Will be applied recursively on all nested nodes first
        """
        if not self._schema_frozen:
            warnings.warn(
                "Transforming without freezing schema is discouraged, as it frequently leads to bugs",
                stacklevel=2,
            )
        for _, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.transform()
        for transformer in self._transforms:
            transformer(self)

    def validate(self) -> None:
        """
        Check additional rules for config, run during loading after transform
        Will be applied recursively on all nested nodes first
        """
        for _, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.validate()
        validators = [CfgNode.validate_required] + self._validators
        try:
            for validator in validators:
                validator(self)
        except AssertionError as exc:
            raise ValidationError from exc

    def run_hooks(self) -> None:
        """
        Perform actions based on config, run during loading after validation
        Hooks should NOT modify the config
        Will be applied recursively on all nested nodes first
        """
        for _, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.run_hooks()
        for hook in self._hooks:
            hook(self)

    def add_transform(self, transform: Callable[[CfgNode], None]) -> None:
        if self._schema_frozen:
            raise SchemaFrozenError("Can't add transform after schema has been frozen")
        self._transforms.append(transform)

    def add_validator(self, validator: Callable[[CfgNode], None]) -> None:
        if self._schema_frozen:
            raise SchemaFrozenError("Can't add validator after schema has been frozen")
        self._validators.append(validator)

    def add_hook(self, hook: Callable[[CfgNode], None]) -> None:
        if self._schema_frozen:
            raise SchemaFrozenError("Can't add hook after schema has been frozen")
        self._hooks.append(hook)

    def to_dict(self) -> dict[str, Any]:
        attrs = {}
        for key, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attrs[key] = attr.to_dict()
            else:
                attrs[key] = attr.value
        return attrs

    @property
    def attrs(self) -> list[tuple[str, Union[CfgNode, CfgLeaf]]]:
        attrs_list = []
        for key in super().keys():  # noqa: SIM118 Doesn't work on super()
            value = self.get_raw(key)
            if isinstance(value, (CfgNode, CfgLeaf)):
                attrs_list.append((key, value))
        return attrs_list

    def freeze_schema(self) -> None:
        self._schema_frozen = True
        for _, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.freeze_schema()

    def unfreeze_schema(self) -> None:
        self._schema_frozen = False
        for _, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.unfreeze_schema()

    def describe(self, key: str = None) -> str | None:
        if key is None:
            return self._desc
        if key not in self:
            raise ConfigUseError(f"{key!r} key does not exist")

        attr = super().__getitem__(key)
        if isinstance(attr, CfgNode):
            return attr.describe()
        if isinstance(attr, CfgLeaf):
            return attr.desc
        raise TypeError("This should not happen!")

    def _set_attrs(self, attrs: list[tuple[str, Union[CfgNode, CfgLeaf]]]) -> None:
        for key, attr in attrs:
            setattr(self, key, attr.clone())

    def _set_new(self, key: str, value: Any) -> None:
        if self._schema_frozen and not self._new_allowed:
            raise SchemaFrozenError(f"Trying to add leaf '{key}' to node '{self.full_key}' with frozen schema.")

        value_to_set: Union[CfgNode, CfgLeaf]
        if isinstance(value, CfgNode):
            value_key = self._child_full_key(key)
            _check_circular_path(value, value_key, [id(self)])
            value_to_set = self._value_to_set_from_node(value, value_key)
        elif isinstance(value, CfgLeaf):
            value_to_set = value
        elif isinstance(value, type):
            value_to_set = self._value_to_set_from_type(value)
        else:
            value_to_set = self._value_to_set_from_value(value, key)
        self._set_key_for_child(value_to_set, key)

        if isinstance(value_to_set, CfgLeaf) and self.leaf_spec:
            value_to_set.check(self.leaf_spec)
            if value_to_set.desc is None:
                value_to_set.desc = self.leaf_spec.desc

        super().__setitem__(key, value_to_set)

    def _set_existing(self, key: str, value: Any) -> None:
        cur_attr = super().__getitem__(key)
        if isinstance(cur_attr, CfgNode):
            if cur_attr:
                raise NodeReassignmentError(f"Non-empty CfgNode {self._child_full_key(key)} cannot be reassigned")
            if not isinstance(cur_attr, CfgNode):
                raise NodeReassignmentError(f"Can only swap CfgNode {self._child_full_key(key)} for another CfgNode")
            object.__setattr__(value, "_desc", cur_attr.describe())
            if self.schema_frozen:
                value.freeze_schema()
            super().__setitem__(key, value)
        elif isinstance(cur_attr, CfgLeaf):
            cur_attr.value = value
        else:
            raise TypeError("This should not happen!")

    def _init_with_base(self, base: dict) -> None:
        for key, value in base.items():
            if isinstance(value, dict):
                value = CfgNode(value)
            self[key] = value

    def __reduce__(self):
        if not self.schema_frozen:
            raise ConfigUseError(f"Can't pickle unfrozen CfgNode: {self.full_key}")
        state = {}
        for attr_name in self._BUILT_IN_ATTRS:
            state[attr_name] = getattr(self, attr_name)
        return self.__class__, (self.to_dict(),), state

    def _value_to_set_from_node(self, node: CfgNode, full_key: str) -> CfgNode:
        if self.leaf_spec:
            raise SchemaError(f"Key {full_key} cannot contain nested nodes as leaf spec is defined for it.")
        return node

    def _value_to_set_from_type(self, type_: type) -> CfgLeaf:
        if self.leaf_spec:
            required, desc = self.leaf_spec.required, self.leaf_spec.desc
        else:
            required, desc = True, None
        return CfgLeaf(
            type_,
            type_,  # Need to pass value here instead of copying from spec, in case new value is more restrictive
            subclass=True,
            required=required,
            desc=desc,
        )

    def _value_to_set_from_value(self, value: Any, key: str) -> CfgLeaf:
        if self.leaf_spec:
            leaf = self.leaf_spec.clone()
            try:
                leaf.value = value
            except ConfigError:
                # Set key and parent to get proper error message
                self._set_key_for_child(leaf, key)
                leaf.value = value
            return leaf
        return CfgLeaf(value, type(value), required=True)

    def clear(self) -> None:
        if self._schema_frozen and not self._new_allowed:
            raise AttributeError(
                f"Can only clear CfgNode when _new_allowed == True if schema is frozen: {self.full_key}",
            )
        for key in list(self.keys()):
            del self[key]

    def update(self, mapping: MutableMapping[str, Any] | Iterable[tuple[str, Any]] = None, **new_kwargs_dict) -> None:
        if not (mapping or new_kwargs_dict):
            return
        mapping = mapping or {}
        iter_mapping = mapping.items() if isinstance(mapping, Mapping) else mapping
        iterator = chain(iter_mapping, new_kwargs_dict.items())

        for key, value in iterator:
            if key in self and isinstance(self[key], Mapping):  # type: ignore
                self[key].update(value)  # type: ignore
            else:
                self[key] = value  # type: ignore

    def _update_module(self, key: str, value) -> None:
        if self._parent is not None:
            self._parent._update_module(f"{self.key}.{key}", value)  # noqa: SLF001 Same class
        if self._module is None:  # Before config is loaded
            return
        key = f"{self._default_key}.{key}"

        reference_comment = "# <Source not found>"
        for info in inspect.stack()[1:]:
            # Kind of a hack, need to keep track of all our files
            if "/".join(info.filename.rsplit("/")[-2:]) in ["cfg/node.py", "cfg/leaf.py"]:
                continue
            reference_comment = f"# {info.filename}:{info.lineno} {info.code_context[0]}"  # type: ignore
            break

        lines = [reference_comment]
        valid_types = [bool, int, float, str]
        if isinstance(value, type):
            module = inspect.getmodule(value)
            lines.append(f"from {module.__name__} import {value.__name__}\n")
            lines.append(f"{key} = {value.__name__}\n")
        elif type(value) in valid_types:
            lines.append(f"{key} = {value!r}\n")
        elif type(value) == PosixPath:
            lines.append("from pathlib import PosixPath\n")
            lines.append(f"{key} = {value!r}\n")
        elif isinstance(value, CfgSavable):
            import_str, cls_name, args, kwargs = value.save_strs()
            lines.append(f"{import_str}\n")
            lines.append(f"{key} = {value.create_eval_str(cls_name, args, kwargs)}\n")
        elif isinstance(value, list) and all(type(v) in valid_types for v in value):
            lines.append(f"{key} = {value!r}\n")
        else:
            message = f"Config was modified with unsavable value: {value!r}"
            LOGGER.warning(message)
            lines.append(f"# {message}")
            self._safe_save = False
        self._module.extend(lines)

    def set_root_name(self, name: str) -> None:
        self._root_name = name

    def _set_key_for_child(self, child: Union[CfgNode, CfgLeaf], key: str) -> None:
        child.key = key
        child.parent = self

    def init_cfg(self) -> CfgNode:
        """Initialise config from schema"""
        cfg = self.clone()
        cfg.freeze_schema()
        return cfg

    def static_init(self) -> CfgNode:
        """Default initialisation when config is used as is, instead of using load()"""
        cfg = self.init_cfg()
        cfg.propagate_changes()
        return cfg

    def load_or_static(self, path: Union[Path, str] = None) -> CfgNode:
        return self.load(path) if path else self.static_init()


def _check_circular_path(new_node: CfgNode, key: str, parent_ids: list[int] = None):
    parent_ids = parent_ids or []
    new_id = id(new_node)
    if any(new_id == parent_id for parent_id in parent_ids):
        raise ValueError(f"Tried to set circular cfg for {key}")
    for key, value in new_node.items():
        if isinstance(value, CfgNode):
            _check_circular_path(value, key, [new_id, *parent_ids])


CN = CfgNode

__all__ = ["CfgNode", "CN"]
