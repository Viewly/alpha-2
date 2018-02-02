import io

import boto3

from ..config import (
    S3_UPLOADER_BUCKET,
    S3_UPLOADER_REGION,
)


class S3Transfer:
    def __init__(self, region_name=None, bucket_name=None):
        self._region_name = region_name or S3_UPLOADER_REGION
        self._bucket_name = bucket_name or S3_UPLOADER_BUCKET

        self.s3 = boto3.client(
            's3',
            region_name=self._region_name
        )

    def download_bytes(self, key: str) -> io.BytesIO:
        response = self.s3.get_object(
            Bucket=self._bucket_name,
            Key=key
        )
        return io.BytesIO(response['Body'].read())

    def upload_file(self, file_path: str, key: str, overwrite=True):
        # don't overwrite unless allowed
        if self.key_exists(key) and not overwrite:
            return

        return self.s3.upload_file(
            file_path,
            self._bucket_name,
            key,
        )

    def key_exists(self, key):
        try:
            self.s3.get_object_acl(
                Bucket=self._bucket_name,
                Key=key
            )
        except self.s3.exceptions.NoSuchKey:
            return False

        return True
