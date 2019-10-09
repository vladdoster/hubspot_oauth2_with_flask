#!/usr/bin/env python3
"""
    File name: auth.py
    Author: Vlad Doster
    Maintainer: Vlad Doster
    Date created: 3/18/2019
    Date last modified: 3/26/2019
    Python Version: 3.6
"""
import logging
import os

from flask import Blueprint, app
from flask import session, url_for, flash, render_template, request, redirect
from oauthlib.oauth2 import MissingTokenError, InsecureTransportError
from requests_oauthlib import OAuth2Session

bp = Blueprint("hubspot_oauth", __name__)


@bp.route("/", methods=["GET"])
def index():
    """Index page"""

    # Set session variables for rest of requests

    session["client_id"] = os.getenv("HUBSPOT_CLIENT_ID")
    session["client_secret"] = os.getenv("HUBSPOT_CLIENT_SECRET")
    session["authorization_base_url"] = os.getenv("HUBSPOT_AUTHORIZATION_URL")
    session["token_url"] = os.getenv("HUBSPOT_TOKEN_URL")
    session["scope"] = os.getenv("HUBSPOT_SCOPES")
    session["redirect_uri"] = os.getenv("HUBSPOT_REDIRECT_URI")

    if session["client_id"] == "" or session["client_secret"] == "":
        flash("Check that you set client_id and client_secret in the .env file (ಠ_ಠ)")
    return render_template("index.html")


@bp.route("/login", methods=["GET"])
def initiate_oauth2_authorization():
    """When sending the user to HubSpot's OAuth 2.0 server, first step is to
    create the authorization URL. This will identify your app, and define
    the resources that it's requesting access to on behalf of the user. """

    hubspot = OAuth2Session(
        session["client_id"],
        scope=session["scope"],
        redirect_uri=session["redirect_uri"],
    )
    authorization_url, state = hubspot.authorization_url(
        session["authorization_base_url"]
    )

    # State is used to prevent CSRF, keep this for later.
    session["oauth_state"] = state
    logging.debug(authorization_url)
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.
@bp.route("/callback", methods=["GET"])
def callback():
    """When the user has completed the consent prompt from step 3, the OAuth
    2.0 server sends a GET request to the redirect URI specified in your
    authentication URL. If there are no issues and the user approves the
    access request, the request to the redirect URI will have a code query
    parameter attached when it's returned. If the user doesn't grant access,
    no request will be sent. """

    code = request.values.get("code")
    hubspot = OAuth2Session(session["client_id"], state=session["oauth_state"])

    try:
        https_url = request.url
        i = request.url.find(":")
        https_request_url = https_url[:i] + "s" + https_url[i:]
        token = hubspot.fetch_token(
            session["token_url"],
            method="POST",
            client_secret=session["client_secret"],
            authorization_response=https_request_url,
            body=f"""grant_type=authorization_code&client_id={session["client_id"]}&client_secret={session["client_secret"]}&redirect_uri={session["redirect_uri"]}&code={code}""",
        )

        session["oauth_token"] = token
    except InsecureTransportError as e:
        logging.error(
            f"Something went wrong in the callback due to HTTPS\n" f"Error: {e}"
        )
        flash("Callback: error due to HTTPS")
    except Exception as e:
        logging.error(f"Something went wrong in the callback\n" f"Error: {e}")
        flash("Callback: error due to unknown ¯\(°_o)/¯")
    return redirect(
        url_for(endpoint=".get_token_info", _scheme="https", _external=True)
    )


@bp.route("/refresh_token", methods=["GET"])
def refresh_token():
    """Use a previously obtained refresh token to generate a new access
    token.  Access tokens expire after 6 hours, so if you need offline
    access to data in HubSpot, you'll need to store the refresh token you
    get when initiating your OAuth integration, and use that to generate a
    new access token once the initial access token expires. """
    logging.info(session["oauth_token"].get("refresh_token"))
    try:
        hubspot = OAuth2Session(session["client_id"], state=session["oauth_state"])
        new_token = hubspot.refresh_token(
            session["token_url"],
            body=f"""grant_type=refresh_token&client_id={session["client_id"]}&client_secret={session["client_secret"]}&refresh_token={session["oauth_token"].get('refresh_token')}""",
        )
        session["oauth_token"] = new_token
        flash("Token refreshed successfully! (ʘ‿ʘ)")
    except MissingTokenError as e:
        flash("Try logging in to access this resource! ¯\(°_o)/¯\n" f"Errror: {e}")
    except Exception as e:
        logging.error(f"Error refreshing token! {e}")
    return redirect(url_for(endpoint=".index", _scheme="https", _external=True))


@bp.route("/token_info", methods=["GET"])
def get_token_info():
    """This can be used to get the email address of the HubSpot user that
    the token was created for, as well as the Hub ID that the token is
    associated with. """
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{session["oauth_token"].get("refresh_token")}'
        hubspot = OAuth2Session(session["client_id"], state=session["oauth_state"])
        data = hubspot.get(token_info_url)
        return render_template("index.html", context=data.json())
    else:
        flash(
            "Try logging in to access this resource!\n"
            "Ran into an error retrieivng token in /get_token_info"
        )
        return redirect(url_for(endpoint=".index", _scheme="https", _external=True))


@bp.route("/delete_refresh_token", methods=["GET"])
def delete_refresh_token():
    """Deletes a refresh token. You can use this to delete your refresh
    token if a user uninstalls your app. """
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{session["oauth_token"].get("refresh_token")}'
        hubspot = OAuth2Session(session["client_id"], state=session["oauth_state"])
        data = hubspot.delete(token_info_url)
        if data.status_code == 204:
            flash("Refresh token successfully deleted!")
            session["oauth_token"] = None
            session["oauth_state"] = None
    else:
        flash("Try logging in to access this resource!")
    return redirect(url_for(endpoint=".index", _scheme="https", _external=True))
