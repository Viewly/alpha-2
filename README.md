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

**IAM Policy**
Create a `s3-viewly-uploader` API user with the following S3 policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::viewly-uploads-test/*"
        }
    ]
}
```
_Replace `viewly-uploads-test` with upload bucket name._
Use this users API credentials as `S3_UPLOADER_PUBLIC_KEY` and `S3_UPLOADER_SECRET_KEY`.

**Environment Variables**

| Variable               | Default                |
| ---------------------- | ---------------------- |
| S3_BUCKET              | s3-viewly-uploader     |
| S3_REGION              | eu-central-1           |
| S3_UPLOADER_PUBLIC_KEY |                        |
| S3_UPLOADER_SECRET_KEY |                        |


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

**Additional Setup**

Use Amazon S3 Console to:
 - Enable _Transfer Acceleration_ on the Upload bucket
 - Add a lifecycle rule to _Clean up incomplete multipart uploads_
 
 
## Videos Bucket Configuration
No additional configuration required at this time.

## S3 Manager Role
The S3 Manager is responsible for:

 - pulling raw video files for evaluation
 - deleting uploads
 - generating metadata files

**IAM Policy**
Create an `s3-viewly-manager` API user with full S3 privileges
on our uploads and videos buckets.

**Environment Variables**

| Variable              | Default                  |
| --------------------- | ------------------------ |
| S3_MANAGER_PUBLIC_KEY |                          |
| S3_MANAGER_SECRET_KEY |                          |


## Elastic Transcoder
Use `ElasticTranscoder.ipynb`. 
Output configuration saved [here](src/conf/elastic_transcoder.prod.json).

## CloudFront
Create a Cloudfront Distribution manually.
Use the `viewly-videos-*` bucket, and set the default TTL to 1 day or more.
Create a CNAME (cdn.view.ly), and issue custom certificate trough ACM.

**Environment Variables**

| Variable | Default             |
| -------- | ------------------- |
| CDN_URL  | https://cdn.view.ly |
