"""
Deploy script and zip to S3.
"""

from http import HTTPStatus
import logging
import sys

import boto3

from raypack.aws_interface import upload_to_s3
from raypack.config_loading import Config

logger = logging.getLogger(__name__)


def deploy_script_and_zip(config: Config, output_zip_name: str) -> None:
    """Deploy script and zip to S3."""
    print(f"Packaged files saved as {output_zip_name}")
    if config.upload_to_s3 and config.s3_bucket_name == "example":
        print("Can't upload, need bucket name, configure via pyproject.toml")
        sys.exit(-1)
    if config.upload_to_s3:
        logger.info(f"Uploading {output_zip_name} to {config.s3_bucket_name}")
        upload_to_s3(output_zip_name, config.s3_bucket_name)


def update_job_with_script_and_zip(
    job_name: str,
    script_name: str,
    zip_name: str,
    bucket_for_zip: str,
) -> None:
    """Update a Glue job with a new script and zip."""
    # Initialize a Glue client
    glue_client = boto3.client("glue")

    # Specify the new S3 path to the Python modules zip file
    new_s3_py_modules = f"{bucket_for_zip}/{zip_name}"

    # Specify the new list of packages to be installed using pip
    # new_pip_install_packages = ['package1', 'package2', 'package3']

    # Get the current job definition
    job_response = glue_client.get_job(JobName=job_name)
    job = job_response["Job"]

    # Update the job parameters
    job["Command"]["ScriptLocation"] = script_name
    # job['Command']['PythonVersion'] = '3'  # Specify the desired Python version
    job["DefaultArguments"]["--s3-py-modules"] = new_s3_py_modules

    # TODO
    # job['DefaultArguments']['--pip-install'] = ','.join(new_pip_install_packages)

    # Update the job
    response = glue_client.update_job(JobName=job_name, JobUpdate=job)

    # Check the response for success
    if response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK:
        print(f"Job '{job_name}' updated successfully.")
    else:
        print(f"Failed to update job '{job_name}'.")
