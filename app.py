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

Database.create_default_tables()
count = Database.get_var( 'SELECT count( ID ) FROM users WHERE role = "administrator" LIMIT 1' )
count = int( count )

if count == 0:
    Users.create_user( config.default_admin_email, config.default_admin_password, 'administrator' )

app            = Flask( __name__ )
app.secret_key = config.secret_key

login_manager  = flask_login.LoginManager()
login_manager.init_app( app )

csrf = CSRFProtect( app )

@login_manager.user_loader
def load_user( user_id ):
    return Users.get_user_by( 'ID', user_id )

# Unauthorized handler to redirect to login page
@login_manager.unauthorized_handler
def handle_needs_login():
    return redirect( url_for( 'login' ) ) 

@app.route( '/' )
@flask_login.login_required
def index():

    args = {}

    if( not flask_login.current_user.is_admin() ):
        args['created_by'] = flask_login.current_user.id
    
    tickets = Tickets.get_tickets( args )
    return render_template( 'index.html', tickets = tickets )

@app.route( '/login', methods=['GET', 'POST'] )
def login():

    if request.method == 'POST':

        logger    = Users.get_logger()

        email     = request.form.get( 'email' )
        password  = request.form.get( 'password' )
        client_ip = request.remote_addr

        email    = bleach.clean( email )
        password = bleach.clean( password )

        user     = Users.get_user_by( 'email', email )

        if user and user.password == Users.hash_password( password, user.salt ):
            flask_login.login_user( user )

            Users.track_login( user.id )
            logger.info(f"User '{user.id}' logged in from IP address {client_ip}.")

            return redirect( url_for( 'index' ) )
        
        flash( 'Invalid Email Address or Password', 'error' )
        
        logger.info(f"User '{user.id}' FAILED login from IP address {client_ip}.")
        
        return render_template( 'login.html', email = email )

    return render_template( 'login.html' )

@app.route( '/register' )
def register():
    return render_template( 'register.html' )

@app.route( '/logout' )
def logout():

    flask_login.logout_user()
    flash( 'You have been logged out', 'success' )

    return redirect( 'login' )

@app.route( '/account' )
@flask_login.login_required
def account():

    user = flask_login.current_user

    return render_template( 'account.html', email=user.email )

@app.route('/ticket/<int:id>')
@flask_login.login_required
def ticket( id ):

    current_user   = flask_login.current_user
    ticket = Tickets.get_ticket( id )

    if False == ticket:

        flash( 'Ticket could not be found, maybe it was deleted?', 'error' )

        return redirect( url_for( 'index' ) )

    if current_user.role != 'administrator' and ticket['created_by'] != current_user.id:

        flash( 'You\'re not allowed to do that!', 'error' )

        return redirect( url_for( 'index' ) )
    
    comments = Comments.get_comments_by_ticket_id( ticket['ID'] )
    user     = Users.get_user_by( 'ID', ticket['created_by'] )
    
    return render_template( 'ticket.html', ticket=ticket, comments=comments, user=user )

@app.route('/ticket/new')
@flask_login.login_required
def new_ticket():

    return render_template( 'ticket-new.html' )

@app.route( '/users' )
@flask_login.login_required
def users():

    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )

    users = Users.get_users()
    return render_template( 'users.html', users = users )

@app.route( '/user/new' )
@flask_login.login_required
def new_user():

    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )
    
    return render_template( 'user-new.html' )

@app.route('/user/<int:id>')
@flask_login.login_required
def user( id ):

    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )

    user = Users.get_user_by( 'ID', id )

    return render_template( 'user.html', user = user )

@app.route( '/post/create_ticket', methods=['POST'] )
@flask_login.login_required
def handler_create_ticket():
    
    user      = flask_login.current_user

    subject   = request.form.get( 'subject' )
    comment   = request.form.get( 'comment' )

    allowed_tags = ['br']
    comment      = comment.replace("\n", "<br>")

    comment      = bleach.clean( comment, tags=allowed_tags )
    subject      = bleach.clean( subject )

    if( not comment or not subject ):
        flash( 'A required form field is missing or invalid', 'error' )
        return redirect( url_for( 'new_ticket' ) )
    
    ticket_id  = Tickets.create_ticket( subject, user.id )
    comment_id = Comments.create_comment( ticket_id, user.id, comment )

    return redirect( url_for( 'ticket', id=ticket_id) )

