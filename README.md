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


Install PostgreSQL
```
brew install postgresql
```

Start PostgreSQL
```
brew services run postgresql
```

Create Viewly Database
```
CREATE DATABASE viewly_beta;
```

*You can also make the database with flask cli:*
```
flask db-reset
```

## Run Locally
Run the Flask server:
```
export FLASK_APP=src/views.py
flask run --reload --debugger
```


## Environment Variables

| Variable      | Default                          |
| ------------- | -------------------------------- |
| PRODUCTION    | False                            |
| SECRET_KEY    | not_a_secret                     |
| POSTGRES_URI  | postgres://localhost/viewly_beta |
| MAIL_USERNAME | postmaster@mg.view.ly            |
| MAIL_PASSWORD | ''                               |


# Production

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
