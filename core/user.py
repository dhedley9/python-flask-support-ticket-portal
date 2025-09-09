class User:

    id               = None
    email            = None 
    password         = None
    salt             = None
    role             = None
    date_created     = None
    last_login       = None
    is_authenticated = None
    is_active        = None
    is_anonymous     = None

    def __init__( self, args ) :

        self.id               = args['ID']
        self.email            = args['email']
        self.password         = args['password']
        self.salt             = args['salt']
        self.role             = args['role']
        self.date_created     = args['date_created']
        self.last_login       = args['last_login']
        self.is_authenticated = True
        self.is_active        = True
        self.is_anonymous     = False

    def get_id( self ):

        return str( self.id )
    
    def is_admin( self ):

        if( self.role == 'administrator' or self.role == 'superadministrator' ):
            return True
        
        return False