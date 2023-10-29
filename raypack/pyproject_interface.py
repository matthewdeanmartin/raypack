"""All pyproject.toml wrangling."""
import functools
import logging
from typing import Any, Optional, cast

import toml

logger = logging.getLogger(__name__)


@functools.cache
def current_pyproject_toml(toml_file_path: str) -> Optional[dict[str, Any]]:
    """Load and cache pyproject.toml file."""
    try:
        with open(toml_file_path, encoding="utf-8") as file:
            data = toml.load(file)
    except FileNotFoundError:
        print(f"'{toml_file_path}' not found.")
        return None
    return data


def get_project_info_from_toml(toml_file_path: str = "pyproject.toml", use_pep621: bool = False) -> tuple[str, str]:
    """Read the pyproject.toml and return the project name and version based on priority."""
    data = current_pyproject_toml(toml_file_path)
    if not data:
        return "", ""

    # Doesn't handle if both are present
    if use_pep621:
        # Check PEP 621 standardized fields first
        project_name = data.get("project", {}).get("name", "")
        project_version = data.get("project", {}).get("version", "")

        # Fallback to Poetry-specific fields if not found
        if not project_name:
            project_name = data.get("tool", {}).get("poetry", {}).get("name", "")
        if not project_version:
            project_version = data.get("tool", {}).get("poetry", {}).get("version", "")
    else:
        # Check Poetry-specific fields first
        project_name = data.get("tool", {}).get("poetry", {}).get("name", "")
        project_version = data.get("tool", {}).get("poetry", {}).get("version", "")

        # Fallback to PEP 621 standardized fields if not found
        if not project_name:
            project_name = data.get("project", {}).get("name", "")
        if not project_version:
            project_version = data.get("project", {}).get("version", "")

    # if not project_name or not project_version:
    #     raise ValueError("Project name and/or version not found in pyproject.toml")

    return project_name, project_version


def own_package_includes(toml_file_path: str = "pyproject.toml") -> list[str]:
    """Read the pyproject.toml and return the project name and version."""
    # Load the pyproject.toml content
    data = current_pyproject_toml(toml_file_path)
    if not data:
        return []
    poetry_tool = data.get("tool", {}).get("poetry", {})
    includes = poetry_tool.get("include", [])

    return cast(list[str], [includes] if isinstance(includes, str) else includes)


def toml_section_exists(toml_file_path: str = "pyproject.toml") -> bool:
    """Check we have a pyproject.toml file"""
    data = current_pyproject_toml(toml_file_path)
    if not data:
        return False

    # Check if the [tool.raypack] section exists
    raypack_config = data.get("tool", {}).get("raypack", {})
    if raypack_config:
        return True
    return False


# Read and override the default configuration from pyproject.toml, if available
def override_config_from_toml(config: dict[str, Any], toml_file_path: str = "pyproject.toml") -> None:
    """Read the pyproject.toml and override the default CONFIG values."""
    data = current_pyproject_toml(toml_file_path)
    if not data:
        print(f"'{toml_file_path}' not found. Using default configuration.")
        return
    # Check if the [tool.raypack] section exists
    raypack_config = data.get("tool", {}).get("raypack", {})

    # Override the default CONFIG values with the values from the toml file
    config |= raypack_config