@app.route( '/post/update_ticket', methods=['POST'] )
@flask_login.login_required
def handler_update_ticket():
    
    user      = flask_login.current_user

    comment   = request.form.get( 'comment' )
    action    = request.form.get( 'action' )
    ticket_id = request.form.get( 'ticket_id' )

    actions = ['update', 'resolved', 'delete']

    if action not in actions:
        return 'Invalid action'
    
    ticket = Tickets.get_ticket( ticket_id )

    if False == ticket:
        return 'Invalid ticket ID'
    
    if user.role != 'administrator' and ticket.created_by != user.id:
        return 'You cannot edit this ticket'
    
    if user.role != 'administrator' and action == 'delete':
        return 'You have insufficient permissions to perform the specified action'
    
    if action == 'delete':

        Tickets.delete_ticket( ticket['ID'] )
        flash( 'Ticket deleted', 'success' )

        return redirect( url_for( 'index' ) )
    else:

        allowed_tags = ['br']
        comment      = comment.replace("\n", "<br>")
        comment      = bleach.clean( comment, tags=allowed_tags )

        if( comment ) :
            Comments.create_comment( ticket['ID'], user.id, comment )
        elif( not comment and action != 'resolved' ):
            flash( '<b>ERROR:</b> Comment cannot be empty', 'error' )

            return redirect( url_for( 'ticket', id=ticket['ID'] ) )

        if( action == 'resolved' ):
            Tickets.update_ticket( ticket['ID'], { 'status': 'complete' } )
        elif( user.is_admin() ):
            Tickets.update_ticket( ticket['ID'], { 'status': 'pending' } )
        else:
            Tickets.update_ticket( ticket['ID'], { 'status': 'processing' } )

        return redirect( url_for( 'ticket', id=ticket['ID'] ) )
    
@app.route( '/post/update_account', methods=['POST'] )
@flask_login.login_required
def handler_update_account():
    
    user             = flask_login.current_user

    email            = request.form.get( 'email' )
    password         = request.form.get( 'password' )
    new_password     = request.form.get( 'new_password' )
    confirm_password = request.form.get( 'new_password_confirm' )

    email            = bleach.clean( email )
    password         = bleach.clean( password )
    new_password     = bleach.clean( new_password )
    confirm_password = bleach.clean( confirm_password )

    email  = Users.sanitize_email( email )
    update = {}

    if( user.password != Users.hash_password( password, user.salt ) ):
        flash( 'Please confirm your current password to make changes to your account', 'error' )
        return redirect( url_for( 'account' ) )

    if( not Users.validate_email( email ) ) :
        flash( 'Email address is invalid, please enter a different email address', 'error' )
        return redirect( url_for( 'account' ) )
    
    if( email != user.email ):

        lookup = Users.get_user_by( 'email', email )

        if( lookup ):
            flash( 'Email address is already in use', 'error' )
            return redirect( url_for( 'account' ) )
        
        update['email'] = email

    if new_password:

        if not confirm_password:
            flash( 'You must confirm your new password', 'error' )
            return redirect( url_for( 'account' ) )

        if new_password != confirm_password:
            flash( 'New passwords did not match', 'error' )
            return redirect( url_for( 'account' ) )
        
        hash = Users.hash_password( new_password, user.salt )

        if hash != user.password:
            update['password'] = hash

    
    if len( update ) > 0:
        Users.update_user( user.id, update )

    flash( 'User account updated', 'success' )
    
    return redirect( url_for( 'account' ) )

