from typing import Literal

from .utils.constants import SUPPORTED_BUMP_TYPES, VERSION_METADATA_FILE
from .utils.git import has_code_changed as _has_code_changed
from .utils.metadata import (load_version_metadata as _load_version_metadata,
                             save_version_metadata as _save_version_metadata)
from .utils.version import (parse_version as _parse_version, get_version_file_path as _get_version_file_path,
                            bump_version as _bump_version, save_bump as _save_bump)


def bump_packages_if_modified(src_folder, packages: list[str], bump_level: SUPPORTED_BUMP_TYPES = 'patch',
                              versions_json_file=VERSION_METADATA_FILE):
    version_metadata = _load_version_metadata(versions_json_file)

    for package in packages:
        print(f"Checking and bumping {package}")

        # Check if the package has been modified
        if latest_commit_hash := _has_code_changed(src_folder, package, version_metadata):
            print(f"Changes detected in package '{package}'.")

            # Parse current version
            version_file_path = _get_version_file_path(src_folder, package)
            version = _parse_version(version_file_path)
            print(f"Current version: {version}")

            # Bump version
            bumped_version = _bump_version(version, bump_level)
            print("Bumping...")
            print(f"Bumped version: {bumped_version}")

            # Save bumped version metadata
            version_metadata[package] = {
                "version": str(bumped_version),
                "commit_hash": latest_commit_hash
            }

            # Save bumped version into the __version__.py file
            _save_bump(version_file_path, bumped_version)
            print(f"Version successfully bumped to {bumped_version} for package {package}")
        else:
            print(f"No changes detected in package '{package}'.")

    print("Saving versions metadata")
    _save_version_metadata(data=version_metadata, to=versions_json_file)
