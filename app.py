import flask_login
import bleach

from flask import Flask, request, redirect, url_for, render_template, flash
from flask_wtf.csrf import CSRFProtect

import core.config as config
config.abspath = __file__

from core.database import Database
from core.users import Users
from core.user import User
from core.tickets import Tickets
from core.comments import Comments

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
    return redirect( url_for( 'login' ) ) 

# ROUTE - Index
@app.route( '/' )
@flask_login.login_required
def index():

    """
    Returns the homepage of the portal containing a table of tickets
    - Login required
    """

    args = {}

    if( not flask_login.current_user.is_admin() ):
        args['created_by'] = flask_login.current_user.id
    
    tickets = Tickets.get_tickets( args )
    return render_template( 'index.html', tickets = tickets )

# ROUTE - /login
@app.route( '/login', methods=['GET', 'POST'] )
def login():

    """
    Returns and handles the login form
    """

    # Handle the submission of the login form
    if request.method == 'POST':

        logger    = Users.get_logger()

        # Get the posted form info
        email     = request.form.get( 'email' )
        password  = request.form.get( 'password' )
        client_ip = request.remote_addr

        # Sanitize
        email    = bleach.clean( email )
        password = bleach.clean( password )

        # Try to retrieve the user by their email address
        user     = Users.get_user_by( 'email', email )

        # If there is a user and the (hashed) password match, log the user in
        if user and user.password == Users.hash_password( password, user.salt ):
            flask_login.login_user( user )

            # Record and log the login
            Users.track_login( user.id )
            logger.info(f"User '{user.id}' logged in from IP address {client_ip}.")

            # Redirect to the homepage
            return redirect( url_for( 'index' ) )
        
        flash( 'Invalid Email Address or Password', 'error' )
        
        if( user ) :
            logger.info(f"User '{user.id}' FAILED login from IP address {client_ip}. Reason: Invalid password")
        else:
            logger.info(f"User '0' FAILED login from IP address {client_ip}. Reason: Invalid email. Email {email}")
        
        
        return render_template( 'login.html', email = email )

    return render_template( 'login.html' )

# ROUTE - /register
@app.route( '/register' )
def register():

    """
    Simple route which outputs the user registration form
    """

    return render_template( 'register.html' )

# ROUTE - /logout
@app.route( '/logout' )
def logout():

    """
    Simple route logs out the current user
    """

    flask_login.logout_user()
    flash( 'You have been logged out', 'success' )

    return redirect( 'login' )

# ROUTE - /account
@app.route( '/account' )
@flask_login.login_required
def account():

    """
    Returns the account page for the current user
    - Login required
    """

    user = flask_login.current_user

    return render_template( 'account.html', email=user.email )

# ROUTE - /ticket/[ID]
@app.route('/ticket/<int:id>')
@flask_login.login_required
def ticket( id ):

    """
    Returns the page for a single ticket
    - Login required
    - Ticket ID required
    """

    current_user   = flask_login.current_user
    ticket = Tickets.get_ticket( id )

    # Check the ticket ID returns a valid ticket
    if False == ticket:

        flash( 'Ticket could not be found, maybe it was deleted?', 'error' )

        return redirect( url_for( 'index' ) )
    
    # Check the current user can access the ticket
    if current_user.role != 'administrator' and ticket['created_by'] != current_user.id:

        flash( 'You\'re not allowed to do that!', 'error' )

        return redirect( url_for( 'index' ) )
    
    # Retrieve the ticket comments and the ticket user
    comments = Comments.get_comments_by_ticket_id( ticket['ID'] )
    user     = Users.get_user_by( 'ID', ticket['created_by'] )
    
    return render_template( 'ticket.html', ticket=ticket, comments=comments, user=user )

# ROUTE - /ticket/new
@app.route('/ticket/new')
@flask_login.login_required
def new_ticket():

    """
    Returns the page to create a new ticket
    - Login required
    """

    return render_template( 'ticket-new.html' )

# ROUTE - /users
@app.route( '/users' )
@flask_login.login_required
def users():

    """
    Returns the page for all registered users
    - Login required
    """

    # Only admins can see/edit users
    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )

    users = Users.get_users()
    return render_template( 'users.html', users = users )

# ROUTE - /user/new
@app.route( '/user/new' )
@flask_login.login_required
def new_user():

    """
    Returns the page to create a new user
    - Login required
    """

    # Only admins can create new users
    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )
    
    return render_template( 'user-new.html' )

# ROUTE - /user/[ID]
@app.route('/user/<int:id>')
@flask_login.login_required
def user( id ):

    """
    Returns the page to edit a single user
    - Login required
    """

    # Only admins can edit users
    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )

    user = Users.get_user_by( 'ID', id )

    return render_template( 'user.html', user = user )

