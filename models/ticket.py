from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Ticket( Base ):

    __tablename__ = 'tickets'

    ID           = Column( Integer, primary_key=True )
    title        = Column( String, nullable=False )
    status       = Column( String, nullable=False )
    created_by   = Column( Integer, ForeignKey('users.ID'), nullable=False )
    date_created = Column( DateTime, nullable=False )
    last_updated = Column( DateTime, nullable=False )

    def __init__( self, args = None ):
        
        for key in args:
            setattr( self, key, args[key] )