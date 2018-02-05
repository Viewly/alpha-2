# Requirements
This guide assumes MacOS with HomeBrew.

## Dependencies
Install JS dependencies
```
cd src/public
npm i
```


Install Python 3.6
```
brew install python3
```


Install Python dependencies:
```
pip install -r requirements.txt
```

Install and Start Redis:
```
brew install redis
brew services start redis
```

Install and start PostgreSQL
```
brew install postgresql
brew services start postgresql
```
*Now you can initialize your SQL database (see Database Management).*

## Environment Variables
To run flask commands, you need `FLASK_APP` environment variable set.
```
export FLASK_APP=src/views.py
```

Here is the default environment (you may want to set these yourself):


| Variable               | Default                          |
| ---------------------- | -------------------------------- |
| PRODUCTION             | False                            |
| SECRET_KEY             | not_a_secret                     |
| POSTGRES_URI           | postgres://localhost/viewly_beta |
| MAIL_USERNAME          | postmaster@mg.view.ly            |
| MAIL_PASSWORD          | ''                               |

_Note: This list does not include AWS related variables. Look for those in AWS section
of the readme_.

## Run Locally
Run the Flask server:
```
flask run --reload --debugger --port 5000
```

## Database Management
In development, you can initialize your PostgreSQL database with:
```
flask db-init
```

If you've messed up, you can nuke the database, and re-create the schemas with:
```
flask db-reset
```

## Database Migrations (optional)
To avoid having to delete and re-create the database in development, we can use migrations.

First, change the schema in `models.py`. 
Then, create a migrations file.
```
flask db migrate -m "example migration message"
```

Lastly, apply the migration:
```
flask db upgrade
```

## Celery Workers
Transcoding workers:
```
celery worker -A src.tasks.transcoder -l info -c 1 -P solo
```

## Celery Cron Jobs
Enable the beat service:
```
celery -A src.tasks.cron beat
```

Run the cron worker:
```
celery worker -A src.tasks.cron -l info -c 1 -P solo
```

# Amazon Services

## S3 Setup
Create S3 Upload and Video storage buckets trough `ElasticTranscoder.ipynb`.

Example config:
```
config = {
    'region_name': 'eu-central-1',
    'pipeline_name': 'viewly-pipeline-v1',
    's3_input_bucket': 'viewly-uploads-eu1',
    's3_output_bucket': 'viewly-videos-eu1',
}
```

ACL and CORS will be applied automatically, however we need to perform some manual tasks
on fresh deployment.

## Uploader Bucket Configuration
**Upload Bucket CORS Policy**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<CORSRule>
    <AllowedOrigin>*</AllowedOrigin>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
    <ExposeHeader>ETag</ExposeHeader>
    <AllowedHeader>content-type</AllowedHeader>
    <AllowedHeader>origin</AllowedHeader>
    <AllowedHeader>x-amz-acl</AllowedHeader>
    <AllowedHeader>x-amz-meta-qqfilename</AllowedHeader>
    <AllowedHeader>x-amz-date</AllowedHeader>
    <AllowedHeader>x-amz-content-sha256</AllowedHeader>
    <AllowedHeader>authorization</AllowedHeader>
</CORSRule>
</CORSConfiguration>
```

**Manual Setup**

Use Amazon S3 Console to:
 - Enable _Transfer Acceleration_ on the Upload bucket
 - Add a lifecycle rule to _Clean up incomplete multipart uploads_
 
 
**IAM Policy**  
Create a `s3-viewly-uploader` API user with the following S3 policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::viewly-uploads-us1/*"
        }
    ]
}
```
_Replace `viewly-uploads-us1` with upload bucket name._
Use this users API credentials as `S3_UPLOADER_PUBLIC_KEY` and `S3_UPLOADER_SECRET_KEY`.

**Environment Variables**

| Variable               | Default             |
| ---------------------- | ------------------- |
| S3_UPLOADS_BUCKET      | viewly-uploads-test |
| S3_UPLOADS_REGION      | us-west-2           |
| S3_UPLOADER_PUBLIC_KEY |                     |
| S3_UPLOADER_SECRET_KEY |                     |

 
## Videos Bucket Configuration
To be able to stream files from this bucket via CloudFormation, the following 
bucket policy needs to be applied:
```json
{
    "Id": "Policy1517839392609",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1517839387764",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::viewly-videos-us1/*",
            "Principal": "*"
        }
    ]
}
```

We also need the following CORS config:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<CORSRule>
    <AllowedOrigin>*</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
    <AllowedHeader>*</AllowedHeader>
</CORSRule>
</CORSConfiguration>
```

**Environment Variables**

| Variable         | Default            |
| ---------------- | ------------------ |
| S3_VIDEOS_BUCKET | viewly-videos-test |
| S3_VIDEOS_REGION | us-west-2          |


## Elastic Transcoder
Use `ElasticTranscoder.ipynb` to create and configure the ET pipeline. 
Output configuration saved [here](src/conf/elastic_transcoder.prod.json).

## CloudFront
Create a Cloudfront Distribution manually.
Use the `viewly-videos-*` bucket, and set the default TTL to 1 day or more.
Create a CNAME (cdn.view.ly), and issue custom certificate trough ACM.

**Environment Variables**

| Variable | Default             |
| -------- | ------------------- |
| CDN_URL  | https://cdn.view.ly |


## IAM Manager Account
The manager account has just the privileges necessary to:
 - Read, Write, Delete files in the uploads and videos buckets
 - Create, Cancel and Read ElasticTranscoder Jobs
 - Invalidate CloudFormation Caches (ie. on thumbnail change)
 
**Manager Policy**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObjectAcl",
                "s3:GetObject",
                "s3:ListBucketMultipartUploads",
                "s3:GetObjectTagging",
                "s3:ListBucket",
                "s3:PutObjectTagging",
                "s3:DeleteObject",
                "s3:GetBucketAcl",
                "s3:GetBucketLocation",
                "s3:PutObjectAcl",
                "s3:GetObjectVersion"
            ],
            "Resource": [
                "arn:aws:s3:::viewly-uploads-us1",
                "arn:aws:s3:::viewly-videos-us1",
                "arn:aws:s3:::viewly-uploads-us1/*",
                "arn:aws:s3:::viewly-videos-us1/*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "elastictranscoder:ListJobsByPipeline",
                "cloudfront:GetInvalidation",
                "elastictranscoder:ReadPreset",
                "elastictranscoder:ListPipelines",
                "elastictranscoder:ReadJob",
                "cloudfront:CreateInvalidation",
                "elastictranscoder:ListJobsByStatus",
                "s3:ListObjects",
                "elastictranscoder:ReadPipeline",
                "cloudfront:ListInvalidations",
                "elastictranscoder:CancelJob",
                "elastictranscoder:CreateJob",
                "s3:HeadBucket",
                "elastictranscoder:ListPresets"
            ],
            "Resource": "*"
        }
    ]
}
```

**Manager Account**  
Create `viewly-alpha-manager` API account with the above policy. 

**Environment Variables**

| Variable                | Default |
| ----------------------- | ------- |
| AWS_MANAGER_PUBLIC_KEY  |         |
| AWS_MANAGER_PRIVATE_KEY |         |