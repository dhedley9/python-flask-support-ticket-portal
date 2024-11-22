from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Comment( Base ):

    __tablename__ = 'comments'

    ID           = Column( Integer, primary_key=True )
    ticket_id    = Column( Integer, ForeignKey('tickets.ID'), nullable=False )
    user_id      = Column( Integer, ForeignKey('users.ID'), nullable=False )
    content      = Column( String, nullable=False )
    date_created = Column( DateTime, nullable=False )
    
    def __init__( self, args = None ):
        
        for key in args:
            setattr( self, key, args[key] )

    def get_user( self ):

        from core.users import Users

        return Users.get_user_by( 'ID', self.user_id )