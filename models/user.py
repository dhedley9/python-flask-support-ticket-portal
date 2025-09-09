from flask import session
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .base import Base

class User( UserMixin, Base ):

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

    def __init__( self, args = None ):
        
        for key in args:
            setattr( self, key, args[key] )