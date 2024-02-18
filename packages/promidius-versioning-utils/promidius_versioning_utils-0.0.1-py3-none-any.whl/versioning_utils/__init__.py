from typing import Literal

from .utils.constants import SUPPORTED_BUMP_TYPES, VERSION_METADATA_FILE
from .utils.git import has_code_changed
from .utils.metadata import load_version_metadata, save_version_metadata
from .utils.version import parse_version, get_version_file_path, bump_version, save_bump


def bump_packages_if_modified(src_folder, packages: list[str], bump_level: SUPPORTED_BUMP_TYPES = 'patch',
                              versions_json_file=VERSION_METADATA_FILE):
    version_metadata = load_version_metadata(versions_json_file)

    for package in packages:
        print(f"Checking and bumping {package}")
        if latest_commit_hash := has_code_changed(src_folder, package, version_metadata):
            version_file_path = get_version_file_path(src_folder, package)
            version = parse_version(version_file_path)
            print(f"Current version: {version}")
            bumped_version = bump_version(version, bump_level)
            print(f"Bumped version: {bumped_version}")
            version_metadata[package] = {
                "version": str(bumped_version),
                "commit_hash": latest_commit_hash
            }
            print("Bumping version...")
            save_bump(version_file_path, bumped_version)
            print(f"Version successfully bumped to {bumped_version} for package {package}")
        else:
            print(f"No changes detected in package '{package}'.")

    print("Saving versions metadata")
    save_version_metadata(data=version_metadata, to=versions_json_file)
