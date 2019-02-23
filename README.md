# hubspot_oauth2_with_flask

Requirements:
- Requests-OAuthlib
- Flask login
- Flask Alchemy
- Hubspot Oauth

Finished product:
Basic user login setup using hubspot Oauth.

## Pre-requisites
Have Python 3 installed on system

## Steps to run
`git clone https://github.com/vladdoster/hubspot_oauth2_with_flask.git`

`cd hubspot_oauth2_with_flask/`

`python3 -m venv venv/`

`source venv/bin/activate`

You should see a (venv) infront of your current shell line to indicate it is active

`pip3 install -r requirements.txt`

`export FLASK_APP=src/app.py`

`flask run`

Direct a browser towards `localhost:5000` and it should do the rest!
