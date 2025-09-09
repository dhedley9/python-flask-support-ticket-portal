from core import config
from core.database import database
from core.users import Users
from core.tickets import Tickets
from core.comments import Comments

from models import Base

class Init:

    def run( self ):

        # Create the database tables
        database.create_tables( Base )

        # Create a database session for all our initialisation tasks
        config.init_use_db_session = True

        # Create the default admin user
        self.create_admin_user()

        # Close the session
        database.close_session()

        # Reset the session flag
        config.init_use_db_session = False
    
    def create_admin_user( self ):

        # Create the default admin user, if it doesn't exist
        if Users.admin_user_exists() == False:

            admin_id = Users.create_user( config.default_admin_email, config.default_admin_password, 'administrator' )    

            print( 'created admin', admin_id )

            Users.update_user( admin_id, { 'email_verified': 1 } )

    def create_default_tickets( self, user_id ):

        ticket_id = Tickets.create_ticket( 'Homepage Not Loading Correctly on Mobile Devices', user_id )
        Comments.create_comment( ticket_id, user_id, 'The homepage is not displaying properly on mobile devices. Our clients have reported that some images and text appear misaligned, and the header menu is not responsive. Can you please check and fix the layout issues? The desktop version seems fine.' )

        ticket_id = Tickets.create_ticket( 'Contact Form Submissions Not Received', user_id )
        Comments.create_comment( ticket_id, user_id, 'We’ve noticed that contact form submissions are not coming through. Some customers have mentioned submitting inquiries, but we haven’t received any emails. Could you investigate and ensure the form is connected correctly and emails are being sent without issues?' )

        ticket_id = Tickets.create_ticket( 'Need to Update Website Footer with New Company Info', user_id )
        Comments.create_comment( ticket_id, user_id, 'Our company address and phone number have changed, and we need to update the footer on all pages with this new information. Can you make the necessary changes and ensure it’s consistent across the site?' )