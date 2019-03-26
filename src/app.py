#!/usr/bin/env python
"""
    File name: app.py
    Author: Vlad Doster
    Maintainer: Vlad Doster
    Date created: 3/18/2019
    Date last modified: 3/26/2019
    Python Version: 3.6
"""

# Standard lib
import logging
import os

# 3rd Party libs
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for, flash, render_template
from oauthlib.oauth2 import MissingTokenError
from requests_oauthlib import OAuth2Session

# Set logging to debug
logging.basicConfig(level=logging.DEBUG)

# Load env variables from .env
load_dotenv()

# Instantiate app
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
    """Index page"""
    return render_template('index.html')


@app.route("/login", methods=["GET"])
def initiate_oauth2_authorization():
    """When sending the user to HubSpot's OAuth 2.0 server, first step is to create the authorization URL. This will
    identify your app, and define the resources that it's requesting access to on behalf of the user. """
    hubspot = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = hubspot.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.
@app.route("/callback", methods=["GET"])
def callback():
    """When the user has completed the consent prompt from step 3, the OAuth 2.0 server sends a GET request to the
    redirect URI specified in your authentication URL. If there are no issues and the user approves the access
    request, the request to the redirect URI will have a code query parameter attached when it's returned. If the
    user doesn't grant access, no request will be sent."""

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
    """Use a previously obtained refresh token to generate a new access token.  Access tokens expire after 6 hours,
    so if you need offline access to data in HubSpot, you'll need to store the refresh token you get when initiating
    your OAuth integration, and use that to generate a new access token once the initial access token expires. """
    logging.info(session['oauth_token'].get("refresh_token"))
    try:
        hubspot = OAuth2Session(client_id, state=session['oauth_state'])
        new_token = hubspot.refresh_token(token_url,
                                          body=f"""grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={
                                          session['oauth_token'].get('refresh_token')}""")
        session['oauth_token'] = new_token
        # Convey success to user
        flash("Token refreshed successfully!")
        return redirect(url_for('.index'))
    except MissingTokenError as e:
        flash("Try logging in to access this resource!")
        return redirect(url_for('.index'))
    except Exception as e:
        logging.error(f"Error refreshing token! {e}")
        return redirect(url_for('.index'))

@app.route("/token_info", methods=['GET'])
def get_token_info():
    """This can be used to get the email address of the HubSpot user that the token was created for, as well as the
    Hub ID that the token is associated with. """
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{session["oauth_token"].get("refresh_token")}'
        hubspot = OAuth2Session(client_id, state=session['oauth_state'])
        data = hubspot.get(token_info_url)
        return render_template('index.html', context=data.json())
    # If no token present, we redirect to index
    else:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))


@app.route("/delete_refresh_token", methods=['GET'])
def delete_refresh_token():
    """Deletes a refresh token. You can use this to delete your refresh token if a user uninstalls your app."""
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{session["oauth_token"].get("refresh_token")}'
        hubspot = OAuth2Session(client_id, state=session['oauth_state'])
        data = hubspot.delete(token_info_url)
        if data.status_code == 204:
            flash("Refresh token successfully deleted!")
            session['oauth_token'] = None
            session['oauth_state'] = None
            return redirect(url_for(".index"))
    # If no token present, we redirect to index
    else:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))


if __name__ == "__main__":
    session.init_app(app)
    app.run(debug=True, ssl_context=context)
