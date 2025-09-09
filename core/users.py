import hashlib
import os
import re
import logging

import core.config as config

from core.database import database
from core.user import User
from models.user import User as User_Model
from sqlalchemy import func

from datetime import datetime
from pathlib import Path

class Users():

    """
    Class containing useful methods for users
    """

    def create_user( email, password, role ):

        """
        Create a new user

        :param email - (string) the email address of the user
        :param password - (string) the password in plaintext
        :param role - (string) the role

        :return int or False
        """

        user = Users.get_user_by( 'email', email )

        # Check there isn't already a user with that email address
        if( user != False ) :
            return False
        
        # Get today's date and a random salt string
        date   = datetime.today()
        salt   = os.urandom( 32 )
        pepper = config.pepper

        # Hash the password with the salt
        hashed_password = Users.hash_password( password, salt, pepper )
        
        data = {
            'email': email,
            'password': hashed_password,
            'salt': salt,
            'role': role,
            'date_created': date,
        }

        user = User_Model( data )

        database.add_model( user )

        return user.ID
    
    def update_user( ID, args ):

        """
        Update a user

        :param ID - (int) the ID of the user to update
        :param args - (dictionary) arguments to update the user with

        :return boolean
        """

        # user       = Users.get_user_by( 'ID', ID )
        user_model = database.get_model( User_Model, { 'ID': ID } )
        
        # Only allow certain fields to be updated
        allowed = ['email', 'password', 'role', 'last_login', 'secret', 'email_verified', 'email_verification_code', 'signup_email_sent', 'two_factor_enabled']
        clean   = {}

        for key in args:
            
            if key in allowed:
                clean[key] = args[key]
        
        if len( clean ) == 0:
            return False
        
        database.update_model( user_model, clean )

        return True
    
    def delete_user( ID ):

        """
        Delete a user

        :param ID - (int) the ID of the user to delete

        :return True
        """

        # user = Users.get_user_by( 'ID', ID )
        user_model = database.get_model( User_Model, { 'ID': ID } )

        if user_model == None:
            return False
        
        database.delete_model( user_model )

        return True
    
    def get_user_by( field, value ):

        """
        Retrieve a user either by email or by user ID

        :param field - (string) the field to retrieve by, either: 'ID', 'email'
        :param value - (mixed) the value to use to lookup

        :return User
        """

        # Allowable fields
        fields = [ 'ID', 'email' ]

        # Default to ID
        if field not in fields: 
            field = 'ID'

        if field == 'ID':
            value = int( value )
        else:
            value = str( value )

        model = database.get_model( User_Model, { field: value } )

        if( model == None ):
            return False

        args = {
            'ID': model.ID,
            'email': model.email,
            'password': model.password,
            'salt': model.salt,
            'role': model.role,
            'date_created': model.date_created,
            'secret': model.secret,
            'last_login': model.last_login,
            'email_verification_code': model.email_verification_code,
            'signup_email_sent': model.signup_email_sent,
            'email_verified': model.email_verified,
            'two_factor_enabled': model.two_factor_enabled
        }

        user = User( args )
       
        return user

    
    def get_users():

        """
        Retrieve all the users

        :return List - containing dictionaries
        """

        users = database.get_models( User_Model )

        return users
    
    def hash_password( password, salt, pepper ) :

        """
        Salt and hash a password

        :param password - (string) the plaintext password
        :param salt - (string) the salt string to salt the password with
        :param pepper - (string) the pepper string to salt the password with

        :return string
        """

        peppered_password = password + pepper

        # Hash using sha235 algorithm
        return hashlib.pbkdf2_hmac( 'sha256', peppered_password.encode( 'utf-8' ), salt, 100000 )
    
    def sanitize_email( email ): 

        """
        Sanitise an email address

        :param email - (string) the email address

        :return string
        """

        # Remove extra whitespace and lowercase
        sanitized_email = email.strip()
        sanitized_email = sanitized_email.lower()

        return sanitized_email
        
    def validate_email( email ):

        """
        Validate an email address

        :param email - (string) the email address

        :return boolean
        """
        
        # Regex for [string]@[string].[string] format
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        return re.match( pattern, email )
    
    def track_login( ID ):

        """
        Record a user login in the database

        :param ID - (int) the user ID
        """
        
        last_login = datetime.today()

        Users.update_user( ID, { 'last_login': last_login } )

    def get_logger():

        """
        Get the custom text logger, used to log logins to a text file

        :return Logger object
        """

        if( not config.users_logger ) :

            file = config.abspath

            path     = Path( file ).parent.absolute()
            path     = str( path )

            # Get the current date in "YYYY-MM" format
            current_date = datetime.now().strftime( "%Y-%m" )

            # Log file for the current month
            log_file = path + '/logs/user-logins-' + current_date + '.log'

            # Check if the log file exists, if not, create it
            if not os.path.exists( log_file ):
                os.makedirs( os.path.dirname( log_file ), exist_ok=True )
                open( log_file, 'a' ).close()

            # Create a custom logger
            custom_logger = logging.getLogger( 'user_logins_logger' )
            custom_logger.setLevel( logging.INFO )

            # Create a file handler for your custom log file
            file_handler = logging.FileHandler( log_file )

            # Create a formatter
            formatter = logging.Formatter( "%(asctime)s - %(levelname)s - %(message)s" )
            file_handler.setFormatter( formatter )

            # Add the file handler to the custom logger
            custom_logger.addHandler( file_handler )

            config.users_logger = custom_logger
        
        return config.users_logger
    
    def admin_user_exists():

        admin = database.get_model( User_Model, { 'role': 'administrator' } )

        return admin != None
