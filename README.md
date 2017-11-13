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
| S3_BUCKET              | flask-uploader-test              |
| S3_REGION              | eu-central-1                     |
| S3_UPLOADER_PUBLIC_KEY |                                  |
| S3_UPLOADER_SECRET_KEY |                                  |
| S3_MANAGER_PUBLIC_KEY  |                                  |
| S3_MANAGER_SECRET_KEY  |                                  |

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

# Amazon Services

## S3 Uploader Role
This guide assumes the bucket has been created with proper IAM permissions.
This guide uses bucket `flask-uploader-test` in `eu-eastern-1` region as example.

**Environment Variables**

| Variable               | Default                |
| ---------------------- | ---------------------- |
| S3_BUCKET              | flask-uploader-test    |
| S3_REGION              | eu-central-1           |
| S3_UPLOADER_PUBLIC_KEY |                        |
| S3_UPLOADER_SECRET_KEY |                        |

**IAM Policy**
Create a `s3-fine-uploader` group with the following restricted S3 Policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::flask-uploader-test/*"
        }
    ]
}
```
Assign a new user `s3-viewly-uploader` to it. 
Use this users credentials as `S3_UPLOADER_PUBLIC_KEY` and `S3_UPLOADER_SECRET_KEY`.


**Bucket CORS Policy**
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
*TODO: Make `AllowedOrigin` more restrictive.*


## S3 Manager Role
The S3 Manager is responsible for:

 - pulling raw video files for evaluation
 - deleting uploads
 - generating metadata files


**Environment Variables**

| Variable              | Default                  |
| --------------------- | ------------------------ |
| S3_MANAGER_PUBLIC_KEY |                          |
| S3_MANAGER_SECRET_KEY |                          |


**IAM Policy**
The Manager should have full S3 privileges on our `upload` and `transcoder-output` buckets.
