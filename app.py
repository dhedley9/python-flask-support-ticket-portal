import flask_login
import bleach

from flask import Flask, request, redirect, url_for, render_template, flash, session
from flask_wtf.csrf import CSRFProtect

import core.config as config
config.abspath = __file__

from core.database import Database
from core.users import Users
from core.user import User
from core.tickets import Tickets
from core.comments import Comments
from core.auth import Auth
from core.failed_logins import Failed_Logins

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.portal_routes import portal_bp

# Create the database tables and the default admin user, if they don't exist
Database.create_default_tables()
count = Database.get_var( 'SELECT count( ID ) FROM users WHERE role = "administrator" LIMIT 1' )
count = int( count )

if count == 0:
    Users.create_user( config.default_admin_email, config.default_admin_password, 'administrator' )

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

@app.before_request
def enforce_two_factor():

    endpoint = request.endpoint
    user     = flask_login.current_user

    if( not user or user.is_anonymous ):
        return
    
    if endpoint is None or endpoint in [ 'auth.logout', 'auth.login', 'auth.login_setup_2fa', 'auth.login_setup_2fa_confirm', 'auth.login_2fa', 'static']:
        return
        
    if ( user.two_factor_auth == False and user.two_factor_enabled == False ):
        
        return redirect( url_for( 'auth.login_setup_2fa' ) )
    
    elif( user.two_factor_auth == False and user.two_factor_enabled == True ):

        return redirect( url_for( 'auth.login_2fa' ) )

# Register Blueprints
app.register_blueprint( auth_bp )
app.register_blueprint( portal_bp )

if __name__ == '__main__':
    app.run()