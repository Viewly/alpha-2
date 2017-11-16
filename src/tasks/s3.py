import io

import boto3

config = dict(
    region_name='us-west-2',
    bucket_name='viewly-uploads-test'
)


class S3Transfer:
    def __init__(self, region_name=None, bucket_name=None):
        self._region_name = region_name or config['region_name']
        self._bucket_name = bucket_name or config['bucket_name']

        self.s3 = boto3.client(
            's3',
            region_name=config['region_name']
        )

    def download_bytes(self, key: str) -> io.BytesIO:
        response = self.s3.get_object(
            Bucket=config['bucket_name'],
            Key=key
        )
        return io.BytesIO(response['Body'].read())

    def upload_file(self, file_path: str, key: str, overwrite=True):
        # don't overwrite unless allowed
        if self.key_exists(key) and not overwrite:
            return

        return self.s3.upload_file(
            file_path,
            config['bucket_name'],
            key,
        )

    def key_exists(self, key):
        try:
            self.s3.get_object_acl(
                Bucket=config['bucket_name'],
                Key=key
            )
        except self.s3.exceptions.NoSuchKey:
            return False

        return True
