"""
This module contains the functions to load and save the versions metadata
"""

import json


def load_version_metadata(versions_file_path):
    """
    Load the versions metadata from a file
    Args:
        versions_file_path:

    Returns:

    """
    try:
        with open(versions_file_path, 'r') as sources_file:
            return json.load(sources_file)
    except FileNotFoundError:
        return {}


def save_version_metadata(data, to):
    """
    Save the versions metadata to a file
    Args:
        data: The dict containing the metadata for each package
        to: the file of the json where the metadata will be saved

    Returns:

    """
    with open(to, 'w') as sources_file:
        json.dump(data, sources_file, indent=2)
