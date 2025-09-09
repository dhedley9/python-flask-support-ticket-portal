class Test_Login:

    def test_login_page( self, client ):

        response = client.get( '/login' )

        # First assertion: Check if the status code is 200 (OK)
        assert response.status_code == 200

        # Second assertion: Check if the page contains the text "Log in to your account"
        assert b"Log in to your account" in response.data
    
    def test_login( self, client ):

        data = {
            'email': 'admin@admin.co.uk',
            'password': 'password'
        }

        response = client.post( '/login', data = data )

        # First assertion: Check if the status code is 302 (Redirect)
        assert response.status_code == 302

    
    def test_login_invalid_email( self, client ):

        data = {
            'email': 'notarealemail',
            'password': 'password'
        }

        response = client.post( '/login', data = data )

        # First assertion: Check if the status code is 200 (OK)
        assert response.status_code == 200

        # Second assertion: Check if the page contains the text "Invalid Email Address or Password"
        assert b"Invalid Email Address or Password" in response.data
        
    def test_login_invalid_password( self, client ):
            
        data = {
            'email': 'admin@admin.co.uk',
            'password': 'wrongpassword'
        }

        response = client.post( '/login', data = data )

        # First assertion: Check if the status code is 200 (OK)
        assert response.status_code == 200

        # Second assertion: Check if the page contains the text "Invalid Email Address or Password"
        assert b"Invalid Email Address or Password" in response.data