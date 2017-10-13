# Requirements
This guide assumes MacOS with HomeBrew.

## Python
Install Python 3.6. 
```
brew install python3
```

Install Project dependencies:
```
cd alpha.viewl.ly
pip install -r requirements.txt
```

## MongoDB

Install MongoDB.
```
brew install mongodb
```

Start MongoDB:
```
brew services run mongodb
```

Pre-Populate the database with data:
- Get the [latest snapshot](https://s3-us-west-2.amazonaws.com/viewly-dev-resource/dump.zip)
- Unzip it.
- run `mongorestore` command


## Run Locally
Run the flask server:
```
export FLASK_APP=src/views.py
flask run --reload --debugger
```
