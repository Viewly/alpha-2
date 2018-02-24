import io

import boto3

from ..config import (
    S3_UPLOADS_BUCKET,
    S3_UPLOADS_REGION,
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
)


class S3Transfer:
    def __init__(self, region_name=None, bucket_name=None):
        self._region_name = region_name or S3_UPLOADS_REGION
        self._bucket_name = bucket_name or S3_UPLOADS_BUCKET

        self.s3 = boto3.client(
            's3',
            region_name=self._region_name,
            aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
            aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
        )

    def download_bytes(self, key: str) -> io.BytesIO:
        response = self.s3.get_object(
            Bucket=self._bucket_name,
            Key=key
        )
        return io.BytesIO(response['Body'].read())

    def download_file(self, key: str, file_name: str):
        return self.s3.download_file(
            self._bucket_name,
            key,
            file_name
        )

    def upload_file(self, file_path: str, key: str, overwrite=True):
        # don't overwrite unless allowed
        if self.key_exists(key) and not overwrite:
            return

        return self.s3.upload_file(
            file_path,
            self._bucket_name,
            key,
        )

    def upload_fileobj(self, obj, key: str, overwrite=True):
        # don't overwrite unless allowed
        if self.key_exists(key) and not overwrite:
            return

        return self.s3.upload_fileobj(
            obj,
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
