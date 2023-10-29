import sys
import platform


# A namedtuple to simulate sys.version_info
from collections import namedtuple

from raypack.build import create_filename

VersionInfo = namedtuple("VersionInfo", ["major", "minor"])


def test_create_filename_windows(monkeypatch):
    # Mock values
    mock_version_info = VersionInfo(3, 9)
    mock_system = "Windows"
    mock_maxsize = 2**33  # 64 bit

    # Patching
    monkeypatch.setattr(sys, "version_info", mock_version_info)
    monkeypatch.setattr(platform, "system", lambda: mock_system)
    monkeypatch.setattr(sys, "maxsize", mock_maxsize)

    filename = create_filename("sample_project", "0.1.0")
    expected_filename = "sample_project-0.1.0-py3.9-windows-windows64.zip"

    assert filename == expected_filename


def test_create_filename_linux(monkeypatch):
    # Testing with other mock values
    monkeypatch.setattr(sys, "version_info", VersionInfo(3, 8))
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(sys, "maxsize", 2**31)  # 32 bit

    filename = create_filename("sample_project", "0.1.1")
    expected_filename = "sample_project-0.1.1-py3.8-linux-linux32.zip"

    assert filename == expected_filename


# Add more tests as needed, particularly for edge cases or other OS and versions.
