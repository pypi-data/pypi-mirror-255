import os
from typing import Literal

from packaging.version import Version, parse, InvalidVersion


def save_bump(version_file_path, v: Version):
    """
    Writes the new version into the __version__.py file
    Args:
        version_file_path: the path to the __version__.py file
        v:

    Returns:

    """
    with open(version_file_path, 'w') as version_file:
        version_file.write(f"__version__ = '{v}'\n")


def bump_version(v: Version, level: Literal["major", "minor", "patch", "alpha", "dev"] = 'patch'):
    """
    Bumps the version according to the specified level
    Args:
        v:
        level:

    Returns: The new bumped version

    """
    major = v.release[0]
    minor = v.release[1]
    patch = v.release[2]
    alpha = None if not v.pre else v.pre[1]
    dev = None if not v.is_devrelease else v.dev

    match level:
        case "major":
            major, minor, patch = major + 1, 0, 0
            alpha, dev = None, None
        case "minor":
            minor, patch = minor + 1, 0
            alpha, dev = None, None
        case "patch":
            patch += 1
            alpha, dev = None, None
        case "alpha":
            alpha = alpha + 1
            dev = None
        case "dev":
            dev = dev + 1

    version_str = f"{major}.{minor}.{patch}"
    if alpha is not None:
        version_str += f"a{alpha}"
    if dev is not None:
        version_str += f"dev{dev}"
    return parse(version_str)


def parse_version(version_file_path) -> Version:
    """
    Reads the current version from the __version__.py file and returns a Version object
    Args:
        version_file_path: the path to the __version__.py file

    Returns: The Version object

    """
    try:
        with open(version_file_path, 'r') as version_file:
            version_globals = {}
            exec(version_file.read(), version_globals)
            raw_version = version_globals.get('__version__')

            if raw_version:
                try:
                    # Validate the version using the packaging library
                    return parse(raw_version)
                except InvalidVersion:
                    print(f"Warning: Invalid version '{raw_version}")
            else:
                raise ValueError(f"No version found at {version_file_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Version file not found at {version_file_path}")


def get_version_file_path(source_folder, package_name):
    """
    Returns the path to the __version__.py file
    Args:
        source_folder: the path to the src folder
        package_name: the name of the package

    Returns:

    """
    return os.path.join(source_folder, package_name, "__version__.py")