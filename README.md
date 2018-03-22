![](https://i.imgur.com/ekvJd60.png)
# Viewly Alpha
This is the second iteration of the Viewly Alpha (https://alpha.view.ly).

# Running in Docker
To run in Docker, make sure you have latest `docker` and `docker-compose` installed.
You will also need a `docker.dev.env` file, which is not part of this repo, because
it contains API keys to AWS and other resources.

## Clone the repo
```
git clone git@github.com:Viewly/alpha-2.git --recursive
```
Then, add the `docker.dev.env` file into project root.

## Bring up the Docker stack
```
docker-compose -f docker-compose.web.yml -f docker-compose.workers.yml up
```
If there are no errors, you should be able to open Alpha Web app at http://localhost:50001

You will need to install npm/gulp dependencies locally. 
See "Install JS dependencies" below.

Any local file changes will be reflected inside of container automatically, allowing 
for convenient dockerized development.

_Note: To avoid conflicts with locally installed Postgres/Redis/Flask, the
the Dockerized version of the app binds to ports that have `1` added at the end.
For example, the PostgreSQL port binds to host on `54321` rather than `5432`. The latter 
is available within the container only._

_Note: To persist the data, PostgreSQL container will mount its data volume into
`postgres_data` locally. Remove this folder if you wish to start from scratch._


## Re-building the stack from scratch
If you've added extra dependencies or applied changes that require
containers be rebuilt, you can use this command:
```
docker-compose -f docker-compose.web.yml -f docker-compose.workers.yml  build --no-cache
```

Alternatively you can just delete images when bringing _down_ the stack.
```
docker-compose -f docker-compose.web.yml -f docker-compose.workers.yml  down --rmi all
```

# Running Locally
Follow this guide if you wish to run the app bare-metal.

## Dependencies
Package Dependencies:
 - Python 3.6 or higher
 - PostgreSQL 9.6 or 10.x
 - Redis
 - npm
 
Install JS dependencies:
```
cd src/static &&  npm install
cd semantic   &&  gulp build
```

Install Python dependencies:
```
pip install -r requirements.txt
```

## Environment Variables
To run flask commands, you need `FLASK_APP` environment variable set.
```
export FLASK_APP=src/views.py
```

Here is the default environment (you may want to set these yourself):


| Variable      | Default                    |
| ------------- | -------------------------- |
| PRODUCTION    | False                      |
| SECRET_KEY    | not_a_secret               |
| POSTGRES_URI  | postgres://localhost/alpha |
| MAIL_USERNAME | postmaster@mg.view.ly      |
| MAIL_PASSWORD | ''                         |

_Note: This list does not include AWS related variables. Look for those in AWS section
of the readme_.

## Web App
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

| Variable               | Default |
| ---------------------- | ------- |
| S3_UPLOADS_BUCKET      |         |
| S3_UPLOADS_REGION      |         |
| S3_UPLOADER_PUBLIC_KEY |         |
| S3_UPLOADER_SECRET_KEY |         |

 
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

| Variable         | Default |
| ---------------- | ------- |
| S3_VIDEOS_BUCKET |         |
| S3_VIDEOS_REGION |         |


## Elastic Transcoder
Use `ElasticTranscoder.ipynb` to create and configure the ET pipeline. 
Output configuration saved [here](config/elastic_transcoder.prod.json).

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
