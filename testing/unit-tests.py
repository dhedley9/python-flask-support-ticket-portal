import unittest
import os, sys

# Retrieve the directory of the core application
main_dir = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
main_file = main_dir + '/app.py'

# Change the path so application files can be loaded
sys.path.append( main_dir )

import core.config as config

config.abspath = main_file

from core.tickets import Tickets
from core.comments import Comments
from core.users import Users
from core.database import Database

class TestTicketMethods( unittest.TestCase ):

    """
    Class for performing unit tests relating to tickets
    """

    def test_create( self ):

        """
        Test the Tickets.create_ticket method

        :param self
        """

        title   = 'unittest'
        user_id = 1
        status  = 'active'
        
        result = Tickets.create_ticket( title, user_id, status )

        is_int =  isinstance( result, int )

        self.assertTrue( is_int )

        Tickets.delete_ticket( result )
    
    def test_retrieve( self ):

        """
        Test the Tickets.get_tickets method

        :param self
        """

        title   = 'unittest'
        user_id = 1
        status  = 'active'
        
        ticket_id  = Tickets.create_ticket( title, user_id, status )

        results = Tickets.get_tickets()

        is_list = isinstance( results, list )

        self.assertTrue( is_list )
        self.assertTrue( len( results ) > 0 )

        result = results[-1]

        is_dict = isinstance( result, dict )

        self.assertTrue( is_dict )
        self.assertEqual( result['title'], 'unittest' )

        Tickets.delete_ticket( ticket_id )
    
    def test_retrieve_by_id( self ):

        """
        Test the Tickets.get_ticket method

        :param self
        """

        title   = 'unittest'
        user_id = 1
        status  = 'active'
        
        ticket_id = Tickets.create_ticket( title, user_id, status )

        results  = Tickets.get_tickets()
        result_1 = results[-1]
        result_2 = Tickets.get_ticket( result_1['ID'] )

        self.assertEqual( result_1, result_2 )

        Tickets.delete_ticket( ticket_id )

    def test_update( self ):

        """
        Test the Tickets.update_ticket method

        :param self
        """

        title   = 'unittest'
        user_id = 1
        status  = 'active'
        
        ticket_id = Tickets.create_ticket( title, user_id, status )

        args = {
            'title': 'unittestnew'
        }

        result = Tickets.update_ticket( ticket_id, args )

        tickets = Tickets.get_tickets()
        ticket  = tickets[-1]

        self.assertTrue( result )
        self.assertEqual( 'unittestnew', ticket['title'] )

        Tickets.delete_ticket( ticket_id )

    def test_delete( self ):

        """
        Test the Tickets.delete_ticket method

        :param self
        """

        title   = 'unittest'
        user_id = 1
        status  = 'active'
        
        ticket_id = Tickets.create_ticket( title, user_id, status )

        result = Tickets.delete_ticket( ticket_id )

        self.assertTrue( result )

    def test_get_status_label( self ):

        """
        Test the Tickets.get_status_label method

        :param self
        """

        self.assertEqual( Tickets.get_status_label('active'), 'Awaiting Staff Reply' )
        self.assertEqual( Tickets.get_status_label('pending'), 'Awaiting Client Reply' )
        self.assertEqual( Tickets.get_status_label('complete'), 'Resolved' )
        self.assertEqual( Tickets.get_status_label('notarealstatus'), 'notarealstatus' )

class TestCommentMethods( unittest.TestCase ):

    """
    Class for performing unit tests relating to comments
    """

    def test_comments( self ):

        """
        Test the Comments.create_comment and Comments.get_comments_by_ticket_id methods

        :param self
        """
        
        title   = 'unittest'
        user_id = 1
        status  = 'active'
        
        ticket_id = Tickets.create_ticket( title, user_id, status )

        comment_id = Comments.create_comment( ticket_id, user_id, title )

        self.assertTrue( comment_id )

        comments = Comments.get_comments_by_ticket_id( ticket_id )

        is_list = isinstance( comments, list )

        self.assertTrue( is_list )

        Database.delete( 'comments', { 'ID': comment_id } )
        Tickets.delete_ticket( ticket_id )

class TestUsersMethods( unittest.TestCase ):

    """
    Class for performing unit tests relating to users
    """

    def test_create_update_delete( self ):

        """
        Test the Users.create_user, Users.update_user, Users.get_user_by, Users.get_users and Users.delete_user methods

        :param self
        """
        
        email    = 'unittest@test.co.uk'
        password = 'test'
        role     = 'standard'

        user_id  = Users.create_user( email, password, role )

        self.assertTrue( user_id )

        update = { 'email': 'newunittest@test.co.uk' }

        result = Users.update_user( user_id, update )

        self.assertTrue( result )

        user_1 = Users.get_user_by( 'ID', user_id )
        user_2 = Users.get_user_by( 'email', 'newunittest@test.co.uk' )

        self.assertTrue( user_1 )
        self.assertTrue( user_2 )

        users = Users.get_users()

        self.assertTrue( users )

        result = Users.delete_user( user_id )

        self.assertTrue( result )
    
    def test_hash_password( self ):

        """
        Test the Users.hash_password method

        :param self
        """

        password = 'password'
        salt     = os.urandom( 32 )
        hash     = Users.hash_password( password, salt )

        self.assertNotEqual( hash, password )


    def test_sanitize_email( self ):

        """
        Test the Users.sanitize_email method

        :param self
        """

        self.assertEqual( Users.sanitize_email( 'UpPerCaseEmail@TEST.co.uk' ), 'uppercaseemail@test.co.uk' )
        self.assertEqual( Users.sanitize_email( '    emailwithwhitespace.co.uk   ' ), 'emailwithwhitespace.co.uk' )

    def test_validate_email( self ):

        """
        Test the Users.validate_email method

        :param self
        """

        self.assertTrue( Users.validate_email( 'test@test.co.uk' ) )
        self.assertFalse( Users.validate_email( 'notanemail' ) )


if __name__ == '__main__':
    unittest.main()