import pytest
import sys
import os

# Add the parent directory to the path so the application can be imported
sys.path.insert( 0, os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

from app import app as app
from app import database as database

from core import config
from core.users import Users

@pytest.fixture
def client():

    app.config['TESTING']          = True
    app.config['SECRET_KEY']       = 'test_secret_key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:

        with app.app_context():

            # database.create_tables()

            database.auto_commit = False

            yield client

            session = database.get_session()

            session.rollback()
            session.close()