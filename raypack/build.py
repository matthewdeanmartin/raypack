"""
Build a zip file for AWS Glue, Ray.io tasks.

Don't put config or argparse logic here.
"""

import contextlib
import glob
import logging
import os
import platform
import sys
import zipfile
from pathlib import PurePath
from typing import Optional

from raypack import poetry_interface
from raypack.config_loading import Config
from raypack.pyproject_interface import get_project_info_from_toml

logger = logging.getLogger(__name__)


def check_for_binary_files(directory: str) -> list[str]:
    """Check for binary files in a directory."""
    binary_extensions = {".so", ".pyd", ".dll", ".dylib"}  # Add more extensions as needed
    binary_files = []

    for root, _dirs, files in os.walk(directory):
        for filename in files:
            if any(filename.endswith(ext) for ext in binary_extensions):
                binary_files.append(os.path.join(root, filename))

    return binary_files


def create_filename(name: str, version: str) -> str:
    """Create a filename similar to bdist_wheel name, but not the simpler."""

    # Determine the Python version
    python_version = f"py{str(sys.version_info.major)}.{str(sys.version_info.minor)}"

    # Determine the operating system
    os_name = platform.system().lower()  # e.g., "windows", "linux", "darwin" for macOS

    # Determine the CPU bitness
    bitness = "64" if sys.maxsize > 2**32 else "32"

    os_bitness = f"{os_name}{bitness}"

    return f"{name}-{version}-{python_version}-{os_name}-{os_bitness}.zip"


def find_site_packages(start_dir: str = ".virtualenv") -> Optional[str]:
    """Find the site-packages directory in a virtual environment."""
    return next(
        (os.path.join(root, "site-packages") for root, dirs, _files in os.walk(start_dir) if "site-packages" in dirs),
        None,
    )


def find_single_whl_in_dist(dist_folder: str = "dist/") -> str:
    """Find the wheel"""
    # List all .whl files in the dist_folder
    whl_files = [f for f in os.listdir(dist_folder) if f.endswith(".whl")]

    # Check if there's exactly one .whl file
    if len(whl_files) == 1:
        return os.path.join(dist_folder, whl_files[0])
    raise TypeError(f"Expected exactly one .whl file in {dist_folder}, found {len(whl_files)}.")


def get_site_packages_dir(config: Config) -> str:
    """Find site-packages regardless of virtual environment or OS."""
    venv_name = config.source_venv
    if not os.path.exists(venv_name):
        # will fall back to faking it on non-arm64
        poetry_interface.create_native_arm64_venv()
    full_path = os.path.abspath(venv_name)
    print(f"Virtual environment found at {full_path}")

    site_package_dir = find_site_packages(venv_name)
    if not site_package_dir or not os.path.exists(site_package_dir):
        logger.warning(f"No site-packages, assuming installed with --target at {full_path}")
        return full_path
        # raise TypeError("Could not find site-packages directory")
    return site_package_dir


def uses_aarch64manylinux() -> bool:
    """Is build server AWS compatible AFAIK?"""
    return platform.machine() == "aarch64" and platform.system() == "Linux"


def run_with_config(config: Config, output_zip_name: Optional[str] = None) -> None:
    """Package files for AWS Glue, Ray.io tasks."""

    if not uses_aarch64manylinux():
        logger.warning(
            "From AWS documentation: Ray jobs can run provided binaries, but they must be\n"
            "compiled for Linux on ARM64. "
            "This means you might be able to use the contents of aarch64manylinux wheels.\n"
            "\n"
            "If you are not building on an aarch65 linux machine, your packages will need to be pure python."
        )

    cwd = os.getcwd()
    logger.debug(f"Current working directory: {cwd}")

    if not output_zip_name:
        name, version = get_project_info_from_toml()
        output_zip_name = create_filename(name, version)
        logger.info(f"Using default output filename: {output_zip_name}")
    venv_path = get_site_packages_dir(Config())
    logger.info(f"Packaging site-packages from {venv_path}")

    binaries_in_venv = check_for_binary_files(venv_path)
    if binaries_in_venv:
        logger.warning("Binary files found in virtualenv.")
    if binaries_in_venv and config.deps_are_pure_python:
        logger.warning("Binary files found in virtualenv, but deps_are_pure_python is true.")
        logger.warning("You need to be on an ARM64 to safely build binaries")
        logger.warning("Please set deps_are_pure_python to `false` in pyproject.toml.")
        sys.exit(-1)

    # includes = own_package_includes()

    # Zip the directory
    count = 0

    # implied that this is not wanted, but who knows, maybe someone's app depends on one of these.
    exclusions = [
        "_distutils_hack",
        "wheel",
        "pkg_resources",
        "pip",
        "setuptools",
        "__pycache__",
    ]
    # own_package_exclusions = [
    #     "__pycache__",
    # ]
    outer_folder_name = config.outer_folder_name

    with contextlib.suppress(FileNotFoundError):
        os.remove(output_zip_name)
    with zipfile.ZipFile(output_zip_name, "w") as zipf:
        count = zipup_virtualenv(config, count, exclusions, outer_folder_name, venv_path, zipf)
        if count == 0:
            logger.warning("No files were added to the zip file from virtual env")

        # own_count = zipup_own_module(config, includes, outer_folder_name, zipf)
        whl_file = find_single_whl_in_dist()
        own_count = zipup_own_module_from_wheel(whl_file, outer_folder_name, zipf)
        if own_count == 0:
            logger.warning("No files were added to the zip file from own module")
        total_count = count + own_count
    if total_count == 0:
        raise TypeError("No files were added to the zip file. Check the path to site-packages.")


