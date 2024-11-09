from flask import session
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .base import Base

class User( Base ):

    __tablename__ = 'users'

    ID                      = Column( Integer, primary_key=True )
    email                   = Column( String, nullable=False, unique=True )
    password                = Column( String, nullable=False )
    salt                    = Column( String, nullable=False )
    role                    = Column( String, nullable=False )
    date_created            = Column( DateTime, nullable=False )
    secret                  = Column( String )
    last_login              = Column( DateTime )
    email_verification_code = Column( String )
    signup_email_sent       = Column( DateTime )
    email_verified          = Column( Boolean, default=False )
    two_factor_enabled      = Column( Boolean, default=False )

    is_authenticated        = True
    is_active               = True
    is_anonymous            = None

    two_factor_auth         = False

    def __init__( self, args = None ):
        
        for key in args:
            setattr( self, key, args[key] )
        
        self.is_authenticated        = True
        self.is_active               = True
        self.is_anonymous            = False

        self.has_passed_two_factor_auth()

    def get_id( self ):

        return str( self.ID )
    
    def is_admin( self ):

        if( self.role == 'administrator' or self.role == 'superadministrator' ):
            return True
        
        return False
    
    def passed_two_factor_auth( self ):

        session['two_factor_auth'] = True
        self.two_factor_auth       = True

        return self.two_factor_auth
    
    def has_passed_two_factor_auth( self ):

        if( self.two_factor_auth == None ):
            
            if( session.get('two_factor_auth') ):
                self.two_factor_auth = True
            else:
                self.two_factor_auth = False

        return self.two_factor_auth