import shlex
from unittest.mock import patch, call, Mock
import raypack  # Replace 'your_module_name' with the actual module name
import raypack.poetry_interface


def test_create_venv_success():
    """Test successful command executions."""
    # Given: Mocked subprocess that always succeeds
    mock_run = Mock(return_value=Mock(returncode=0, stdout="Success", stderr=""))
    mock_logger = Mock()

    with patch("raypack.poetry_interface.subprocess.run", mock_run), patch(
        "raypack.poetry_interface.logger.debug", mock_logger.debug
    ):
        # When: create_venv is called
        raypack.poetry_interface.create_venv()

        # Then:
        # Verify subprocess.run calls
        expected_calls = [
            call(
                shlex.split("poetry config virtualenvs.create true --local"),
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            ),
            call(
                shlex.split("poetry config virtualenvs.in-project true --local"),
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            ),
            call(shlex.split("poetry install --no-dev"), capture_output=True, text=True, check=True, shell=False),
        ]
        mock_run.assert_has_calls(expected_calls, any_order=False)

        # Verify logger.debug calls
        expected_log_calls = [
            call("Command: poetry config virtualenvs.create true --local"),
            call("Command: poetry config virtualenvs.in-project true --local"),
            call("Command: poetry install --no-dev"),
        ]
        mock_logger.debug.assert_has_calls(expected_log_calls, any_order=False)
