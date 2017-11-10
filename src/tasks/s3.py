import io

import boto3

config = dict(
    region_name='us-west-2',
    bucket_name='steem-hackaton-input'
)


def get_image(key: str) -> io.BytesIO:
    s3 = boto3.client(
        's3',
        region_name=config['region_name']
    )
    response = s3.get_object(
        Bucket=config['bucket_name'],
        Key=key
    )
    return io.BytesIO(response['Body'].read())


def write_image(file_path: str, key: str, overwrite=True):
    s3 = boto3.client(
        's3',
        region_name=config['region_name']
    )

    # don't overwrite unless allowed
    if key_exists(s3, key) and not overwrite:
        return

    return s3.upload_file(
        file_path,
        config['bucket_name'],
        key,
    )


def key_exists(s3, key):
    try:
        s3.get_object_acl(
            Bucket=config['bucket_name'],
            Key=key
        )
    except s3.exceptions.NoSuchKey:
        return False

    return True
