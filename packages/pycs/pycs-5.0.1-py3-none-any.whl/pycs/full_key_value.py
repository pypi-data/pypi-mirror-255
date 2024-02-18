from __future__ import annotations


class FullKeyValue:
    def __init__(self):
        self._parent: FullKeyParent = None
        self._key: str = None

    @property
    def full_key(self):
        key = ""
        if self.parent is not None and self.parent.full_key:
            key += self.parent.full_key + "."
        key += self.key or self._default_key
        return key

    @property
    def _default_key(self) -> str:
        """Key to use when None was provided"""
        return ""

    @property
    def parent(self) -> FullKeyValue:
        return self._parent

    @parent.setter
    def parent(self, value: FullKeyParent) -> None:
        if self._parent:
            raise AttributeError(f"Parent for {self} at {self.full_key} has already been set to {self._parent}")
        self._parent = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str) -> None:
        if self._key:
            raise AttributeError(f"Key for {self} at {self.full_key} has already been set to {self._parent}")
        self._key = value

    def _child_full_key(self, child_key: str) -> str:
        return f"{self.full_key}.{child_key}"


class FullKeyParent(FullKeyValue):
    pass
