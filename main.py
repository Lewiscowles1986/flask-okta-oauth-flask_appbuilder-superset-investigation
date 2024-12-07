from os import getenv
from flask import Flask, redirect, url_for, session, jsonify
from flask_appbuilder import AppBuilder, SQLA
from authlib.integrations.flask_client import OAuth
from flask_appbuilder.security.manager import AUTH_OAUTH

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY", "your_secret_key_here")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db" # can use in-memory or any SQLAlchemy URL DSN, but I like this for simplicity
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Okta OAuth configuration
OKTA_CLIENT_ID = getenv("OKTA_CLIENT_ID")
OKTA_CLIENT_SECRET = getenv("OKTA_CLIENT_SECRET")
OKTA_ISSUER_URL = getenv("OKTA_ISSUER_URL") # "https://dev-83615971.okta.com"  # Replace with your Okta Issuer URL
OKTA_OAUTH_BASE_URL = f"{OKTA_ISSUER_URL}/oauth2/v1"

# AppBuilder Security Config
app.config["AUTH_TYPE"] = AUTH_OAUTH
app.config["AUTH_USER_REGISTRATION"] = True  # Allow automatic user registration
app.config["AUTH_USER_REGISTRATION_ROLE"] = "Public"  # Default role, can change to "Admin" to generate first user... Otherwise make a mapping table
app.config["SQLALCHEMY_ECHO"] = True
app.config["OAUTH_PROVIDERS"] = [
    {
        "name": "okta",
        "icon": "fa-circle-o",  # Icon for the login button
        "token_key": "access_token",  # Field in OAuth token for access
        "remote_app": {
            "client_id": OKTA_CLIENT_ID,
            "client_secret": OKTA_CLIENT_SECRET,
            "api_base_url": f"{OKTA_ISSUER_URL}/oauth2/v1",
            "server_metadata_url": f"{OKTA_ISSUER_URL}/.well-known/openid-configuration",
            "client_kwargs": {"scope": "openid profile email groups", "token_endpoint_auth_method": "client_secret_post"},
            "access_token_url": f"{OKTA_OAUTH_BASE_URL}/token",
            "authorize_url": f"{OKTA_OAUTH_BASE_URL}/authorize",
        },
    }
]
app.config["AUTH_ROLES_SYNC_AT_LOGIN"] = True

# Initialize database and OAuth
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)
oauth = OAuth(app)

# Configure the Okta OAuth integration
okta = oauth.register(
    name="okta",
    client_id=OKTA_CLIENT_ID,
    client_secret=OKTA_CLIENT_SECRET,
    api_base_url=f"{OKTA_ISSUER_URL}/oauth2/v1",
    server_metadata_url=f"{OKTA_ISSUER_URL}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email groups"},
    access_token_url=f"{OKTA_OAUTH_BASE_URL}/token",
    authorize_url=f"{OKTA_OAUTH_BASE_URL}/authorize",
)

# Home page route
@app.route("/")
def home():
    return redirect(url_for("login"))

# Login route
@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return okta.authorize_redirect(redirect_uri)

# Callback route for Okta
@app.route("/authorize")
def authorize():
    token = okta.authorize_access_token()
    user_info = okta.parse_id_token(token)
    session["user"] = user_info
    return redirect(url_for("profile"))

# Profile page
@app.route("/profile")
def profile():
    user = session.get("user")
    if user:
        return jsonify(user)
    return redirect(url_for("login"))

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Create DB
if __name__ == "__main__":
    db.create_all()
    if any([
        not OKTA_CLIENT_ID,
        not OKTA_CLIENT_SECRET,
        not OKTA_ISSUER_URL
    ]):
        print("Yeah, you have to provide the Okta creds to use this...")
        exit(1)
    app.run(debug=True, port=8088)
