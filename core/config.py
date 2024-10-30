from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv( 'SECRET_KEY' )

default_admin_email    = os.getenv( 'DEFAULT_USER' )
default_admin_password = os.getenv( 'DEFAULT_PASSWORD' )

# These variables are loaded later in the application
abspath      = None
users_logger = None