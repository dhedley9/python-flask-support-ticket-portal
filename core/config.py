from dotenv import load_dotenv
import os

load_dotenv()

secret_key  = os.getenv( 'SECRET_KEY' )
pepper      = os.getenv( 'PEPPER' )
environment = os.getenv( 'FLASK_ENV' )

default_admin_email    = os.getenv( 'DEFAULT_USER' )
default_admin_password = os.getenv( 'DEFAULT_PASSWORD' )

mailgun_api_key = os.getenv( 'MAILGUN_API_KEY' )
mailgun_domain  = os.getenv( 'MAILGUN_DOMAIN' )
mailgun_region  = os.getenv( 'MAILGUN_REGION' )

# These variables are loaded later in the application
abspath      = None
users_logger = None