# ROUTE - /post/create_ticket
@app.route( '/post/create_ticket', methods=['POST'] )
@flask_login.login_required
def handler_create_ticket():

    """
    Form handler for the create ticket form
    - Login required
    """
    
    user      = flask_login.current_user

    # Get the form data
    subject   = request.form.get( 'subject' )
    comment   = request.form.get( 'comment' )

    # Swap out new lines for HTML line breaks and allow when sanitising
    allowed_tags = ['br']
    comment      = comment.replace("\n", "<br>")

    # Sanitise
    comment      = bleach.clean( comment, tags=allowed_tags )
    subject      = bleach.clean( subject )

    # Check the fields aren't empty
    if( not comment or not subject ):
        flash( 'A required form field is missing or invalid', 'error' )
        return redirect( url_for( 'new_ticket' ) )
    
    # Create the ticket and comment
    ticket_id  = Tickets.create_ticket( subject, user.id )
    comment_id = Comments.create_comment( ticket_id, user.id, comment )

    # Redirect to the newly created ticket
    return redirect( url_for( 'ticket', id=ticket_id) )

# ROUTE - /post/update_ticket
@app.route( '/post/update_ticket', methods=['POST'] )
@flask_login.login_required
def handler_update_ticket():

    """
    Form handler for the edit ticket form
    - Login required
    """
    
    user      = flask_login.current_user

    # Get the form data
    comment   = request.form.get( 'comment' )
    action    = request.form.get( 'action' )
    ticket_id = request.form.get( 'ticket_id' )

    actions = ['update', 'resolved', 'delete']

    # Check the action we are taking
    if action not in actions:
        return 'Invalid action'
    
    ticket = Tickets.get_ticket( ticket_id )

    # Check the ticket exists
    if False == ticket:
        return 'Invalid ticket ID'
    
    # Check the user can edit the ticket
    if user.role != 'administrator' and ticket['created_by'] != user.id:
        return 'You cannot edit this ticket'
    
    # Only admins can delete tickets
    if user.role != 'administrator' and action == 'delete':
        return 'You have insufficient permissions to perform the specified action'
    
    # Delete the ticket
    if action == 'delete':

        Tickets.delete_ticket( ticket['ID'] )
        flash( 'Ticket deleted', 'success' )

        return redirect( url_for( 'index' ) )
    else:

        # Sanitise the new comment
        allowed_tags = ['br']
        comment      = comment.replace("\n", "<br>")
        comment      = bleach.clean( comment, tags=allowed_tags )

        # Create the comment OR return error
        if( comment ) :
            Comments.create_comment( ticket['ID'], user.id, comment )
        elif( not comment and action != 'resolved' ):
            flash( '<b>ERROR:</b> Comment cannot be empty', 'error' )

            return redirect( url_for( 'ticket', id=ticket['ID'] ) )
        
        # Mark the ticket as resolved
        if( action == 'resolved' ):
            Tickets.update_ticket( ticket['ID'], { 'status': 'complete' } )
        # If an admin commented - mark as 'pending'
        elif( user.is_admin() ):
            Tickets.update_ticket( ticket['ID'], { 'status': 'pending' } )
        # If a normal user commented - mark as 'processing'
        else:
            Tickets.update_ticket( ticket['ID'], { 'status': 'processing' } )

        flash( 'Ticket updated', 'success' )

        # Redirect to the ticket page
        return redirect( url_for( 'ticket', id=ticket['ID'] ) )

# ROUTE - /post/update_account  
@app.route( '/post/update_account', methods=['POST'] )
@flask_login.login_required
def handler_update_account():

    """
    Form handler for the update account form
    - Login required
    """

    user             = flask_login.current_user

    # Get the form data
    email            = request.form.get( 'email' )
    password         = request.form.get( 'password' )
    new_password     = request.form.get( 'new_password' )
    confirm_password = request.form.get( 'new_password_confirm' )

    # Sanitise
    email            = bleach.clean( email )
    password         = bleach.clean( password )
    new_password     = bleach.clean( new_password )
    confirm_password = bleach.clean( confirm_password )

    email  = Users.sanitize_email( email )
    update = {}

    # Check the user has confirmed their password to make changes
    if( user.password != Users.hash_password( password, user.salt ) ):
        flash( 'Please confirm your current password to make changes to your account', 'error' )
        return redirect( url_for( 'account' ) )
    
    # Check the user has entered a valid new email address
    if( not Users.validate_email( email ) ) :
        flash( 'Email address is invalid, please enter a different email address', 'error' )
        return redirect( url_for( 'account' ) )
    
    # If the new email address is different to the current one
    if( email != user.email ):

        # Check no other user is using that email address
        lookup = Users.get_user_by( 'email', email )

        if( lookup ):
            flash( 'Email address is already in use', 'error' )
            return redirect( url_for( 'account' ) )
        
        # Add it to the dictionary to update
        update['email'] = email

    # If a new password has been set
    if( new_password ):

        # Check is has been confirmed
        if not confirm_password:
            flash( 'You must confirm your new password', 'error' )
            return redirect( url_for( 'account' ) )
        
        # Check the two passwords match
        if new_password != confirm_password:
            flash( 'New passwords did not match', 'error' )
            return redirect( url_for( 'account' ) )
        
        # Salt + Hash the password
        hash = Users.hash_password( new_password, user.salt )

        # If it's different, add it to the dictionary
        if hash != user.password:
            update['password'] = hash

    # If there are fields to update, perform an update
    if len( update ) > 0:
        Users.update_user( user.id, update )

    # Redirect with a success message
    flash( 'User account updated', 'success' )
    
    return redirect( url_for( 'account' ) )

