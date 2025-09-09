from core.database import database
from models.ticket import Ticket
from datetime import datetime

class Tickets():

    """
    Class containing useful methods for tickets
    """

    def create_ticket( title, user_id, status = 'active' ):

        """
        Create a new ticket

        :param title - (string) the title of the ticket
        :param user_id - (int) the ID of the user creating the ticket
        :param status - (string) the status of the new ticket

        :return int
        """

        date = datetime.today()

        data = {
            'title': title,
            'status': status,
            'created_by': user_id,
            'date_created': date,
            'last_updated': date,
        }
        
        ticket = Ticket( data )

        database.add_model( ticket )

        return ticket.ID

    def update_ticket( ID, args ):

        """
        Update a ticket

        :param ID - (int) the ID of the ticket to update
        :param args - (dictionary) data to update

        :return boolean
        """

        ticket = Tickets.get_ticket( ID )

        # List of fields that can be updated
        allowed = ['title', 'status', 'created_by']
        updated = False

        for key in args:
            
            if key in allowed:
                setattr( ticket, key, args[key] )
                updated = True

        if updated:
            ticket.last_updated = datetime.today()
            database.commit()
            return True

        return False
    
    def delete_ticket( ID ):

        """
        Delete a ticket

        :param ID - (int) the ticket ID

        :return True
        """

        ticket = Tickets.get_ticket( ID )

        if ticket == False:
            return False
        
        database.delete_model( ticket )

        return True

    def get_tickets( args = {} ) :

        """
        Retrieve tickets based on a set of arguments

        :param args - (dictionary) arguments to filter returned tickets

        :return List
        """

        filters = {}

        # If filtering
        if( len( args ) > 0 ):

            # Fields that can be filtered by
            allowed = ['status', 'created_by']
            
            # Only include allowed arguments
            for key in args:

                if( key in allowed ):

                    filters[key] = args[key]

        return database.get_models( Ticket, filters )
    
    def get_ticket( ID ) :

        """
        Retrieve a single ticket

        :param ID - (int) the ticket ID

        :return dictionary OR False
        """ 

        return database.get_model( Ticket, { ID: ID } )
    
    def get_status_label( status ):

        """
        Get a status label from a status name

        :param status - (string) the status

        :return string
        """

        statuses = {
            'active': 'Awaiting Staff Reply',
            'pending': 'Awaiting Client Reply',
            'complete': 'Resolved'
        }

        if status in statuses:
            return statuses[status]
        
        return status