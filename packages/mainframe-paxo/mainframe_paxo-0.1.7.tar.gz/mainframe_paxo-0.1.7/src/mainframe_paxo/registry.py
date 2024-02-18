from __future__ import annotations

import ntpath
import winreg
from typing import Any, Iterator, Optional, Tuple, Union

"""helper classes for registry operations"""

# map the winreg root key constants to their names
root_keys: dict[int, str] = {}
for key, val in winreg.__dict__.items():
    if key.startswith("HKEY_"):
        root_keys[val] = key
        globals()[key] = val


class Key:
    """A key in the registry.  This is a wrapper around the winreg module."""

    def __init__(
        self,
        parent: Union[Key, int],
        name: str,
        **kwargs,
    ) -> None:
        """Create a new key object.  The key is not opened or created."""
        self._parent = parent
        self.name: str = name
        self._handle: Optional[Any] = None
        self._kwargs = kwargs  # passed to an implicit open() in context manager
        if isinstance(parent, Key):
            self._fullname = ntpath.join("Computer", parent._fullname, name)
        else:
            self._fullname = ntpath.join(root_keys[parent], name)

    def __repr__(self) -> str:
        """Returns a string representation of the key"""
        return f"Key<{self._fullname!r}>"

    def _get_basename(self) -> Tuple[Any, str]:
        """Returns a suitable key handle and base string for this key"""
        if self._handle is not None:
            return self._handle, ""
        if isinstance(self._parent, Key):
            parent_handle, parent_name = self._parent._get_basename()
            return parent_handle, ntpath.join(parent_name, self.name)
        # parent is a raw handle
        return self._parent, self.name

    def open(
        self,
        *subkeys: str,
        create: bool = False,
        write: Optional[bool] = None,
        check: bool = True,
    ) -> Optional[Key]:
        """Opens an existing key"""
        if subkeys:
            return self.subkey(*subkeys).open(create=create, write=write, check=check)
        assert self._handle is None
        handle, name = self._get_basename()
        try:
            # create defaults for true if create is true, false otherwise
            write = write if write is not None else create
            access = winreg.KEY_WRITE if write else winreg.KEY_READ
            func = winreg.CreateKeyEx if create else winreg.OpenKeyEx
            self._handle = func(handle, name, access=access)
        except FileNotFoundError as e:
            if check:
                raise ValueError(f"Key {self.name!r} not found") from e
            return None
        return self

    def subkey(self, *subkeys: str, **kwargs) -> Key:
        """Returns a subkey object"""
        subkey_name = ntpath.join(*subkeys)
        return Key(self, subkey_name, **kwargs)

    def __getattr__(self, name: str) -> Key:
        """Returns a subkey object"""
        return self.subkey(name)

    def __call__(self, *subkeys: str, **kwargs) -> Key:
        """Returns a subkey object"""
        return self.subkey(*subkeys, **kwargs)

    def exists(self) -> bool:
        """checks if the key exists"""
        if self.opened():
            return True
        if self.open(check=False) is None:
            return False
        self.close()
        return True

    def __bool__(self) -> bool:
        """checks if the key exists"""
        return self.exists()

    def opened(self) -> bool:
        """Checks if the key is opened"""
        return self._handle is not None

    def create(self, *args, **kwargs) -> Key:
        """alias for open(... create=True)"""
        kwargs["create"] = True
        return self.open(*args, **kwargs)

    def close(self) -> None:
        """Closes the key."""
        if self._handle is not None:
            handle, self._handle = self._handle, None
            winreg.CloseKey(handle)

    # iterating over the key/value pairs (items) in the key, similar to a dict.

    def items(self) -> Iterator[tuple[str, tuple[Any, int]]]:
        """Iterates over the values in the key"""
        for i in range(1000):
            try:
                name, value, type = winreg.EnumValue(self._handle, i)
                yield (name, (value, type))
            except OSError:
                break

    def keys(self) -> Iterator[str]:
        """iterates of the item names in the key"""
        for itemname, _ in self.items():
            yield itemname

    def values(self) -> Iterator[tuple[Any, int]]:
        """iterates of the item values in the key"""
        for _, value in self.items():
            yield value

    def stringitems(self) -> Iterator[tuple[str, str]]:
        """Iterates over the string items in the key"""
        for k, (v, t) in self.items():
            if t == winreg.REG_SZ:
                yield (k, v)

    def subkeys(self) -> Iterator[Key]:
        """Iterates over the subkeys in the key"""
        for i in range(1000):
            try:
                name = winreg.EnumKey(self._handle, i)
                yield Key(self, name)
            except OSError:
                break

    def get_value(self, name: str, default: Any = None) -> Any:
        """Gets a value from the key."""
        try:
            return winreg.QueryValueEx(self._handle, name)[0]
        except FileNotFoundError:
            return default

    def get_value_ex(self, name: str, default: Any = None) -> tuple[Any, int]:
        """Gets a value from the key, returning the value and a type."""
        if not name:
            name = ""  # get the default value
        try:
            return winreg.QueryValueEx(self._handle, name)
        except FileNotFoundError:
            return default, None

    def set_value(self, name: str, value: Any, type=winreg.REG_SZ) -> None:
        """Sets a value in the key"""
        if not name:
            name = ""  # set the default value
        winreg.SetValueEx(self._handle, name, 0, type, value)

    def get(self, name: str, default: Any = None) -> Any:
        """Gets a value from the key"""
        return self.get_value(name, default)

    def __getitem__(self, name: str) -> Tuple[Any, int]:
        """Get a value from the key"""
        try:
            return winreg.QueryValueEx(self._handle, name)[0]
        except FileNotFoundError as e:
            raise KeyError(name) from e

    def __setitem__(self, name: str, value: str) -> None:
        """Sets a value in the key. We assume a string"""
        return self.set_value(name, value)

    def __delitem__(self, name: str) -> None:
        """Deletes a value from the key"""
        try:
            winreg.DeleteValue(self._handle, name)
        except FileNotFoundError as e:
            raise KeyError(name) from e

    def __enter__(self) -> Key:
        """Context manager: opens the key if required"""
        if not self.opened():
            return self.open(**self._kwargs)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def delete(self, tree: bool = False, missing_ok=True) -> None:
        """Deletes the key, optionally recursively."""
        if self.opened():
            raise ValueError("Cannot delete open key")
        if missing_ok and not self.exists():
            return
        if tree:
            with self.open():
                for subkey in list(self.subkeys()):
                    subkey.delete(tree=True)
        winreg.DeleteKey(self._parent, self.name)

    def copy(self) -> Key:
        """Returns a fresh, un-opened copy of the key"""
        return Key(self._parent, self.name)

    def print(self, tree=False, indent=4, level=0):
        """Prints the key to stdout"""
        print(" " * level * indent + f"key: '{self.name}'")
        with self.copy().open() as key:
            for name, value in key.items():
                print(" " * (level + 1) * indent + f"val: '{name}' = {value})")
            if not tree:
                for sub in key.subkeys():
                    print(" " * (level + 1) * indent + f"key: '{sub.name}'")
            else:
                for sub in key.subkeys():
                    sub.print(tree=True, indent=indent, level=level + 1)
