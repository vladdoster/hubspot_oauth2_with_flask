[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) [![made-with-python](https://img.shields.io/badge/Made%20with-Python3-1f425f.svg)](https://www.python.org/)

# hubspot_oauth2_with_flask

Basic user login setup for Hubspot Oauth using Requests-OAuthlib.

## Pre-requisites
Have Python 3 installed on system

Fill out .env file in src/ with credentials 

## Steps to run
`git clone https://github.com/vladdoster/hubspot_oauth2_with_flask.git`

`cd hubspot_oauth2_with_flask/`

You should generate your own HTTPS certificates:

Run following to generate https certs for OAuth2 HTTPS requirement

*Note: Linux users install OpenSSL via system package manager and Windows users need to install OpenSSL via a .exe

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

If this helped you, leave a 🌟 so others see it!

