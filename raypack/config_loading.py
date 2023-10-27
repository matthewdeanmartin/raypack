"""
All config related code
"""
from dataclasses import dataclass
from typing import Any

CONFIG_INFO = {
    "exclude_packaging_cruft": True,
    "outer_folder_name": "venv",
    "source_venv": ".venv",
    # TODO: support pip as well
    "venv_tool": "poetry",
}


@dataclass
class Config:
    """Configuration for raypack."""

    exclude_packaging_cruft: bool = True
    outer_folder_name: str = "venv"
    source_venv: str = ".venv"
    venv_tool: str = "poetry"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Config":
        """Create a Config instance from a dictionary."""
        return cls(**d)
