import glob
import os.path
import re
import stat
import uuid
from typing import List, Optional, Tuple

from .desktop_win import (
    enumerate_engine_installations,
    normalize_root,
    register_engine_installation,
)

# stuff which helps with the engine management on the desktop. Based on the
# DesktopPlatformBase class from the UnrealEngine.


def is_guid(s: str) -> bool:
    """Check if the string is a guid"""
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


def get_engine_descriptions() -> List[Tuple[str, str, str]]:
    """Get the descriptions of the engines installed on the system."""
    for engine_id, root_dir in enumerate_engine_installations().items():
        yield (engine_id, root_dir, get_engine_description(engine_id, root_dir))


def get_engine_description(identifier: str, root_dir=None) -> str:
    """Get the description of the engine from the identifier."""
    if is_stock_engine_release(identifier):
        return identifier

    # Otherwise get the path
    root_dir = root_dir or get_engine_root_dir_from_identifier(identifier)
    if not root_dir:
        return ""

    platform_root_dir = os.path.normpath(root_dir)

    # source build
    if is_source_distribution(root_dir):
        return f"Source build at {platform_root_dir}"
    else:
        return f"Binary build at {platform_root_dir}"


def is_stock_engine_release(identifier: str) -> bool:
    """Check if the identifier is a stock engine release."""
    try:
        uuid.UUID(identifier)
        return False
    except ValueError:
        pass

    # classic UE uses only uuids for non-stock engines.  But we allow for
    # other engines, so only if this is a x.y version number do we consider it stock
    match = re.match(r"(\d+\.\d+)", identifier)
    return bool(match)


def get_engine_root_dir_from_identifier(engine_id: str) -> Optional[str]:
    """Look up the engine path from the registry"""
    engines = enumerate_engine_installations()
    return engines.get(engine_id, None)


def get_engine_identifier_from_root_dir(root_dir: str) -> str:
    root_dir = normalize_root
    engines = enumerate_engine_installations()

    # we prefer GUID keys to custom keys.
    found = None
    for k, v in engines.items():
        if v == root_dir:
            if is_guid(k):
                return k
            if not found:
                found = k
    if found:
        return found

    # otherwise, just add it
    return register_engine_installation(root_dir)


def is_valid_root_directory(engine_root):
    """See if this is a proper engine root"""

    # 1 there needs to be an Engine/Binaries folder
    if not os.path.isdir(os.path.join(engine_root, "Engine", "Binaries")):
        return False
    # 2 Also check there's an Engine\Build directory.
    # This will filter out anything that has an engine-like directory structure
    # but doesn't allow building code projects - like the launcher.
    if not os.path.isdir(os.path.join(engine_root, "Engine", "Build")):
        return False

    # 3 Check for a Build.version file.  This will rule out empty directory structures
    if not os.path.isfile(
        os.path.join(engine_root, "Engine", "Build", "Build.version")
    ):
        return False

    # else, we are ok
    return True


def is_source_distribution(engine_root):
    """Check if this is a source distribution"""
    filename = os.path.join(engine_root, "Engine", "Build", "SourceDistribution.txt")
    return os.path.isfile(filename) and stat.stat(filename).st_size > 0


def is_perforce_build(engine_root):
    """Check if this is a perforce build"""
    filename = os.path.join(engine_root, "Engine", "Build", "PerforceBuild.txt")
    return os.path.isfile(filename) and stat.stat(filename).st_size > 0


class ProjectDirectory:
    cache = {}

    def __init__(self, root):
        self.root = root
        # project dictionary for a given engine
        roots, projects = self.get_project_dictionary(root)
        self.project_root_dirs = roots
        self.projects = projects

    @classmethod
    def get_project_dictionary(cls, engine_root):
        roots = []
        engine_root = os.path.abspath(engine_root)
        for file in glob.glob(os.path.join(engine_root, "*.uprojectdirs")):
            with open(file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith(";"):
                        continue

                    # convert to absolute path
                    if not os.path.isabs(line):
                        line = os.path.join(engine_root, line)
                    line = os.path.normcase(os.path.abspath(line))

                    # is it under the root
                    if line.startswith(os.path.normcase(engine_root)):
                        roots.append(line)
                    else:
                        print(
                            f"Warning: project search path {line} is not under engine root"
                        )

        # Search for all the projects under each root directory
        projects = []
        for root in roots:
            uprojects = glob.glob(os.path.join(root, "*", "*.uproject"))
            for up in uprojects:
                projects.append(
                    (os.path.basename(up), os.path.normcase(os.path.abspath(up)))
                )
        return roots, projects

    @classmethod
    def get(cls, engine_root):
        engine_root = os.path.abspath(engine_root)
        if engine_root in cls.cache:
            return cls.cache[engine_root]

        # create a new one
        result = cls(engine_root)
        cls.cache[engine_root] = result
        return result

    def is_foreign_project(self, project_file_name):
        # a foreign project is one which is not 'native', i.e. outside the engine root
        # check if this project is within the engine
        project_file_name = os.path.normcase(os.path.abspath(project_file_name))
        projects = [x[1] for x in self.projects]
        if project_file_name in projects:
            return False
        # could be a new project, check if its parent dir is in the project root dirs
        project_root_dir = os.path.dirname(project_file_name)
        if project_root_dir in self.project_root_dirs:
            return False

        # ok, must be foreign, then
        return True
