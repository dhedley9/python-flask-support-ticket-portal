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

    def create_user( email, password, role ):

        user = Users.get_user_by( 'email', email )

        if( user != False ) :
            return False

        date = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )
        salt = os.urandom( 32 )

        hashed_password = Users.hash_password( password, salt )
        
        data = {
            'email': email,
            'password': hashed_password,
            'salt': salt,
            'role': role,
            'date_created': date,
        }

        user_id = Database.insert( 'users', data )

        return user_id
    
    def update_user( ID, args ):
        
        allowed = ['email', 'password', 'role', 'last_login']
        clean   = {}
        where   = { 'ID': ID }

        for key in args:
            
            if key in allowed:
                clean[key] = args[key]

        if len( clean ) == 0:
            return False
        
        Database.update( 'users', clean, where )
    
    def delete_user( ID ):

        where = { 'ID': ID }

        Database.delete( 'users', where )

        return True
    
    def get_user_by( field, value ):

        fields = [ 'ID', 'email' ]

        if field not in fields: 
            field = 'ID'

        sql = 'SELECT ID, email, password, salt, role, date_created, last_login FROM users WHERE ' + field + ' = ?'

        value  = [value]
        value  = tuple( value )
        
        result = Database.get_row( sql, value )

        if( result == None ) :
            return False
            
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

        return User( userdata )
    
    def get_users() :

        sql = 'SELECT ID, email, password, salt, role, date_created, last_login FROM users'

        results = Database.get_results( sql )
        users   = []

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

            if userdata['last_login'] != None:
                userdata['last_login'] = datetime.strptime( userdata['last_login'], '%Y-%m-%d %H:%M:%S' )

            users.append( userdata )

        return users
    
    def hash_password( password, salt ) :
        return  hashlib.pbkdf2_hmac( 'sha256', password.encode( 'utf-8' ), salt, 100000 )
    
    def sanitize_email( email ): 

        sanitized_email = email.strip()
        sanitized_email = sanitized_email.lower()

        return sanitized_email
        
    def validate_email( email ):
        
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.match( pattern, email )
    
    def track_login( ID ):
        
        last_login = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )

        Users.update_user( ID, { 'last_login': last_login } )

    def get_logger():

        if( not config.users_logger ) :

            file = config.abspath

            path     = Path( file ).parent.absolute()
            path     = str( path )
            log_file = path + '/logs/user-logins.log'

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