# ROUTE - /post/create_account  
@app.route( '/post/create_account', methods=['POST'] )
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
        return redirect( url_for( 'register' ) )
    
    # Check the password isn't empty
    if( not clean_password ) :
        flash( 'Password cannot be empty', 'error' )
        return redirect( url_for( 'register' ) )
    
    # Check the two passwords match
    if( clean_password != confirm ):
        flash( 'Passwords must match', 'error' )
        return redirect( url_for( 'register' ) )
    
    user = Users.get_user_by( 'email', email )

    # Check the email address hasn't already been used
    if( user ):
        flash( 'Email address has already been registered', 'error' )
        return redirect( url_for( 'register' ) )
    
    # Create a new user - with standard role
    user_id = Users.create_user( email, password, 'standard' )

    if( not user_id ):
        flash( 'An error occurred creating the user', 'error' )
        return redirect( url_for( 'register' ) )
    
    # Log the user in to their new account
    user = Users.get_user_by( 'ID', user_id )
    flask_login.login_user( user )

    # Redirect to the homepage
    return redirect( url_for( 'index' ) )

# ROUTE - /post/new_user  
@app.route( '/post/new_user', methods=['POST'] )
@flask_login.login_required
def handler_new_user():

    """
    Form handler for the new user form
    - Login required
    """

    # Only admins can create new users
    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )
    
    # Get form data
    email    = request.form.get( 'email' )
    password = request.form.get( 'password' )
    role     = request.form.get( 'role' )

    # Sanitise
    clean_email    = bleach.clean( email )
    clean_email    = Users.sanitize_email( email )
    clean_password = bleach.clean( password )

    # Check the email is valid
    if( email != clean_email or not Users.validate_email( clean_email ) ):
        flash( 'Email address is invalid or contained invalid characters', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    # Check the password isn't empty
    if( not clean_password ) :
        flash( 'Password cannot be empty', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    # Check the role is valid
    if( role != 'standard' and role != 'administrator' ):
        flash( 'Invalid role', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    user = Users.get_user_by( 'email', email )

    # Check the user doesn't already exits
    if( user ):
        flash( 'Email address has already been registered', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    # Create the user
    user_id = Users.create_user( email, password, role )

    if( not user_id ):
        flash( 'An error occurred creating the user', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    # Redirect to the edit page for the new user
    return redirect( url_for( 'user', id=user_id ) )

# ROUTE - /post/edit_user  
@app.route( '/post/edit_user', methods=['POST'] )
@flask_login.login_required
def handler_edit_user():

    """
    Form handler for the edit user form
    - Login required
    """

    # Only admins can edit users
    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )
    
    # Get the form data
    action   = request.form.get( 'action' )
    user_id  = request.form.get( 'user_id' )
    email    = request.form.get( 'email' )
    password = request.form.get( 'password' )
    role     = request.form.get( 'role' )

    user = Users.get_user_by( 'ID', user_id )

    # If the user doesn't exist
    if( not user ):
        flash( 'Invalid user ID', 'error' )
        return redirect( url_for( 'users' ) )
    
    actions = ['update', 'delete']

    # Check the action the user is performing
    if action not in actions:
        return 'Invalid action'
    
    current_user = flask_login.current_user

    # User can't edit their own account (unless through the account form)
    if( user.id == current_user.id ):
        flash( 'You cannot change your own role or delete your own account', 'error' )
        return redirect( url_for( 'account' ) )
    
    # Delete the user
    if( action == 'delete' ):
        Users.delete_user( user_id )

        flash( 'User account deleted', 'success' )
   
        return redirect( url_for( 'users' ) )
    
    # Sanitise
    clean_email    = bleach.clean( email )
    clean_email    = Users.sanitize_email( email )
    clean_password = bleach.clean( password )

    # Check the email address is valid
    if( email != clean_email or not Users.validate_email( clean_email ) ):
        flash( 'Email address is invalid or contained invalid characters', 'error' )
        return redirect( url_for( 'user', id=user_id ) )
    
    # Check the role is valid
    if( role != 'standard' and role != 'administrator' ):
        flash( 'Invalid role', 'error' )
        return redirect( url_for( 'user', id=user_id ) )
    
    update = {}

    if( clean_email != user.email ):
        update['email'] = clean_email
    
    # If a new password is being set
    if( clean_password ):

        # Salt + Hash the password
        hash = Users.hash_password( clean_password, user.salt )

        if( hash != user.password ):
            update['password'] = hash
    
    if( role != user.role ):
        update['role'] = role

    # If there is an update to be made, update the user
    if len( update ) > 0:
        Users.update_user( user.id, update )

    flash( 'User account updated', 'success' )
   
    return redirect( url_for( 'user', id=user.id ) )

if __name__ == '__main__':
    app.run()