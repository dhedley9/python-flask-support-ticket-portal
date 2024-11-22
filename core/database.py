import core.config as config
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from flask import g, has_request_context

class Database():

    url           = None
    engine        = None
    auto_commit   = True

    def __init__( self, db_url = None ):

        if( db_url != None ):
            self.url = db_url
        else:
            self.url = config.db_url

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
        
        if( config.init_use_db_session is True ):
            
            if config.init_db_session:
                return config.init_db_session
            else:
                config.init_db_session = sessionmaker( bind = self.engine )()
                return config.init_db_session
        
        return sessionmaker( bind = self.engine )()
    
    def commit( self, session ):

        """
        Commit the changes to the session
        """

        if ( has_request_context() ) and ( self.auto_commit is True ):
            session.commit()
        elif ( config.init_use_db_session is True ) or ( self.auto_commit is False ):
            session.flush()
        else:
            session.commit()
            session.close()

    def close_session( self ):

        """
        Close the session
        """

        if( has_request_context() and hasattr( g, 'db_session' ) == True ):

            g.db_session.commit()
            g.db_session.close()
            delattr( g, 'db_session' )

        if( config.init_use_db_session is True ):

            if( config.init_db_session != None ):
                config.init_db_session.commit()
                config.init_db_session.close()
                config.init_db_session = None
    
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
    
    def get_models( self, model, filters = {}, order = {} ):
            
        """
        Get a list of models from the database
        """

        session = self.get_session()
        query   = session.query( model )

        # Apply filters to the query
        if( len( filters ) > 0 ):
            query = query.filter_by( **filters )
        
        # Apply ordering to the query
        if( 'order_by' in order ):

            order_by  = order['order_by']
            order_dir = 'asc'

            if( 'order_dir' in order ):
                order_dir = order['order_dir'].lower()
                        
            if( order_dir == 'desc' ):
                query = query.order_by( desc( order_by ) )
            else:
                query = query.order_by( asc( order_by ) )

        result = query.all()
        
        self.commit( session )

        return result

    def add_model( self, model ):

        """
        Add a new model to the database
        """

        session = self.get_session()

        session.add( model )

        self.commit( session )

    def update_model( self, model, args ):
            
        """
        Update a model in the database
        """

        session = self.get_session()

        for key in args:
            setattr( model, key, args[key] )

        self.commit( session )
    
    def delete_model( self, model ):
            
        """
        Delete a model from the database
        """

        session = self.get_session()

        session.delete( model )

        self.commit( session )

database = Database()