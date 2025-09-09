import pytest
import sys
import os

# Add the parent directory to the path so the application can be imported
sys.path.insert( 0, os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

from app import app as app

@pytest.fixture
def client():

    app.config['TESTING']    = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        yield client

class Test_Login:

    def test_login_page( self, client ):

        response = client.get( '/login' )

        # First assertion: Check if the status code is 200 (OK)
        assert response.status_code == 200

        # Second assertion: Check if the page contains the text "Log in to your account"
        assert b"Log in to your account" in response.data
