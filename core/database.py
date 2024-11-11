import core.config as config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import g, has_request_context


class Database():

    url           = None
    engine        = None

    def __init__( self ):

        self.url    = 'sqlite:///sql/database.db'
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

        if( has_request_context() == True ):
            
            if( hasattr( g, 'db_session' ) != False ):
                
                return {
                    'session': g.db_session,
                    'is_anonymous': False
                }

        session_maker = sessionmaker( bind = self.engine )
        session       = session_maker()
        is_anonymous  = True

        if( has_request_context() == True ):
            g.db_session = session
            is_anonymous = False

        return {
            'session': session,
            'is_anonymous': is_anonymous
        }

    def close_request( self ):

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

        
        session_data = self.get_session()
        session      = session_data['session']
        
        if( len( clean_filters ) == 0 ):
            result = session.query( model ).first()
        else:
            result = session.query( model ).filter_by( **clean_filters ).first()
        
        if( session_data['is_anonymous'] == True ):
            session.close()

        return result
    
    def get_models( self, model, filters = {} ):
            
        """
        Get a list of models from the database
        """

        session_data = self.get_session()
        session      = session_data['session']

        if( len( filters ) == 0 ):
            result = session.query( model ).all()
        else:
            result = session.query( model ).filter_by( **filters ).all()
        
        if( session_data['is_anonymous'] == True ):
            session.close()

        return result

    def add_model( self, model ):

        """
        Add a new model to the database
        """

        session_data = self.get_session()
        session      = session_data['session']

        session.add( model )

        if( session_data['is_anonymous'] == True ):
            session.commit()
            session.close()
        else:
            session.flush()

    
    def delete_model( self, model ):
            
        """
        Delete a model from the database
        """

        session_data = self.get_session()
        session      = session_data['session']

        session.delete( model )

        if( session_data['is_anonymous'] == True ):
            session.commit()
            session.close()
        else:    
            session.flush()

database = Database()