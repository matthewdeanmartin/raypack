"""Interface to Poetry."""
import logging
import shlex
import subprocess

logger = logging.getLogger(__name__)

COMMANDS = [
    "poetry config virtualenvs.create true --local",
    "poetry config virtualenvs.in-project true --local",
    "poetry install --no-dev",
    "poetry build",
]


def create_venv() -> None:
    """Create a virtual environment and install the dependencies."""

    for cmd in COMMANDS:
        logger.debug(f"Command: {cmd}")
        result = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False, shell=False)

        if result.returncode == 0:
            print(f"Command '{cmd}' executed successfully!")
            print(result.stdout)
        else:
            print(f"Command '{cmd}' failed!")
            print(result.stdout)
            print(result.stderr)
