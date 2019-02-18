import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, url_for, render_template, flash
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized, oauth_error
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

# Load env variables from .env
load_dotenv()
# setup Flask application
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'secret'
blueprint = OAuth2ConsumerBlueprint(
    "hubspot", __name__,
    scope=['oauth', ],
    client_id=str(os.getenv('HUBSPOT_CLIENT_ID')),
    client_secret=str(os.getenv('HUBSPOT_CLIENT_SECRET')),
    token_url="https://api.hubapi.com/oauth/v1/token",
    redirect_uri='https://musings.vdoster.com',
    authorization_url='https://app.hubspot.com/oauth/authorize',
)

app.register_blueprint(blueprint, url_prefix="/login")

# setup database models
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hubspot_oauth.db'
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256))


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


# setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'hubspot.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# setup SQLAlchemy backend
blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)


# create/Login Local user on Succesful OAuth Login
@app.route("/callback")
@oauth_authorized.connect_via(sender=blueprint)
def hubspot_logged_in(blueprint, token):
    print(f"Hubspot logged in!")
    if not token:
        print("TOKEN MISSING")
        return False

    resp = blueprint.session.get("/user")
    if not resp.ok:
        print("Response NOT OK")
        return False

    hubspot_info = resp.json()
    hubspot_user_id = str(hubspot_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=hubspot_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            user_id=hubspot_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with Hubspot.")
    else:
        # Create a new local user account for this user
        user = User(
            # Remember that 'email' can be None, if the user declines
            email=hubspot_info["email"],
            name=hubspot_info["name"],
        )
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in with hubspot")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on Oauth provider error
@oauth_error.connect_via(blueprint)
def hubspot_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} url={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


@app.route("/login")
@login_required
def login():
    flash("You have logged in")
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


# hook up extensions to app
db.init_app(app)
login_manager.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()
        print("Database tables created")
    env_path = Path('.') / '.env'
    load_dotenv(find_dotenv())
    app.run(debug=True, host='127.0.0.1', port=5000,
            ssl_context='adhoc')
