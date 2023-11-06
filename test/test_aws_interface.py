import boto3
import moto

from raypack.aws_interface import upload_to_s3


@moto.mock_s3
def test_s3_bucket():
    conn = boto3.resource("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    conn.create_bucket(Bucket=bucket_name)
    upload_to_s3(output_zip_path=__file__, bucket=bucket_name)
