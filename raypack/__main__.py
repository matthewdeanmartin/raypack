"""
Raypack will create a package for AWS Glue, Ray.io tasks.

If you are only using included-by-default packages, public packages, pure python packages, 
binary wheel packages, you don't have to do this.

AWS Glue can't handle anything without a binary wheel or private package repositories.

So you have build on a machine that matches the AWS runtime OS (Fedora-like), create a virtual directory,
and then zip it up and upload it to s3.

This tool aims to do that and be pipx installable and work on any OS

Some code generate with ChatGPT (OpenAI)
"""
import argparse
import logging
import logging.config
import sys

from raypack.build import run_with_config
from raypack.config_loading import CONFIG_INFO, Config
from raypack.logging_utils import configure_logging
from raypack.pyproject_interface import override_config_from_toml

logger = logging.getLogger(__name__)


def main() -> int:
    """Parse args and run the application."""
    parser = argparse.ArgumentParser(description="Raypack will create a package for AWS Glue, Ray.io tasks.")

    # Adding arguments based on the CONFIG_INFO structure
    parser.add_argument(
        "--exclude-packaging-cruft",
        action="store_true",
        help="Exclude packaging cruft files. Default is True.",
        default=True,
    )
    parser.add_argument(
        "--outer-folder-name", type=str, help="Name of the outer folder. Default is 'venv'.", default="venv"
    )
    parser.add_argument(
        "--source-venv", type=str, help="Source virtual environment. Default is '.venv'.", default=".venv"
    )
    parser.add_argument(
        "--venv-tool",
        type=str,
        choices=["poetry", "pip"],
        help="Tool used for managing the virtual environment. Default is 'poetry'.",
        default="poetry",
    )
    parser.add_argument(
        "--deps-are-pure-python",
        action="store_true",
        help="Specify if the dependencies are pure Python. Default is False.",
        default=False,
    )

    # Adding version and verbose options
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("--verbose", action="store_true", help="Increase output verbosity.", default=False)

    # Parse the arguments
    args = parser.parse_args()

    # Use the gathered values
    config_info = {
        "exclude_packaging_cruft": args.exclude_packaging_cruft
        if args.exclude_packaging_cruft is not None
        else CONFIG_INFO["exclude_packaging_cruft"],
        "outer_folder_name": args.outer_folder_name if args.outer_folder_name else CONFIG_INFO["outer_folder_name"],
        "source_venv": args.source_venv if args.source_venv else CONFIG_INFO["source_venv"],
        "venv_tool": args.venv_tool if args.venv_tool else CONFIG_INFO["venv_tool"],
        "deps_are_pure_python": args.deps_are_pure_python
        if args.deps_are_pure_python is not None
        else CONFIG_INFO["deps_are_pure_python"],
    }
    config = Config.from_dict(config_info)

    # pylint: disable=broad-except,bare-except
    try:
        use_args(config, args.verbose)
        return 0
    except:
        if args.verbose:
            raise
        return -1


def use_args(_config: Config, verbose: bool) -> None:
    """Run the application."""
    if verbose:
        logging_config = configure_logging()
        logging.config.dictConfig(logging_config)
        logger.info("Verbose mode enabled")
    override_config_from_toml(CONFIG_INFO)
    final_config = Config.from_dict(CONFIG_INFO)
    run_with_config(config=final_config)


if __name__ == "__main__":
    # Call the function on application start
    sys.exit(main())
