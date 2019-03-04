from dotenv import load_dotenv
from flask import Blueprint
import os

from flask import request, redirect, session, url_for, flash
from flask.json import jsonify
from flask_login import login_required
from requests_oauthlib import OAuth2Session

hubspot_oauth = Blueprint('hubspot_oauth', __name__, template_folder='templates', url_prefix='/hubspot')

# This information is obtained upon registration of a new GitHub OAuth
# application here: https://github.com/settings/applications/new
# Load env variables from .env
load_dotenv()

client_id = os.getenv('HUBSPOT_CLIENT_ID')
client_secret = os.getenv('HUBSPOT_CLIENT_SECRET')
authorization_base_url = 'https://app.hubspot.com/oauth/authorize'
token_url = 'https://api.hubapi.com/oauth/v1/token'
scope = ["contacts", "oauth"]
redirect_uri = 'https://127.0.0.1:5000/hubspot/callback'


@hubspot_oauth.route("/", methods=["GET"])
@login_required
def hubspot_login():
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

@hubspot_oauth.route("/callback", methods=["GET"])
@login_required
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
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.get_token_info'))


@hubspot_oauth.route("/token_info", methods=['GET'])
@login_required
def get_token_info():
    hubspot = OAuth2Session(client_id, token=session['oauth_token'])
    # data = hubspot.get('https://api.hubapi.com/oauth/v1/refresh-tokens/:token').json()
    flash(session['oauth_token'])
    return jsonify(message=session['oauth_token'])


@hubspot_oauth.route("/contacts", methods=["GET"])
@login_required
def contacts():
    """Fetching a protected resource using an OAuth 2 token.
    """
    hubspot = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(hubspot.get('https://api.hubapi.com/contacts/v1/lists/all/contacts/all').json())
