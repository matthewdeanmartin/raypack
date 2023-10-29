"""
All config related code
"""
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_INFO = {
    "exclude_packaging_cruft": True,
    "outer_folder_name": "venv",
    "source_venv": ".venv",
    # TODO: support pip as well
    "venv_tool": "poetry",
    "deps_are_pure_python": False,
}


@dataclass
class Config:
    """Configuration for raypack."""

    upload_to_s3: bool = False
    s3_bucket_name: str = "example"
    exclude_packaging_cruft: bool = True
    outer_folder_name: str = "venv"
    source_venv: str = ".venv"
    venv_tool: str = "poetry"
    deps_are_pure_python: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Config":
        """Create a Config instance from a dictionary."""
        return cls(**d)