def zipup_virtualenv(
    config: Config, count: int, exclusions: list[str], outer_folder_name: str, venv_path: str, zipf: zipfile.ZipFile
) -> int:
    """Zip up the virtual environment."""
    # virtual environment.
    for foldername, _subfolders, filenames in os.walk(venv_path, topdown=True):
        _subfolders[:] = [d for d in _subfolders if not any(foldername.endswith(folder) for folder in exclusions)]

        if config.exclude_packaging_cruft and any(foldername.endswith(folder) for folder in exclusions):
            logger.warning(f"excluding: {foldername}")
            continue

        # AWS explicitly asks to remove this.
        if foldername.endswith("dist-info"):
            # remove dist-info
            continue

        for filename in filenames:
            skip_this = False

            # check again for dist-info
            path_parts = PurePath(filename).parts
            if any(part.endswith(".dist-info") for part in path_parts):
                skip_this = True
            is_packaging_cruft = (
                filename.endswith(".pth") or filename.endswith(".virtualenv") or filename == "_virtualenv.py"
            )
            if config.exclude_packaging_cruft and is_packaging_cruft:
                skip_this = True
            if "__MACOSX" not in filename and not skip_this:
                count += 1
                # AWS Glue wants an extra folder (docs call it temp_folder, but name doesn't seem to matter)
                filepath = os.path.join(foldername, filename)
                # print(f"Adding {filepath}")
                zipf.write(filepath, os.path.join(outer_folder_name, os.path.relpath(filepath, venv_path)))
            else:
                logger.warning(f"Skipping {filename}")
    return count


def zipup_own_module_from_wheel(source_whl: str, outer_folder_name: str, new_zip: zipfile.ZipFile) -> int:
    """Copy a .whl file to a new .zip file, excluding the .dist-info/ folders."""
    # copy_without_dist_info('source.whl', 'destination.zip')
    count = 0
    with zipfile.ZipFile(source_whl, "r") as whl:
        for file_info in whl.infolist():
            path_parts = PurePath(file_info.filename).parts
            if any(part.endswith(".dist-info") for part in path_parts):
                continue
            with whl.open(file_info.filename) as source_file:
                filepath = os.path.join(outer_folder_name, file_info.filename)
                new_zip.writestr(filepath, source_file.read())
                count += 1
    return count


def zipup_own_module(config: Config, includes: list[str], outer_folder_name: str, zipf: zipfile.ZipFile) -> int:
    """Zip up the project's own code, without using wheel."""
    count = 0
    # User code as governed by pyproject.toml includes
    for file_glob in includes:
        # Expand the glob pattern
        matched_files = glob.glob(file_glob, recursive=True)

        if not matched_files:
            logger.warning(f"Warning: No files matched for pattern {file_glob}.")
            continue

        for file in matched_files:
            is_packaging_cruft = file.endswith(".pth") or file.endswith(".virtualenv") or file == "_virtualenv.py"
            skip_this = False
            if config.exclude_packaging_cruft and is_packaging_cruft:
                skip_this = True

            # TODO: do a folder name check, not a substring check
            if "__pycache__" in file:
                skip_this = True
            if "__MACOSX" not in file and not skip_this:
                # AWS Glue wants an extra folder (docs call it temp_folder, but name doesn't seem to matter)
                filepath = os.path.join(outer_folder_name, file)
                count += 1
                zipf.write(file, filepath)
    return count
