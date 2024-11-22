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
    client_id    = Column( Integer, ForeignKey('users.ID'), nullable=False )

    def __init__( self, args = None ):
        
        for key in args:
            setattr( self, key, args[key] )
    
    def get_number( self ):
        return '#{:06d}'.format( self.ID )
    
    def get_status_label( self ):

        statuses = {
            'active': 'Awaiting Staff Reply',
            'pending': 'Awaiting Client Reply',
            'complete': 'Resolved'
        }

        if self.status in statuses:
            return statuses[self.status]
        
        return self.status
    
    def get_date_created( self, format ='%Y-%m-%d %H:%M:%S' ):
        return self.date_created.strftime( format )
    
    def get_last_updated( self, format ='%Y-%m-%d %H:%M:%S' ):
        return self.last_updated.strftime( format )