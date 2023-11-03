"""Interface to Poetry."""
import logging
import os
import platform
import shlex
import subprocess
import sys
from typing import Any

logger = logging.getLogger(__name__)

NATIVE_COMMANDS = [
    "poetry config virtualenvs.create true --local",
    "poetry config virtualenvs.in-project true --local",
    "poetry install --only main",
    "poetry build",
]


def export_to_requirements_txt() -> Any:
    """Pipe results to text"""
    with open("requirements-poetry.txt", "w", encoding="utf-8") as out:
        return subprocess.run(
            ["poetry", "export", "--without-hashes", "--format=requirements.txt"], stdout=out, check=False
        )


NONNATIVE_COMMANDS = [
    "poetry build",
    # this is your only option for non-arm64
    # "poetry export --without-hashes --format=requirements.txt > requirements-poetry.txt",
    export_to_requirements_txt,
    "pip install -r requirements-poetry.txt --target vendor --upgrade --platform=linux_arm64 --only-binary=:all:",
]


def create_native_arm64_venv() -> None:
    """Create a virtual environment and install the dependencies."""

    environ = os.environ.copy()
    if "arm64" not in platform.platform().lower():
        print("Switching to attempting to create zip on non-arm64 using pre-comipiled")
        return create_venv()
    return run_commands(NATIVE_COMMANDS, environ)


def create_venv() -> None:
    """Create a virtual environment and install the dependencies."""

    environ = os.environ.copy()
    if platform.platform() != "arm64":
        print(f"Will attempt to install only wheels, can't compile to arm64 on {platform.platform()}")
        environ["PIP_ONLY_BINARY"] = ":all:"
    # manylinux2014_aarch64 rumored to work on aws arm64
    # example plat for mypy macosx_11_0_arm64.whl
    environ["PIP_PLATFORM"] = "macosx_11_0_arm64"
    try:
        run_commands(NONNATIVE_COMMANDS, environ)
    finally:
        os.environ["PIP_PLATFORM"] = ""


def run_commands(commands: list[Any], environ: Any) -> None:
    """Just run commands"""
    for cmd in commands:
        if not isinstance(cmd, str):
            result = cmd()
        else:
            logger.debug(f"Command: {cmd}")
            result = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                # capture_output=True,
                check=False,
                shell=False,  # False is secure.
                env=environ,
            )
        if result.returncode == 0:
            print(f"Command '{cmd}' executed successfully!")
            print(result.stdout)
        else:
            print(f"Command '{cmd}' failed!")
            print(result.stdout)
            print(result.stderr)
            sys.exit(-1)
