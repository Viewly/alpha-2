from ..config import (
    S3_VIDEOS_BUCKET,
    S3_VIDEOS_REGION,
    AWS_MANAGER_PUBLIC_KEY,
    AWS_MANAGER_PRIVATE_KEY,
)
import boto3


class Rekognition:
    def __init__(
            self,
            region_name=None,
            bucket_name=None,
    ):
        self._region_name = region_name or S3_VIDEOS_REGION
        self._bucket_name = bucket_name or S3_VIDEOS_BUCKET

        self.client = boto3.client(
            'rekognition',
            region_name=self._region_name,
            aws_access_key_id=AWS_MANAGER_PUBLIC_KEY,
            aws_secret_access_key=AWS_MANAGER_PRIVATE_KEY,
        )

    def nsfw(self, key: str, **kwargs):
        response = self.client.detect_moderation_labels(
            Image={
                'S3Object': {
                    'Bucket': self._bucket_name,
                    'Name': key,
                }
            },
            MinConfidence=kwargs.get('min_confidence', 80),
        )
        return response.get('ModerationLabels')

    def labels(self, key: str, **kwargs):
        response = self.client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': self._bucket_name,
                    'Name': key,
                }
            },
            MaxLabels=kwargs.get('max_labels', 100),
            MinConfidence=kwargs.get('min_confidence', 80),
        )
        return response.get('Labels')
