from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Failed_Login( Base ):

    __tablename__ = 'failed_logins'

    ID           = Column( Integer, primary_key=True )
    ip_address   = Column( String, nullable=False )
    attempts     = Column( Integer, default=0 )
    last_attempt = Column( DateTime, nullable=False )

    def __init__( self, args = None ):
        
        for key in args:
            setattr( self, key, args[key] )
    