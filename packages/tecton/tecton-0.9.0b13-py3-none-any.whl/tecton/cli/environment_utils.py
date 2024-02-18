import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

from pkg_resources import parse_requirements

from tecton.cli import printer
from tecton_core.errors import FailedDependencyDownloadError


PLATFORM = "manylinux_2_17_x86_64"
PYTHON_VERSION_TO_PLATFORM = {
    "3.8": f"{PLATFORM}-cp-3.8.17-cp38",
    "3.9": f"{PLATFORM}-cp-3.9.17-cp39",
}

MISSING_REQUIREMENTS_ERROR = "Could not find a version that satisfies the requirement"
ENSURE_WHEELS_EXIST_WARNING = "Please also ensure that the package(s) have wheels (.whl) available for download in PyPI or any other repository used."


def resolve_dependencies(
    requirements_path: Path, resolved_requirements_path: Path, python_version: str, timeout_seconds: int, verbose: bool
):
    """Resolve dependencies using `pex`
    Parameters:
        requirements_path(Path): Path to the `requirements.txt` file
        resolved_requirements_path(Path): The target path for generating the fully resolved and pinned `resolved-requirements.txt` file
        python_version(str): The python version to resolve dependencies for
        timeout_seconds(int): The timeout in seconds for the dependency resolution
    """
    if python_version not in PYTHON_VERSION_TO_PLATFORM:
        msg = f"Invalid `python_version` {python_version}. Expected one of: {list(PYTHON_VERSION_TO_PLATFORM.keys())}"
        raise ValueError(msg)
    platform = PYTHON_VERSION_TO_PLATFORM[python_version]
    if verbose:
        printer.safe_print(f"🔎 Resolving dependencies for platform: {platform}")
    with tempfile.TemporaryDirectory() as tmpdir:
        intermediate_output_path = Path(tmpdir) / "output"
        lock_command = _construct_lock_command(
            requirements_path=requirements_path, target_path=intermediate_output_path, platform=platform
        )
        export_command = _construct_export_command(
            target_path=intermediate_output_path,
            resolved_requirements_path=resolved_requirements_path,
            platform=platform,
        )
        _run_pex_command(command_list=lock_command, timeout_seconds=timeout_seconds, verbose=verbose)
        _run_pex_command(command_list=export_command, timeout_seconds=timeout_seconds, verbose=verbose)


def download_dependencies(requirements_path: Path, target_directory: Path, python_version: str, verbose: bool = False):
    """
    Download wheels for all dependencies in a requirements.txt to a target directory
    Parameters:
        requirements_path(Path): Path to requirements.txt
        target_directory(Path): The target directory to download requirements to
        python_version(str): The python version to download dependencies for
        verbose(bool): Activates verbose logging
    """
    command = _construct_download_command(
        target_path=target_directory, requirements_path=requirements_path, python_version=python_version
    )
    if verbose:
        command_str = " ".join(command)
        printer.safe_print(f"🔎 Executing command: {command_str})")

    result = subprocess.run(
        command,
        text=True,
    )
    if result.returncode != 0:
        raise FailedDependencyDownloadError(result.stderr)


def _run_pex_command(command_list: List[str], timeout_seconds: int, verbose: bool = False):
    """Run the `pex` command passed as input and process any errors
    Parameters:
        command_list(str): The pex command to be executed
        timeout_seconds(int): The timeout in seconds for the pex command
        verbose(bool): Activates verbose logging
    """
    command = [sys.executable, "-m", "tecton.cli.pex_wrapper", *command_list]
    if verbose:
        command_str = " ".join(command)
        printer.safe_print(f"🔎 Executing command: {command_str}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        error_message = (
            "Dependency Resolution timed out! If problem persists, please contact Tecton Support for assistance"
        )
        raise TimeoutError(error_message)
    if result.returncode != 0:
        error_message = result.stderr if verbose else _parse_pex_error(result.stderr)
        raise ValueError(error_message)


def _construct_lock_command(requirements_path: Path, target_path: Path, platform: str) -> List[str]:
    return [
        "lock",
        "create",
        "-r",
        str(requirements_path),
        "--no-build",
        "--style=strict",
        "-o",
        str(target_path),
        "--platform",
        platform,
    ]


def _construct_export_command(target_path: Path, resolved_requirements_path: Path, platform: str) -> List[str]:
    return ["lock", "export", "--platform", platform, str(target_path), "--output", str(resolved_requirements_path)]


def _construct_download_command(target_path: Path, requirements_path: Path, python_version: str):
    return [
        sys.executable,
        "-m",
        "pip",
        "download",
        "-r",
        str(requirements_path),
        "-d",
        str(target_path),
        "--no-cache-dir",
        "--only-binary",
        ":all:",
        "--python-version",
        python_version,
        "--implementation",
        "cp",
        "--platform",
        PLATFORM,
    ]


def _parse_pex_error(error_string: str) -> str:
    """Parse and cleanup error messages from the `pex` command"""
    start_index = error_string.find("ERROR:")
    if start_index != -1:
        error_string = error_string[start_index + 6 :].replace("\n", " ")
    # The pex error message does not clarify that wheels must be present and so we append it to the original error message
    if MISSING_REQUIREMENTS_ERROR in error_string:
        error_string = f"{error_string}\n\n💡 {ENSURE_WHEELS_EXIST_WARNING}"
    return error_string


def is_requirement_present(requirements_path: Path, package_name: str) -> bool:
    requirements = parse_requirements(requirements_path.read_text())
    package_names = [requirement.project_name for requirement in requirements]
    return package_name in package_names


def is_valid_environment_name(name: str) -> bool:
    # Only letters, numbers, hyphens, or underscores allowed in an environment name
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, name))
