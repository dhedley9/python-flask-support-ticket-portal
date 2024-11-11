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

# Database connection
db_url = os.getenv( 'DATABASE_URL' )

# Database session - used only for initialisation process (see core.init), not for the application itself. Sessions are handled per request

init_use_db_session = None # Toggle this to True to create a session for the setup process
init_db_session     = None # This is for use by the Database class only