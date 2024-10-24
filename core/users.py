import hashlib
import os
import re
import logging

import core.config as config

from core.database import Database
from core.user import User

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
        date = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )
        salt = os.urandom( 32 )

        # Hash the password with the salt
        hashed_password = Users.hash_password( password, salt )
        
        data = {
            'email': email,
            'password': hashed_password,
            'salt': salt,
            'role': role,
            'date_created': date,
        }

        # Insert the user to the database
        user_id = Database.insert( 'users', data )

        return user_id
    
    def update_user( ID, args ):

        """
        Update a user

        :param ID - (int) the ID of the user to update
        :param args - (dictionary) arguments to update the user with

        :return boolean
        """
        
        # Only allow certain fields to be updated
        allowed = ['email', 'password', 'role', 'last_login']
        clean   = {}
        where   = { 'ID': ID }

        for key in args:
            
            if key in allowed:
                clean[key] = args[key]

        if len( clean ) == 0:
            return False
        
        Database.update( 'users', clean, where )

        return True
    
    def delete_user( ID ):

        """
        Delete a user

        :param ID - (int) the ID of the user to delete

        :return True
        """

        where = { 'ID': ID }

        Database.delete( 'users', where )

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

        # Prepared query
        sql = 'SELECT ID, email, password, salt, role, date_created, last_login FROM users WHERE ' + field + ' = ?'

        value  = [value]
        value  = tuple( value )
        
        result = Database.get_row( sql, value )

        # Check there is a user
        if( result == None ) :
            return False
        
        # Convert to standardised dictionary
        userdata = {
            'ID': result[0],
            'email': result[1],
            'password': result[2],
            'salt': result[3],
            'role': result[4],
            'date_created': datetime.strptime( result[5], '%Y-%m-%d %H:%M:%S' ),
            'last_login': result[6],
        }

        if userdata['last_login'] != None:
            userdata['last_login'] = datetime.strptime( userdata['last_login'], '%Y-%m-%d %H:%M:%S' )

        # Create a user object
        return User( userdata )
    
    def get_users():

        """
        Retrieve all the users

        :return List - containing dictionaries
        """

        sql = 'SELECT ID, email, password, salt, role, date_created, last_login FROM users'

        results = Database.get_results( sql )
        users   = []

        # Organise results into dictionaries
        for row in results:

            userdata = {
                'ID': row[0],
                'email': row[1],
                'password': row[2],
                'salt': row[3],
                'role': row[4],
                'date_created': datetime.strptime( row[5], '%Y-%m-%d %H:%M:%S' ),
                'last_login': row[6],
            }

            # If there is a value for the last login, convert into a datetime
            if userdata['last_login'] != None:
                userdata['last_login'] = datetime.strptime( userdata['last_login'], '%Y-%m-%d %H:%M:%S' )

            users.append( userdata )

        return users
    
    def hash_password( password, salt ) :

        """
        Salt and hash a password

        :param password - (string) the plaintext password
        :param salt - (string) the salt string to salt the password with

        :return string
        """

        # Hash using sha235 algorithm
        return hashlib.pbkdf2_hmac( 'sha256', password.encode( 'utf-8' ), salt, 100000 )
    
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
        
        last_login = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )

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
