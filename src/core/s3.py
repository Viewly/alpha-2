import io

import boto3
from botocore.config import Config as BotoConfig
from boto3.s3.transfer import S3Transfer as BotoTransfer
from boto3.s3.transfer import TransferConfig

from ..config import (
    S3_UPLOADS_BUCKET,
    S3_UPLOADS_REGION,
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
)


class S3Transfer:
    def __init__(
            self,
            region_name=None,
            bucket_name=None,
            accelerated_transfer=True,
            **kwargs,
    ):
        self._region_name = region_name or S3_UPLOADS_REGION
        self._bucket_name = bucket_name or S3_UPLOADS_BUCKET

        self.client = boto3.client(
            's3',
            region_name=self._region_name,
            aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
            aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
            config=BotoConfig(s3={
                "use_accelerate_endpoint": accelerated_transfer,
            })
        )

        self._config = TransferConfig(
            multipart_threshold=25 * 1024 * 1024,  # 25 MB
            max_concurrency=15,
            num_download_attempts=5,
            io_chunksize=1024 * 1024,  # 1 MB
        )
        self.transfer = BotoTransfer(self.client, self._config)

    def download_bytes(self, key: str) -> io.BytesIO:
        response = self.client.get_object(
            Bucket=self._bucket_name,
            Key=key
        )
        return io.BytesIO(response['Body'].read())

    def upload_fileobj(self, obj, key: str, overwrite=True):
        # s3 weirdness prevention
        key = key.lstrip('/')

        # don't overwrite unless allowed
        if self.key_exists(key) and not overwrite:
            return

        return self.client.upload_fileobj(
            obj,
            self._bucket_name,
            key,
        )

    def key_exists(self, key):
        try:
            self.client.get_object_acl(
                Bucket=self._bucket_name,
                Key=key
            )
        except self.client.exceptions.NoSuchKey:
            return False

        return True

    def download_file(self, key: str, file_name: str):
        return self.transfer.download_file(
            self._bucket_name,
            key,
            file_name
        )

    def upload_file(self, file_path: str, key: str, overwrite=True):
        # s3 weirdness prevention
        key = key.lstrip('/')

        # don't overwrite unless allowed
        if self.key_exists(key) and not overwrite:
            return

        return self.transfer.upload_file(
            file_path,
            self._bucket_name,
            key,
        )

    def ls(self, prefix: str):
        """ Limited to 1000 entries. """
        result = self.client.list_objects_v2(
            Bucket=self._bucket_name,
            MaxKeys=1000,
            Prefix=prefix)

        return result.get('Contents', [])
