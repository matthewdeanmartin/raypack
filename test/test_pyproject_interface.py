import toml
from unittest.mock import mock_open
from raypack.pyproject_interface import get_project_info_from_toml

MOCK_TOML_DATA = "[tool.poetry]\nname = 'test_project'\nversion = '0.1.0'"


def test_get_project_info_from_toml(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data=MOCK_TOML_DATA))
    # monkeypatch.setattr(toml, 'load', mock_toml_load)

    project_name, project_version = get_project_info_from_toml()
    assert project_name == "test_project"  # Assuming you'd also return the project name from your function


def test_no_poetry_section(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data=MOCK_TOML_DATA))
    monkeypatch.setattr(toml, "load", lambda x: {})

    project_name, project_version = get_project_info_from_toml()
    assert project_name == ""
