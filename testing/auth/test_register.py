from core.users import Users

class Test_Register:

    def test_register_page( self, client ):

        response = client.get( '/register' )

        # First assertion: Check if the status code is 200 (OK)
        assert response.status_code == 200

        # Second assertion: Check if the page contains the text "Register for an account"
        assert b"Create an account" in response.data

    def test_register( self, client ):

        data = {
            'email': 'deletethisuser@domain.com',
            'password': 'SuperSecretPassword1234!',
            'password_confirm': 'SuperSecretPassword1234!'
        }

        response = client.post( '/post/create_account', data = data )

        # First assertion: Check if the status code is 302 (Redirect)
        assert response.status_code == 302

        # Second assertion: Check if the user was added to the database
        user = Users.get_user_by( 'email', 'deletethisuser@domain.com' )

        assert user is not None
