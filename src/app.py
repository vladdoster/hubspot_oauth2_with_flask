#!/usr/bin/env python

"""
    File name: app.py
    Author: Vlad Doster
    Maintainer: Vlad Doster
    Date created: 3/18/2019
    Date last modified: 3/18/2019
    Python Version: 3.6
"""

# Standard lib
import logging
import os

from OpenSSL import SSL
# 3rd Party libs
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for, flash, render_template
from requests_oauthlib import OAuth2Session

# Set logging to debug
logging.basicConfig(level=logging.DEBUG)

# Load env variables from .env
load_dotenv()

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('key.pem')
context.use_certificate_file('cert.pem')

app = Flask(__name__)
app.secret_key = os.urandom(24).__str__()

# This information is obtained upon registration of a new Hubspot OAuth
# application here: https://github.com/settings/applications/new
client_id = os.getenv('HUBSPOT_CLIENT_ID')
client_secret = os.getenv('HUBSPOT_CLIENT_SECRET')
authorization_base_url = 'https://app.hubspot.com/oauth/authorize'
token_url = 'https://api.hubapi.com/oauth/v1/token'
scope = ["contacts", "oauth"]
redirect_uri = 'https://127.0.0.1:5000/callback'

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/login", methods=["GET"])
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    hubspot = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = hubspot.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.
@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    code = request.values.get('code')
    hubspot = OAuth2Session(client_id, state=session['oauth_state'])
    token = hubspot.fetch_token(token_url, method='POST',
                                client_secret=client_secret,
                                authorization_response=request.url,
                                body="grant_type=authorization_code&client_id=" + client_id + "&client_secret=" + client_secret + "&redirect_uri=" + redirect_uri + "&code=" + code)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /token_info.
    session['oauth_token'] = token
    return redirect(url_for('.get_token_info'))


@app.route("/refresh_token", methods=['GET'])
def refresh_token():
    # Check if we have a token to refresh
    if session.get('oauth_token'):
        hubspot = OAuth2Session(client_id, state=session['oauth_state'])
        # Request a new token
        new_token = hubspot.refresh_token(token_url,
                                          body="grant_type=refresh_token&client_id=" + client_id + "&client_secret=" + client_secret + "&refresh_token=" +
                                               session['oauth_token'].get('refresh_token'))
        # Set new token
        session['oauth_token'] = new_token
        # Convey success to user
        flash("Token refreshed successfully!")
        return redirect(url_for('.index'))
    # If no token present, we redirect to index
    else:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))


@app.route("/token_info", methods=['GET'])
def get_token_info():
    # Check to see if there is a token to derive info from
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{session["oauth_token"].get("refresh_token")}'
        hubspot = OAuth2Session(client_id, state=session['oauth_state'])
        data = hubspot.get(token_info_url)
        return render_template('index.html', context=data.json())
    # If no token present, we redirect to index
    else:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))


#
# @app.route("/contacts", methods=["GET"])
# def contacts():
#     """Fetching a protected resource using an OAuth 2 token.
#     """
#     hubspot = OAuth2Session(client_id, token=session['oauth_token'])
#     return jsonify(hubspot.get('https://api.hubapi.com/contacts/v1/lists/all/contacts/all').json())


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    session.init_app(app)
    # app.run(debug=True, ssl_context='adhoc')
    app.run(debug=True, ssl_context=context)
