from typing import Any

class Registry():
    _values: dict[str, Any] = {}

    @classmethod
    def register(cls, key: str, value: Any):
        cls._values[key] = value

    @classmethod
    def registered(cls, key: str, default: Any = None):
        return cls._values.get(key, default)
