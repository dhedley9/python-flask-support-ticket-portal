from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from datetime import datetime

import flask_login
import bleach

from core.users import Users
from core.auth import Auth
from core.failed_logins import Failed_Logins
from core.mailer import Mailer

import core.config as config

auth_bp = Blueprint( 'auth', __name__ )

# ROUTE - /login
@auth_bp.route( '/login', methods=['GET', 'POST'] )
def login():

    """
    Returns and handles the login form
    """

    client_ip = request.remote_addr

    if Failed_Logins.is_ip_locked( client_ip ):
        return render_template( 'auth/locked.html' ), 403

    # Handle the submission of the login form
    if request.method == 'POST':

        logger    = Users.get_logger()

        # Get the posted form info
        email     = request.form.get( 'email' )
        password  = request.form.get( 'password' )

        # Sanitize
        email    = bleach.clean( email )
        password = bleach.clean( password )

        # Try to retrieve the user by their email address
        user     = Users.get_user_by( 'email', email )

        # If there is a user and the (hashed) password match, log the user in
        if user and Users.check_password( user, password ):

            flask_login.login_user( user )

            # Record and log the login
            Users.track_login( user.ID )
            Failed_Logins.clear_failed_logins( client_ip )

            logger.info(f"User '{user.ID}' logged in from IP address {client_ip}.")

            # Redirect to the homepage
            return redirect( url_for( 'portal.index' ) )
        
        flash( 'Invalid Email Address or Password', 'error' )
        
        if( user ) :
            logger.info(f"User '{user.ID}' FAILED login from IP address {client_ip}. Reason: Invalid password")
        else:
            logger.info(f"User '0' FAILED login from IP address {client_ip}. Reason: Invalid email. Email {email}")
        
        Failed_Logins.log_failed_login( client_ip )

        return render_template( 'auth/login.html', email = email )

    return render_template( 'auth/login.html' )

# ROUTE - /logout
@auth_bp.route( '/logout' )
def logout():

    """
    Simple route logs out the current user
    """

    session.pop( 'two_factor_auth', None )
    flask_login.logout_user()
    flash( 'You have been logged out', 'success' )

    return redirect( url_for( 'auth.login' ) )

# ROUTE - /register
@auth_bp.route( '/register' )
def register():

    """
    Simple route which outputs the user registration form
    """

    return render_template( 'auth/register.html' )

# ROUTE - /login/setup-2fa
@auth_bp.route( '/login/setup-2fa', methods=['GET', 'POST'] )
@flask_login.login_required
def login_setup_2fa():

    """
    Returns and handles the 2FA setup form
    """

    user = flask_login.current_user

    secret = Auth.create_secret()
    uri    = Auth.get_2fa_link( secret, user.email, 'TestSite' )
    qr     = Auth.get_qr_code( uri )
    image  = Auth.get_qr_code_img( qr )

    Users.update_user( user.ID, { 'secret': secret } )

    confirm_url = url_for( 'auth.login_setup_2fa_confirm' )

    return render_template( 'auth/login-setup-2fa.html', qrcode_image = image, secret = secret, confirm_url = confirm_url )

# ROUTE - /login/setup-2fa-confirm
@auth_bp.route( '/login/setup-2fa-confirm', methods=['GET', 'POST'] )
@flask_login.login_required
def login_setup_2fa_confirm():
    
    """
    Handles the 2FA setup confirmation form
    """

    user = flask_login.current_user

    # Handle the submission of the 2FA setup confirmation form
    if request.method == 'POST':

        # Get the code digits
        digit_1 = request.form.get( 'two_factor_code_digit_1' )
        digit_2 = request.form.get( 'two_factor_code_digit_2' )
        digit_3 = request.form.get( 'two_factor_code_digit_3' )
        digit_4 = request.form.get( 'two_factor_code_digit_4' )
        digit_5 = request.form.get( 'two_factor_code_digit_5' )
        digit_6 = request.form.get( 'two_factor_code_digit_6' )

        # Concatenate the digits to form the code
        code = f"{digit_1}{digit_2}{digit_3}{digit_4}{digit_5}{digit_6}"

        # Check the code is valid
        if not Auth.verify_2fa_code( code, user.secret ):

            flash( 'That code didn\'t work. Maybe it expired?', 'error' )

            return render_template( 'auth/login-setup-confirm-2fa.html' )

        user.passed_two_factor_auth()

        Users.update_user( user.ID, { 'two_factor_enabled': 1 } )

        # Redirect to the homepage
        return redirect( url_for( 'portal.index' ) )

    return render_template( 'auth/login-setup-confirm-2fa.html' )

