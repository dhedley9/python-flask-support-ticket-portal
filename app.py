from models import User, Ticket, Comment, Failed_Login, Base
from core.database import database

# Create the database tables
database.create_tables( Base )

import flask_login
import bleach

from flask import Flask, request, redirect, url_for, g
from flask_wtf.csrf import CSRFProtect

import core.config as config
config.abspath = __file__

from core.database import Database
from core.users import Users
from core.tickets import Tickets
from core.comments import Comments
from core.auth import Auth
from core.failed_logins import Failed_Logins
from core.mailer import Mailer

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.portal_routes import portal_bp

# Create the default admin user, if it doesn't exist
if Users.admin_user_exists() == False:
    admin_id = Users.create_user( config.default_admin_email, config.default_admin_password, 'administrator' )    
    Users.update_user( admin_id, { 'email_verified': 1 } )

app            = Flask( __name__ )
app.secret_key = config.secret_key

# Login manager compatability
login_manager  = flask_login.LoginManager()
login_manager.init_app( app )

# CSRF protection compatability
csrf = CSRFProtect( app )

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