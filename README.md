# Requirements
This guide assumes MacOS with HomeBrew.

## Dependencies
Install JS dependencies:
```
npm install -g browserify

cd public
npm i

browserify -r eosio > bundle.js
```


Install Python 3.6. 
```
brew install python3
```


Install Python dependencies:
```
pip install -r requirements.txt
```


Install MongoDB.
```
brew install mongodb
```

Start MongoDB:
```
brew services run mongodb
```

Install PostgreSQL and add a database.
```
CREATE DATABASE testnetone;
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
| MONGO_HOST    | localhost                        |
| MONGO_DBNAME  | ViewlyBeta                       |
| IPFS_API_HOST | localhost                        |
| IPFS_GATEWAY  | http://localhost:8080            |
| UPLOADER_URI  | http://localhost:5005            |
| MAIL_username | postmaster@mg.view.ly            |
| MAIL_PASSWORD | ''                               |