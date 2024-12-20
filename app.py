import flask_login
import bleach

from flask import Flask, request, redirect, url_for, g
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_talisman import Talisman

import core.config as config
config.abspath = __file__

db      = SQLAlchemy()
migrate = Migrate()

from core.database import database
from core.users import Users
from core.tickets import Tickets
from core.comments import Comments
from core.auth import Auth
from core.failed_logins import Failed_Logins
from core.mailer import Mailer
from core.init import Init

from models import User, Ticket, Comment, Failed_Login, Base

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.portal_routes import portal_bp

Init().run()

app            = Flask( __name__ )
app.secret_key = config.secret_key

app.config['SQLALCHEMY_DATABASE_URI']        = config.db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Intialise Flask Migration
db.init_app( app )
migrate.init_app( app, db )

# Login manager compatability
login_manager  = flask_login.LoginManager()
login_manager.init_app( app )

# CSRF protection compatability
csrf = CSRFProtect( app )

# Define a CSP policy to allow Font Awesome
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'", 'https://code.jquery.com', "'unsafe-inline'"],  # Scripts
    'style-src': ["'self'", 'https://cdnjs.cloudflare.com', "'unsafe-inline'"],  # Styles
    'font-src': ["'self'", 'https://cdnjs.cloudflare.com'],   # Fonts
    'img-src': ["'self'", "data:"],  # Images
}

if( config.environment != "testing" ):
    # Add Talisman for security headers
    Talisman( app, content_security_policy=csp, force_https=False )

# Loading the currently logged in user
@login_manager.user_loader
def load_user( user_id ):
    return Users.get_user_by( 'ID', user_id )

# Unauthorized handler to redirect to login page
@login_manager.unauthorized_handler
def handle_needs_login():
    return redirect( url_for( 'auth.login' ) )

@app.teardown_appcontext
def shutdown_session( exception = None ):
    database.close_session()

# Register Blueprints
app.register_blueprint( auth_bp )
app.register_blueprint( portal_bp )

# Middleware for production environment
if config.environment == "production":

    # Enforce HTTPS on all requests
    @app.before_request
    def enforce_https():
        if not request.is_secure:
            url = request.url.replace( "http://", "https://", 1 )
            return redirect( url, code=301 )
    
    # Redirect the alias to the main domain
    @app.before_request
    def redirect_alias():
        if request.host == "qa-software-engineering-devops-d38aa33c0701.herokuapp.com":
            return redirect( "https://assignment.davidhedley.com" + request.path, code=301 )

@app.before_request
def enforce_two_factor():

    endpoint = request.endpoint

    if endpoint is None or endpoint.startswith('auth.') or endpoint == 'static':
        return
    
    user     = flask_login.current_user

    if( not user or user.is_anonymous ):
        return
    
    # If the user has not verified their email, redirect to the email verification page
    if( user.email_verified == False ):

        return redirect( url_for( 'auth.verify_email' ) )
    
    # If the user has not enabled two factor authentication, redirect to the 2FA setup page
    if ( user.two_factor_auth == False and user.two_factor_enabled == False ):
        
        return redirect( url_for( 'auth.login_setup_2fa' ) )
    
    # If the user has not passed two factor authentication, redirect to the 2FA page
    elif( user.two_factor_auth == False and user.two_factor_enabled == True ):

        return redirect( url_for( 'auth.login_2fa' ) )

if __name__ == '__main__':
    app.run()