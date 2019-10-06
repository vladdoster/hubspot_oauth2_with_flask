<div align="center">

# Hubspot OAuth2 w/ Flask-OAuth-lib
  
[![Updates](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/shield.svg)](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/) 
[![Python 3](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/python-3-shield.svg)](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/) 
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()

OAuth 2.0 allows a user to authorize your app to work with specific tools in their HubSpot account, designated by the authorization scopes you set.

</div>

<p align="center">
  <img src="https://drive.google.com/uc?id=1nYV6UGshwYHywJVKEtgFdHQzBYWNZYJr">
</p>

<p align="center">
  <img src="https://drive.google.com/uc?id=1n-uED-nfPxFECQLpn2uApsAo-7U84q2T">
</p>

**Note:** This app by default only passes `oauth` scope when logging in users. You will need to add the appropriate scope to take advantage of other tools that a user might have. More about that [here](https://developers.hubspot.com/docs/methods/oauth2/initiate-oauth-integration#scopes)

## Pre-requisites
Have Python 3 installed on system

Fill out .env file in src/ with credentials 

## Steps to run
`git clone https://github.com/vladdoster/hubspot_oauth2_with_flask.git`

`cd hubspot_oauth2_with_flask/`

You should generate your own HTTPS certificates:

Run following to generate https certs for OAuth2 HTTPS requirement

**Note:** Linux users install OpenSSL via system package manager and Windows users need to install OpenSSL via a .exe

`openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365`

If successful, you should have a key.pem and cert.pem file in root directory

Next, fill out the .env file with appropriate hubspot credentials

Then, create a virtual env and activate it

`python3 -m venv venv/`

`source venv/bin/activate`

You should see a (venv) infront of your current shell line to indicate it is active

ex. `(venv)user@ubuntu$`

Now install the project requirements

`pip install -r requirements.txt`

If on Unix system:

`export FLASK_APP=src/app.py`

If on Windows:

`set FLASK_APP=src/app.py`

Run app

`flask run --cert cert.pem --key key.pem`

Direct a browser towards `https://127.0.0.1:5000`!

### Having issues?

Please open an issue or contact me directly: `mvdoster@gmail.com`

If this in anyway helpful, leave a 🌟 so others see it!

Hiring? Need a developer?
I love solving problems.
