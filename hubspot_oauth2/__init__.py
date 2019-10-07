import logging
import os

from dotenv import load_dotenv
from flask import Flask, request, redirect, app
from flask_session import Session

sess = Session()

load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = os.urandom(24).__str__()

    sess.init_app(app)

    with app.app_context():
        from hubspot_oauth2 import auth
        app.register_blueprint(auth.bp)
        return app
