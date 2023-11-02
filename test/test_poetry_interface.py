# import shlex
# import subprocess
# from unittest.mock import patch, call, Mock
# import raypack  # Replace 'your_module_name' with the actual module name
# import raypack.poetry_interface
#
#
# def test_create_venv_success():
#     """Test successful command executions."""
#     # Given: Mocked subprocess that always succeeds
#     mock_run = Mock(return_value=Mock(returncode=0, stdout="Success", stderr=""))
#     mock_logger = Mock()
#
#     with patch("raypack.poetry_interface.subprocess.run", mock_run), patch(
#         "raypack.poetry_interface.logger.debug", mock_logger.debug
#     ):
#         # When: create_venv is called
#         raypack.poetry_interface.run_commands(raypack.poetry_interface.NATIVE_COMMANDS, {})
#
#         # Then:
#         # Verify subprocess.run calls
#         environ = {}
#         expected_calls = [
#             call(
#                 shlex.split(command),
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True,
#                 # capture_output=True,
#                 check=False,
#                 shell=False,  # False is secure.
#                 env=environ,
#             )
#             for command in raypack.poetry_interface.NATIVE_COMMANDS
#         ]
#         mock_run.assert_has_calls(expected_calls, any_order=False)
#
#         # Verify logger.debug calls
#         expected_log_calls = [call(f"Command: {command}") for command in raypack.poetry_interface.NATIVE_COMMANDS]
#         mock_logger.debug.assert_has_calls(expected_log_calls, any_order=False)
