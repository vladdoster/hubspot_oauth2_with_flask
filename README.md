[![HitCount](http://hits.dwyl.io/vladdoster/hubspot_oauth2_with_flask.svg)](http://hits.dwyl.io/vladdoster/hubspot_oauth2_with_flask) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) [![made-with-python](https://img.shields.io/badge/Made%20with-Python3-1f425f.svg)](https://www.python.org/)



# hubspot_oauth2_with_flask

Basic user login setup for Hubspot Oauth using Requests-OAuthlib.

## Pre-requisites
Have Python 3 installed on system

Fill out .env file in src/ with credentials 

## Steps to run
`git clone https://github.com/vladdoster/hubspot_oauth2_with_flask.git`

`cd hubspot_oauth2_with_flask/`

Generate https certs to appease OAuth2 HTTPS requirement

`openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365`

`python3 -m venv venv/`

`source venv/bin/activate`

You should see a (venv) infront of your current shell line to indicate it is active

`pip3 install -r requirements.txt`

If on Unix system:

`export FLASK_APP=src/app.py`

If on Windows:

`set FLASK_APP=src/app.py`

Initialize DB

`flask db init`

Create migrations

`flask db migrate`

Apply migrations to db

`flask db upgrade`

Run app

`flask run --cert cert.pem --key key.pem`

Direct a browser towards `https://127.0.0.1:5000` and it should do the rest!
