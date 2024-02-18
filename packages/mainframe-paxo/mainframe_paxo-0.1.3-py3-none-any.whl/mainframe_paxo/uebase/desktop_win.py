import os.path
import uuid
from typing import Dict, Optional

from ..registry import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, Key
from . import desktop


def normalize_root(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


def enumerate_engine_installations() -> Dict[str, str]:
    launcher_engines = enumerate_launcher_engine_installations()
    user_engines = enumerate_user_engine_installations()
    launcher_engines.update(user_engines)
    return launcher_engines


def enumerate_launcher_engine_installations() -> Dict[str, str]:
    """Enumerate the engine installations from the launcher"""

    result = {}
    with Key(
        HKEY_LOCAL_MACHINE,
        "SOFTWARE\\EpicGames\\Unreal Engine\\Builds",
    ) as key:
        for subkey in key.subkeys():
            with subkey:
                name = subkey.name
                root = subkey.get("InstalledDirectory", None)
                if root and desktop.is_valid_root_directory(root):
                    result[name] = normalize_root(root)
    return result


def enumerate_user_engine_installations() -> Dict[str, str]:
    """Enumerate the engine installations from the launcher"""

    result = {}
    remove = []  # values to remove
    unique_directories = set()

    with Key(
        HKEY_CURRENT_USER, "SOFTWARE\\Epic Games\\Unreal Engine\\Builds", write=True
    ) as key:
        if not key:
            return result
        for k, v in key.items():
            v = normalize_root(v)
            ok = False
            if desktop.is_valid_root_directory(v):
                try:
                    guid = uuid.UUID(k)
                except ValueError:
                    guid = None
                if guid:
                    # clean out duplicate guid keys for the same engine
                    if v not in unique_directories:
                        unique_directories.add(v)
                        ok = True
                else:
                    # we accept all non-guid keys, since they were created by the user
                    ok = True
            if ok:
                result[k] = v
            else:
                remove.append(k)

        # Remove all the keys which weren't valid
        for k in remove:
            del key[k]
    return result


def register_engine_installation(
    root_dir: str, engine_id: Optional[str]
) -> Optional[str]:
    """Register an engine installation"""
    if not engine_id:
        engine_id = str(uuid.uuid4())
        is_guid = True
    else:
        is_guid = desktop.is_guid(engine_id)
    root_dir = normalize_root(root_dir)
    if not desktop.is_valid_root_directory(root_dir):
        return None

    with Key(
        HKEY_CURRENT_USER, "SOFTWARE\\Epic Games\\Unreal Engine\\Builds", create=True
    ) as key:
        if is_guid:
            # check if there is a guid key with the same root dir
            for k, v in key.items():
                if is_guid(k) and normalize_root(v) == root_dir:
                    # we just re-use the existing guid key
                    return k
        key[engine_id] = root_dir
    return engine_id
