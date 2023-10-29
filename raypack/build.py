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
from typing import Optional

from raypack.aws_interface import upload_to_s3
from raypack.config_loading import Config
from raypack.poetry_interface import create_venv
from raypack.pyproject_interface import get_project_info_from_toml

logger = logging.getLogger(__name__)


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
        create_venv()
    full_path = os.path.abspath(venv_name)
    print(f"Virtual environment found at {full_path}")

    site_package_dir = find_site_packages(venv_name)
    if not site_package_dir or not os.path.exists(site_package_dir):
        raise TypeError("Could not find site-packages directory")
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

    print(f"Packaged files saved as {output_zip_name}")
    if config.upload_to_s3 and config.s3_bucket_name == "example":
        print("Can't upload, need bucket name, configure via pyproject.toml")
        sys.exit(-1)
    if config.upload_to_s3:
        logger.info(f"Uploading {output_zip_name} to {config.s3_bucket_name}")
        upload_to_s3(output_zip_name, config.s3_bucket_name)


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
            continue

        for filename in filenames:
            is_packaging_cruft = (
                filename.endswith(".pth") or filename.endswith(".virtualenv") or filename == "_virtualenv.py"
            )
            skip_this = False
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
        # Exclude folders whose name ends with .dist-info/
        dist_info_folders = [info for info in whl.infolist() if info.filename.endswith(".dist-info/")]

        for file_info in whl.infolist():
            if not any(folder.filename in file_info.filename for folder in dist_info_folders):
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
