from core.database import Database
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

        date = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )

        data = {
            'title': title,
            'status': status,
            'created_by': user_id,
            'date_created': date,
            'last_updated': date,
        }
        
        ticket_id = Database.insert( 'tickets', data )

        return ticket_id

    def update_ticket( ID, args ):

        """
        Update a ticket

        :param ID - (int) the ID of the ticket to update
        :param args - (dictionary) data to update

        :return boolean
        """

        # List of fields that can be updated
        allowed = ['title', 'status', 'created_by']
        clean   = {}
        where   = { 'ID': ID }

        # Loop through and only include allowed fields
        for key in args:
            
            if key in allowed:
                clean[key] = args[key]

        # Make sure there are some updates to do
        if len( clean ) == 0:
            return False
        
        # Track this update's datetime
        clean['last_updated'] = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )

        # Update the record
        Database.update( 'tickets', clean, where )

        return True
    
    def delete_ticket( ID ):

        """
        Delete a ticket

        :param ID - (int) the ticket ID

        :return True
        """

        where = { 'ID': ID }

        Database.delete( 'tickets', where )

        return True

    def get_tickets( args = {} ) :

        """
        Retrieve tickets based on a set of arguments

        :param args - (dictionary) arguments to filter returned tickets

        :return List
        """

        sql    = 'SELECT ID, title, status, created_by, date_created, last_updated FROM tickets WHERE 1=1'
        values = []

        # If filtering
        if( len( args ) > 0 ):

            # Fields that can be filtered by
            allowed = ['status', 'created_by']
            
            # Only include allowed arguments
            for key in args:

                if( key in allowed ):

                    value = args[key]

                    sql += ' AND ' + key + ' = ?'
                    values.append( value )

        # Do the query
        values  = tuple( values )
        results = Database.get_results( sql, values )
        tickets = []

        # Organise results into standardised dictionaries
        for row in results:

            ticket = {
                'ID': row[0],
                'title': row[1],
                'status': row[2],
                'created_by': row[3],
                'date_created': datetime.strptime( row[4], '%Y-%m-%d %H:%M:%S' ),
                'last_updated': row[5],
                'number': '#{:06d}'.format( row[0] ),
                'status_label': Tickets.get_status_label( row[2] )
            }

            if ticket['last_updated'] != None:
                ticket['last_updated'] = datetime.strptime( ticket['last_updated'], '%Y-%m-%d %H:%M:%S' )

            tickets.append( ticket )

        return tickets
    
    def get_ticket( id ) :

        """
        Retrieve a single ticket

        :param id - (int) the ticket ID

        :return dictionary OR False
        """ 

        sql = 'SELECT ID, title, status, created_by, date_created, last_updated FROM tickets WHERE ID = ?'

        id  = int( id )
        id  = [id]
        id  = tuple( id )
        
        result = Database.get_row( sql, id )

        # Check there is a result
        if( result == None ) :
            return False
        
        # Organise the database row into a dictionary
        ticket = {
            'ID': result[0],
            'title': result[1],
            'status': result[2],
            'created_by': result[3],
            'date_created': result[4],
            'last_updated': result[5],
            'number': '#{:06d}'.format( result[0] ),
            'status_label': Tickets.get_status_label( result[2] )
        }

        return ticket
    
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