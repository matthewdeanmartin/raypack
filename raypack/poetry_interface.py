"""Interface to Poetry."""
import shlex
import subprocess


def create_venv() -> None:
    """Create a virtual environment and install the dependencies."""
    commands = [
        "poetry config virtualenvs.create true",
        "poetry config virtualenvs.in-project true",
        "poetry install --no-dev",
    ]

    for cmd in commands:
        result = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=True)

        if result.returncode == 0:
            print(f"Command '{cmd}' executed successfully!")
            print(result.stdout)
        else:
            print(f"Command '{cmd}' failed!")
            print(result.stderr)
