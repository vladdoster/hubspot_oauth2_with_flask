<div align="center">

# Hubspot OAuth2 w/ Flask-OAuth-lib
  
[![Updates](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/shield.svg)](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/) 
[![Python 3](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/python-3-shield.svg)](https://pyup.io/repos/github/vladdoster/hubspot_oauth2_with_flask/) 
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()

### OAuth 2.0 allows a user to authorize your app to work with specific tools in their HubSpot account, designated by the authorization scopes you set.

</div>

<p align="center">
  <img src="https://github.com/vladdoster/hubspot_oauth2_with_flask/blob/master/docs/login.png">
  <img src="https://github.com/vladdoster/hubspot_oauth2_with_flask/blob/master/docs/integrated.png">
</p>

### Stack:

- [Caddy](https://caddyserver.com) [(Because of recent license change)](https://github.com/caddyserver/caddy/issues/2786)
- [Docker](https://www.docker.com/) (Ease of replication)
- [Flask](https://palletsprojects.com/p/flask/) (Don't need any batteries)

**Note:** This app by default only passes `oauth` scope when logging in users. You will need to add the appropriate scope to take advantage of other tools that a user might have. More about that [here](https://developers.hubspot.com/docs/methods/oauth2/initiate-oauth-integration#scopes)

## Pre-requisites
- [Docker Compose](https://docs.docker.com/compose/) 
- [Python 3](https://www.python.org/)

## Steps to run

`git clone https://github.com/vladdoster/hubspot_oauth2_with_flask.git`

`cd hubspot_oauth2_with_flask/`

You should generate your own HTTPS certificates.

`sh ./scripts/generate_certs`

**Note:** Linux users install OpenSSL via system package manager and Windows users need to install OpenSSL via a .exe

If successful, you should have a key.pem and cert.pem file in the certs/ directory

Next, fill out the .env file with appropriate hubspot credentials

### Run app

docker-compose up --build

Direct a browser towards [https://hs-oauth.localhost](https://hs-oauth.localhost)!

### Having issues?

Please open an issue or contact me directly: `mvdoster@gmail.com`

If this in anyway helpful, leave a 🌟 so others see it!

Hiring? Need a developer?
[I love solving problems.](https://vdoster.com)
