import core.config as config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Database():

    url           = None
    engine        = None
    session_maker = None
    session       = None

    def __init__( self ):

        self.url           = 'sqlite:///sql/database.db'
        self.engine        = create_engine( self.url )
        self.session_maker = sessionmaker( bind=self.engine )
        pass

    def create_tables( self, Base ):

        """
        Create the database tables
        """

        Base.metadata.create_all( self.engine )

    def create_session( self ):

        """
        Create a new session
        """

        self.session = self.session_maker()

    def close_session( self ):

        """
        Close the session
        """

        self.session.close()
    
    def get_model( self, model, filters = {} ):

        """
        Get a model from the database
        """

        return self.session.query( model ).filter_by( **filters ).first()
    
    def get_models( self, model, filters = {} ):
            
        """
        Get a list of models from the database
        """

        return self.session.query( model ).filter_by( **filters ).all()

    def add_model( self, model ):

        """
        Add a new model to the database
        """

        self.session.add( model )
        self.commit()
    
    def delete_model( self, model ):
            
        """
        Delete a model from the database
        """

        self.session.delete( model )
        self.commit()
    
    def commit( self ):

        """
        Commit the session
        """

        self.session.commit()

database = Database()