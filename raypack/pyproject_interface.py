"""All pyproject.toml wrangling."""
import logging
from typing import Any, cast

import toml

logger = logging.getLogger(__name__)


def get_project_info_from_toml(toml_file_path: str = "pyproject.toml") -> tuple[str, str]:
    """Read the pyproject.toml and return the project name and version."""
    with open(toml_file_path, encoding="utf-8") as file:
        data = toml.load(file)

    # The project name and version are typically under the [tool.poetry] section
    # Adjust accordingly if your TOML structure differs
    project_name = data.get("tool", {}).get("poetry", {}).get("name", "")
    project_version = data.get("tool", {}).get("poetry", {}).get("version", "")

    # TODO: support PEP 518
    # https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/

    return project_name, project_version


def own_package_includes() -> list[str]:
    """Read the pyproject.toml and return the project name and version."""
    # Load the pyproject.toml content
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_content = toml.load(f)

    poetry_tool = pyproject_content.get("tool", {}).get("poetry", {})
    includes = poetry_tool.get("include", [])

    return cast(list[str], [includes] if isinstance(includes, str) else includes)


# Read and override the default configuration from pyproject.toml, if available
def override_config_from_toml(config: dict[str, Any], toml_file_path: str = "pyproject.toml") -> None:
    """Read the pyproject.toml and override the default CONFIG values."""
    try:
        with open(toml_file_path, encoding="utf-8") as file:
            data = toml.load(file)

        # Check if the [tool.raypack] section exists
        raypack_config = data.get("tool", {}).get("raypack", {})

        # Override the default CONFIG values with the values from the toml file
        config |= raypack_config
    except FileNotFoundError:
        print(f"'{toml_file_path}' not found. Using default configuration.")
