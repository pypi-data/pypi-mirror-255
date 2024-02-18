"""
Wrapper for git commands
"""
import subprocess


def _get_latest_commit_hash(src_path, package_name):
    """
    Get the latest commit hash where the package_name was last modified
    This assumes a folder structure like:
    src/package_name/__version__.py

    Args:
        src_path: The path to the src folder
        package_name: The name of the package
    Returns:

    """

    try:
        # get latest commit where the module was changed excluding the __version__.py file
        git_command = f'git log -1 --pretty=format:%H -- {src_path}/{package_name} ":^{src_path}/{package_name}/__version__.py"'
        result = subprocess.run(git_command, shell=True, capture_output=True, text=True, check=True)
        result_ = result.stdout.split("\n")[0].strip()
        return result_
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def has_code_changed(source_folder: str, package_name: str, latest_hash: str) -> bool | str:
    """
    Check if the code of the package has been modified since last saved commit.
    Compares the latest git commit hash with the saved commit hash.
    If they don't match then there's been changes in the code.


    Args:
        source_folder: the path to the source folder
        package_name: package name
        latest_hash: the latest commit hash saved


    Returns:
        commit_hash: str - The latest commit hash if the code has changed
        False: bool - If the code has not changed

    """

    latest_commit_hash = _get_latest_commit_hash(source_folder, package_name)
    if latest_hash and latest_hash == latest_commit_hash:
        return False
    else:
        return latest_commit_hash