@app.route( '/post/create_account', methods=['POST'] )
def handler_create_account():
    
    email    = request.form.get( 'email' )
    password = request.form.get( 'password' )
    confirm  = request.form.get( 'password_confirm' )

    clean_email    = bleach.clean( email )
    clean_email    = Users.sanitize_email( email )
    clean_password = bleach.clean( password )

    if( email != clean_email or not Users.validate_email( clean_email ) ):
        flash( 'Email address is invalid or contained invalid characters', 'error' )
        return redirect( url_for( 'register' ) )
    
    if( not clean_password ) :
        flash( 'Password cannot be empty', 'error' )
        return redirect( url_for( 'register' ) )
    
    if( clean_password != confirm ):
        flash( 'Passwords must match', 'error' )
        return redirect( url_for( 'register' ) )
    
    user = Users.get_user_by( 'email', email )

    if( user ):
        flash( 'Email address has already been registered', 'error' )
        return redirect( url_for( 'register' ) )
    
    user_id = Users.create_user( email, password, 'standard' )

    if( not user_id ):
        flash( 'An error occurred creating the user', 'error' )
        return redirect( url_for( 'register' ) )
    
    user = Users.get_user_by( 'ID', user_id )
    flask_login.login_user( user )

    return redirect( url_for( 'index' ) )

@app.route( '/post/new_user', methods=['POST'] )
@flask_login.login_required
def handler_new_user():

    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )
    
    email    = request.form.get( 'email' )
    password = request.form.get( 'password' )
    role     = request.form.get( 'role' )

    clean_email    = bleach.clean( email )
    clean_email    = Users.sanitize_email( email )
    clean_password = bleach.clean( password )

    if( email != clean_email or not Users.validate_email( clean_email ) ):
        flash( 'Email address is invalid or contained invalid characters', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    if( not clean_password ) :
        flash( 'Password cannot be empty', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    if( role != 'standard' and role != 'administrator' ):
        flash( 'Invalid role', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    user = Users.get_user_by( 'email', email )

    if( user ):
        flash( 'Email address has already been registered', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    user_id = Users.create_user( email, password, role )

    if( not user_id ):
        flash( 'An error occurred creating the user', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    return redirect( url_for( 'user', id=user_id ) )

@app.route( '/post/edit_user', methods=['POST'] )
@flask_login.login_required
def handler_edit_user():

    if( not flask_login.current_user.is_admin() ):
        flash( 'You\'re not allowed to do that!', 'error' )
        return redirect( url_for( 'index' ) )

    action   = request.form.get( 'action' )
    user_id  = request.form.get( 'user_id' )
    email    = request.form.get( 'email' )
    password = request.form.get( 'password' )
    role     = request.form.get( 'role' )

    user = Users.get_user_by( 'ID', user_id )

    if( not user ):
        flash( 'Invalid user ID', 'error' )
        return redirect( url_for( 'users' ) )
    
    actions = ['update', 'delete']

    if action not in actions:
        return 'Invalid action'
    
    current_user = flask_login.current_user

    if( user.id == current_user.id ):
        flash( 'You cannot change your own role or delete your own account', 'error' )
        return redirect( url_for( 'account' ) )
    
    if( action == 'delete' ):
        Users.delete_user( user_id )

        flash( 'User account deleted', 'success' )
   
        return redirect( url_for( 'users' ) )

    clean_email    = bleach.clean( email )
    clean_email    = Users.sanitize_email( email )
    clean_password = bleach.clean( password )

    if( email != clean_email or not Users.validate_email( clean_email ) ):
        flash( 'Email address is invalid or contained invalid characters', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    if( role != 'standard' and role != 'administrator' ):
        flash( 'Invalid role', 'error' )
        return redirect( url_for( 'new_user' ) )
    
    update = {}

    if( clean_email != user.email ):
        update['email'] = clean_email
    
    if( clean_password ):
        hash = Users.hash_password( clean_password, user.salt )

        if( hash != user.password ):
            update['password'] = hash
    
    if( role != user.role ):
        update['role'] = role

    if len( update ) > 0:
        Users.update_user( user.id, update )

    flash( 'User account updated', 'success' )
   
    return redirect( url_for( 'user', id=user.id ) )

if __name__ == '__main__':
    app.run()