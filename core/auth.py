import pyotp
import qrcode
import base64
import secrets
import string
import re

import core.config as config

from io import BytesIO
from pathlib import Path

class Auth:

    def create_secret():

        return pyotp.random_base32()
    
    def verify_2fa_code( code, secret ):

        totp = pyotp.TOTP( secret )

        return totp.verify( code )
    
    def get_2fa_link( secret, username, issuer_name ):

        totp = pyotp.TOTP( secret )

        return totp.provisioning_uri( name=username, issuer_name=issuer_name )
    
    def get_qr_code( uri ):

        qr = qrcode.make( uri )

        return qr
    
    def get_qr_code_img( qr ):

        # Convert the QR code to an in-memory bytes buffer
        buffered = BytesIO()
        
        qr.save(buffered, format="PNG")
        
        # Encode the image to base64
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Create the HTML image tag with the base64 string
        img_tag = f'<img src="data:image/png;base64,{img_str}" alt="QR Code">'

        return img_tag
    
    def generate_url_safe_token( length ):

        characters = string.ascii_letters + string.digits + "-_"

        return ''.join( secrets.choice( characters ) for i in range( length ) )
    
    def is_password_strong( password ):

        # Define regular expressions for password validation
        has_uppercase = any( char.isupper() for char in password )
        has_lowercase = any( char.islower() for char in password )
        has_number    = any( char.isdigit() for char in password )
        has_special   = re.search( r'[^a-zA-Z0-9]', password)
        has_length    = len( password ) >= 8

        # Check if the password meets all the criteria
        if not ( has_uppercase and has_lowercase and has_number and has_special and has_length ):
            return 'Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number and one special character.'
        
        if Auth.is_password_common( password ):
            return 'Password is too common.'
        
        return True
        
    def is_password_common( password ):

        password_lower    = password.lower()
        password_stripped = re.sub( r'[!@#$%^&*(),.?":{}|<>0-9]', '', password_lower )
        blacklist         = Auth.get_password_blacklist()

        print( password_lower, password_stripped )

        if password_lower in blacklist or password_stripped in blacklist:
            return True
        
        return False

    def get_password_blacklist():
            
        path = Path( config.abspath ).parent.absolute()

        file  = path / 'static/resources/owasp-common-passwords.txt'

        with open( file, "r" ) as f:
            return set( line.strip().lower() for line in f )
        
    
    def get_client_ip( request ):

        # Heroku and most proxies append the real client IP to the X-Forwarded-For header
        forwarded_for = request.headers.get('X-Forwarded-For')
        
        if forwarded_for:
            # X-Forwarded-For is a comma-separated list of IPs, the first is the real client IP
            return forwarded_for.split(',')[0]
        
        return request.remote_addr