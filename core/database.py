import core.config as config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import g, has_request_context


class Database():

    url           = None
    engine        = None

    def __init__( self ):

        self.url    = config.db_url
        self.engine = create_engine( self.url )

    def create_tables( self, Base ):

        """
        Create the database tables
        """

        Base.metadata.create_all( self.engine )

    def get_session( self ):

        """
        Get a new session
        """

        if has_request_context():

            if hasattr( g, 'db_session' ):
                return g.db_session
            else:
                g.db_session = sessionmaker( bind = self.engine )()
                return g.db_session
        
        return sessionmaker( bind = self.engine )()
    
    def commit( self, session ):

        """
        Commit the changes to the session
        """

        if has_request_context():
            session.flush()
        else:
            session.commit()
            session.close()

    def close_session( self ):

        """
        Close the session
        """

        if( hasattr( g, 'db_session' ) == True ):

            g.db_session.commit()
            g.db_session.close()
            delattr( g, 'db_session' )
    
    def get_model( self, model, filters = {} ):

        """
        Get a model from the database
        """

        clean_filters = {}

        for key in filters:

            value = filters[key]

            if( value != None ):
                clean_filters[key] = filters[key]

        
        session = self.get_session()
        
        if( len( clean_filters ) == 0 ):
            result = session.query( model ).first()
        else:
            result = session.query( model ).filter_by( **clean_filters ).first()
        
        self.commit( session )

        return result
    
    def get_models( self, model, filters = {} ):
            
        """
        Get a list of models from the database
        """

        session = self.get_session()

        if( len( filters ) == 0 ):
            result = session.query( model ).all()
        else:
            result = session.query( model ).filter_by( **filters ).all()
        
        self.commit( session )

        return result

    def add_model( self, model ):

        """
        Add a new model to the database
        """

        session = self.get_session()

        session.add( model )

        self.commit( session )

    
    def delete_model( self, model ):
            
        """
        Delete a model from the database
        """

        session = self.get_session()

        session.delete( model )

        self.commit( session )

database = Database()