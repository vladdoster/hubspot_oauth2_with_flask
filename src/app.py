import logging
import os
from dotenv import load_dotenv
from flask import Flask, session
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from OpenSSL import SSL

from src.config import Config
from .hubspot_oauth import hubspot_oauth

# Set logging to debug
logging.basicConfig(level=logging.DEBUG)

# Set HTTPS
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file("key.pem")
context.use_certificate_file("cert.pem")

# Instantiate app
app = Flask(__name__)
app.config.from_object(Config)


# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'

from src.authentication import auth
# Blueprints
app.register_blueprint(hubspot_oauth)
app.register_blueprint(auth)

if __name__ == "__main__":
    session.init_app(app)
    app.run(debug=True, ssl_context=context)
