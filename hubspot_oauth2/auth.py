#!/usr/bin/env python
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

from flask import Blueprint
from flask import request, redirect, session, url_for, flash, render_template, g
from oauthlib.oauth2 import MissingTokenError
from requests_oauthlib import OAuth2Session

bp = Blueprint("hubspot_oauth", __name__)


@bp.route("/", methods=["GET"])
def index():
    """Index page"""
    return render_template("index.html")


@bp.route("/login", methods=["GET"])
def initiate_oauth2_authorization():
    """When sending the user to HubSpot's OAuth 2.0 server, first step is to
    create the authorization URL. This will identify your app, and define
    the resources that it's requesting access to on behalf of the user. """

    session["client_id"] = os.getenv("HUBSPOT_CLIENT_ID")
    session["client_secret"] = os.getenv("HUBSPOT_CLIENT_SECRET")
    session["authorization_base_url"] = "https://app.hubspot.com/oauth/authorize"
    session["token_url"] = "https://api.hubapi.com/oauth/v1/token"
    session["scope"] = ["oauth", "contacts"]
    session["redirect_uri"] = "https://localhost:5000/callback"

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
    hubspot = OAuth2Session(session["client_id"], state=session["oauth_test"])
    token = hubspot.fetch_token(
        session["token_url"],
        method="POST",
        client_secret=session["client_secret"],
        authorization_response=request.url,
        body=f"""grant_type=authorization_code
                                        &client_id={session["client_id"]}
                                        &client_secret={session["client_secret"]}
                                        &redirect_uri={session["redirect_uri"]}&code={code}""",
    )

    session["oauth_token"] = token
    return redirect(url_for(".get_token_info"))


@bp.route("/refresh_token", methods=["GET"])
def refresh_token():
    """Use a previously obtained refresh token to generate a new access
    token.  Access tokens expire after 6 hours, so if you need offline
    access to data in HubSpot, you'll need to store the refresh token you
    get when initiating your OAuth integration, and use that to generate a
    new access token once the initial access token expires. """
    logging.info(g.oauth_token.get("refresh_token"))
    try:
        hubspot = OAuth2Session(g.client_id, state=g.oauth_state)
        new_token = hubspot.refresh_token(
            g.token_url,
            body=f"""grant_type=refresh_token&client_id={g.client_id}&client_secret={g.client_secret}&refresh_token={
            g.oauth_token.get('refresh_token')}""",
        )
        g.oauth_token = new_token
        flash("Token refreshed successfully!")
        return redirect(url_for(".index"))
    except MissingTokenError:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))
    except Exception as e:
        logging.error(f"Error refreshing token! {e}")
        return redirect(url_for(".index"))


@bp.route("/token_info", methods=["GET"])
def get_token_info():
    """This can be used to get the email address of the HubSpot user that
    the token was created for, as well as the Hub ID that the token is
    associated with. """
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{session["oauth_token"].get("refresh_token")}'
        hubspot = OAuth2Session(g.client_id, state=session["oauth_state"])
        data = hubspot.get(token_info_url)
        return render_template("index.html", context=data.json())
    else:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))


@bp.route("/delete_refresh_token", methods=["GET"])
def delete_refresh_token():
    """Deletes a refresh token. You can use this to delete your refresh
    token if a user uninstalls your app. """
    if session.get("oauth_token"):
        token_info_url = f'https://api.hubapi.com/oauth/v1/refresh-tokens/{g.oauth_token.get("refresh_token")} '
        hubspot = OAuth2Session(g.client_id, state=g.oauth_state)
        data = hubspot.delete(token_info_url)
        if data.status_code == 204:
            flash("Refresh token successfully deleted!")
            g.oauth_token = None
            g.oauth_state = None
            return redirect(url_for(".index"))
    else:
        flash("Try logging in to access this resource!")
        return redirect(url_for(".index"))
