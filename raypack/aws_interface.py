"""
# Usage
output_zip_path = "path_to_your_zip_file.zip"
bucket = "your_bucket_name"
upload_to_s3(output_zip_path, bucket)
"""
import logging
from pathlib import Path

import boto3


def upload_to_s3(output_zip_path: str, bucket: str) -> None:
    """Upload a file to an S3 bucket"""
    # Create an S3 client
    s3 = boto3.client("s3")

    # Convert the string path to a Path object
    path_obj = Path(output_zip_path)
    if not path_obj.exists():
        logging.error(f"Can't upload {path_obj} doesn't exist.")

    # Extract the filename from the path to use as the S3 object name
    filename = path_obj.name

    # Upload the file to S3
    s3.upload_file(str(path_obj), bucket, filename)
