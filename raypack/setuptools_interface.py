"""
Possibly no longer needed. I was trying to get the OS/architecture name for the zip file.
"""
import logging
from typing import Any

from setuptools.dist import Distribution

logger = logging.getLogger(__name__)


def wheel_name(**kwargs: Any) -> str:
    """https://stackoverflow.com/a/60773383/33264"""
    # create a fake distribution from arguments
    dist = Distribution(attrs=kwargs)
    # finalize bdist_wheel command
    bdist_wheel_cmd = dist.get_command_obj("bdist_wheel")
    bdist_wheel_cmd.ensure_finalized()
    # assemble wheel file name
    distname = bdist_wheel_cmd.wheel_dist_name
    tag = "-".join(bdist_wheel_cmd.get_tag())
    return f"{distname}-{tag}.whl"
