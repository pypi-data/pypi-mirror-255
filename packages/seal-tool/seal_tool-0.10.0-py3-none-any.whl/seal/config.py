import pyhocon as ph

from pathlib import Path
from typing import Any, Self, SupportsInt, SupportsFloat


class InvalidTaskError(Exception):
    """Exception raised for errors in the taskfile.

    Attributes:
        val -- invalid value
    """

    def __init__(self, val: str):
        super().__init__(f'Invalid value found in taskfile: {val}')


class Config:
    """
    Wraps used config library, pyhocon, mostly to ensure returned values are not None
    to make handling edge cases and typing easier
    """

    def __init__(self, cfg_tree: ph.ConfigTree) -> None:
        self._cfg = cfg_tree

    def get(self, key: str) -> str | int | bool | float | list | dict | ph.ConfigTree:
        return self._cfg.get(key)

    @classmethod
    def from_file(cls, cfg_path: Path) -> Self:
        cfg = ph.ConfigFactory.parse_file(cfg_path)
        if not isinstance(cfg, ph.ConfigTree):
            raise InvalidTaskError('top-level object is an unexpected type')
        return cls(cfg)

    @classmethod
    def from_string(cls, cfg: str) -> Self:
        cfg = ph.ConfigFactory.parse_string(cfg)
        if not isinstance(cfg, ph.ConfigTree):
            raise InvalidTaskError('top-level object is an unexpected type')
        return cls(cfg)

    def get_string(self, key: str, default: Any = ph.UndefinedKey) -> str:
        val = self._cfg.get_string(key, default)
        if val is None:
            raise InvalidTaskError(f'{key} is null')
        return val

    def get_subconf(self, key: str) -> Self:
        val = self._cfg.get_config(key)
        if not isinstance(val, ph.ConfigTree):
            raise InvalidTaskError(f'{key} is a {type(val)}')
        return self.__class__(val)

    def get_int(self, key: str) -> int:
        val = self._cfg.get_int(key)
        if val is None:
            raise InvalidTaskError(f'{key} is null')
        return val

    def get_int_unchecked(
        self, key: str, default: SupportsInt | None | type[ph.UndefinedKey] = ph.UndefinedKey
    ) -> int | None:
        return self._cfg.get_int(key, default)

    def get_float(self, key: str) -> float:
        val = self._cfg.get_float(key)
        if val is None:
            raise InvalidTaskError(f'{key} is null')
        return val

    def get_float_unchecked(
        self, key: str, default: SupportsFloat | None | type[ph.UndefinedKey] = ph.UndefinedKey
    ) -> float | None:
        return self._cfg.get_float(key, default)

    def get_bool(self, key: str, default: Any = ph.UndefinedKey) -> bool:
        val = self._cfg.get_bool(key, default)
        if val is None:
            raise InvalidTaskError(f'{key} is null')
        return val

    def put(self, key: str, value: Any) -> None:
        self._cfg.put(key, value)

    def get_list(
        self, key: str, default: list[str] | type[ph.UndefinedKey] = ph.UndefinedKey
    ) -> list[str | bool | int | float | list | Self]:
        vals = self._cfg.get_list(key, default)
        if vals is None:
            raise InvalidTaskError(f'{key} is null')
        vals = [self.__class__(val) if isinstance(val, ph.ConfigTree) else val for val in vals]
        return vals