# ROUTE - /login/2fa
@auth_bp.route( '/login/2fa', methods=['GET', 'POST'] )
@flask_login.login_required
def login_2fa():
    
    """
    Returns and handles the 2FA form
    """

    user = flask_login.current_user

    # Handle the submission of the 2FA setup confirmation form
    if request.method == 'POST':

        # Get the code digits
        digit_1 = request.form.get( 'two_factor_code_digit_1' )
        digit_2 = request.form.get( 'two_factor_code_digit_2' )
        digit_3 = request.form.get( 'two_factor_code_digit_3' )
        digit_4 = request.form.get( 'two_factor_code_digit_4' )
        digit_5 = request.form.get( 'two_factor_code_digit_5' )
        digit_6 = request.form.get( 'two_factor_code_digit_6' )

        # Concatenate the digits to form the code
        code = f"{digit_1}{digit_2}{digit_3}{digit_4}{digit_5}{digit_6}"

        # Check the code is valid
        if not Auth.verify_2fa_code( code, user.secret ):

            flash( 'That code didn\'t work. Maybe it expired?', 'error' )

            return render_template( 'auth/login-setup-confirm-2fa.html' )

        user.passed_two_factor_auth()

        Users.update_user( user.ID, { 'two_factor_enabled': 1 } )

        # Redirect to the homepage
        return redirect( url_for( 'portal.index' ) )

    return render_template( 'auth/login-2fa.html' )

# ROUTE - /verify_email
@auth_bp.route( '/verify_email' )
def verify_email():

    """
    Simple route which outputs the email verification form
    """

    user = flask_login.current_user

    verify_token = request.args.get( 'token' )
    verify_id    = request.args.get( 'id' )
    resend       = request.args.get( 'resend' )

    if( resend == '1' ):
        send_email = True
    else:
        send_email = False
        
    # Handle the verification link being clicked
    if( verify_token != None and verify_id != None ):

        # The user being verified may not be the currently logged in user
        verify_user = Users.get_user_by( 'ID', verify_id )

        # Check the verification token is valid
        if( verify_user and verify_user.email_verification_code == verify_token ):

            # Update the user's email verification status
            Users.update_user( verify_user.ID, { 'email_verified': 1 } )

            # If the user is the currently logged in user, redirect to the homepage
            if( user.is_anonymous == False and user.ID == verify_user.ID ):
                user.email_verified = True

                flash( 'Email verified', 'success' )

                return redirect( url_for( 'portal.index' ) )
            # Otherwise, return a message
            else:
                return 'Email verified'
        else:
            return 'Invalid verification token'
    
    if( not user or user.is_anonymous ):
        return redirect( url_for( 'auth.login' ) )

    # If the user doesn't have a verification code, generate one
    if( user.email_verification_code == None ):

        token = Auth.generate_url_safe_token( 32 )

        user.email_verification_code = token

        Users.update_user( user.ID, { 'email_verification_code': token } )

        send_email = True

    # Send the email if required
    if( send_email ):

        email_html = render_template( 'emails/signup.html', token = user.email_verification_code, user_id = user.get_id(), env = config.environment )

        date = datetime.today()

        user.signup_email_sent = date

        Users.update_user( user.ID, { 'signup_email_sent': date } )

        Mailer.send_email( user.email, 'Verify your email address', email_html )

    return render_template( 'auth/verify-email.html' )

# ROUTE - /post/create_account  
@auth_bp.route( '/post/create_account', methods=['POST'] )
def handler_create_account():

    """
    Form handler for the register for an account form
    """
    
    # Get the form data
    email    = request.form.get( 'email' )
    password = request.form.get( 'password' )
    confirm  = request.form.get( 'password_confirm' )

    # Sanitise
    clean_email    = bleach.clean( email )
    clean_email    = Users.sanitize_email( email )
    clean_password = bleach.clean( password )

    # Check the email address is valid
    if( email != clean_email or not Users.validate_email( clean_email ) ):
        flash( 'Email address is invalid or contained invalid characters', 'error' )
        return redirect( url_for( 'auth.register' ) )
    
    # Check the password isn't empty
    if( not clean_password ) :
        flash( 'Password cannot be empty', 'error' )
        return redirect( url_for( 'auth.register' ) )
    
    # Check the two passwords match
    if( clean_password != confirm ):
        flash( 'Passwords must match', 'error' )
        return redirect( url_for( 'auth.register' ) )
    
    is_strong = Auth.is_password_strong( clean_password )

    if( is_strong != True ):
        flash( is_strong, 'error' )
        return redirect( url_for( 'auth.register' ) )
    
    # Define regular expressions for password validation
    has_uppercase = any( char.isupper() for char in clean_password )
    has_lowercase = any( char.islower() for char in clean_password )
    has_number    = any( char.isdigit() for char in clean_password )
    has_special   = any( char in '!@#$%^&*(),.?":{}|<>' for char in clean_password )
    has_length    = len( clean_password ) >= 8

    # Check if the password meets all the criteria
    if not ( has_uppercase and has_lowercase and has_number and has_special and has_length ):
        flash('Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number and one special character.', 'error')
        return redirect( url_for( 'auth.register' ) )
    
    user = Users.get_user_by( 'email', email )

    # Check the email address hasn't already been used
    if( user ):
        flash( 'Email address has already been registered', 'error' )
        return redirect( url_for( 'auth.register' ) )
    
    # Create a new user - with standard role
    user_id = Users.create_user( email, password, 'standard' )

    if( not user_id ):
        flash( 'An error occurred creating the user', 'error' )
        return redirect( url_for( 'auth.register' ) )
    
    # Log the user in to their new account
    user = Users.get_user_by( 'ID', user_id )
    flask_login.login_user( user )

    # Redirect to the homepage
    return redirect( url_for( 'portal.index' ) )