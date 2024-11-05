from flask import session

class User:

    """
    Represents a portal user

    Attributes:
        id (int): The user's unique ID
        email (str): The user's email address
        password (str): The user's salted + hashed password
        salt (str): The salt string used to salt the user's password
        role (str): The user's role
        date_created (datetime): The date the user was created
        last_login (datetime): The date the user last logged in
        is_authenticated (bool): Whether the user is authenticated
        is_active (bool): Whether the user is active
        is_anonymous (bool): Whether the user is anonymous (not saved to DB)
    """

    id                      = None
    email                   = None 
    password                = None
    salt                    = None
    role                    = None
    date_created            = None
    secret                  = None
    last_login              = None
    email_verification_code = None
    signup_email_sent       = None
    is_authenticated        = None
    is_active               = None
    is_anonymous            = None

    email_verified     = False
    two_factor_auth    = False
    two_factor_enabled = False

    def __init__( self, args ) :
        
        self.id                      = args['ID']
        self.email                   = args['email']
        self.password                = args['password']
        self.salt                    = args['salt']
        self.role                    = args['role']
        self.date_created            = args['date_created']
        self.secret                  = args['secret']
        self.last_login              = args['last_login']
        self.email_verification_code = args['email_verification_code']
        self.signup_email_sent       = args['signup_email_sent']
        self.is_authenticated        = True
        self.is_active               = True
        self.is_anonymous            = False

        if( int( args['email_verified'] ) == 1 ):
            self.email_verified = True

        if( session.get('two_factor_auth') ):
            self.two_factor_auth = True

        if( int( args['two_factor_enabled'] ) == 1 ):
            self.two_factor_enabled = True

    def get_id( self ):

        return str( self.id )
    
    def is_admin( self ):

        if( self.role == 'administrator' or self.role == 'superadministrator' ):
            return True
        
        return False
    
    def passed_two_factor_auth( self ):

        session['two_factor_auth'] = True
        self.two_factor_auth = True

        return self.two_factor_auth