from core.database import Database
from datetime import datetime

class Tickets():

    def create_ticket( title, user_id, status = 'active' ):

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

        allowed = ['title', 'status', 'created_by']
        clean   = {}
        where   = { 'ID': ID }

        for key in args:
            
            if key in allowed:
                clean[key] = args[key]

        if len( clean ) == 0:
            return False
        
        clean['last_updated'] = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )

        Database.update( 'tickets', clean, where )

        return True
    
    def delete_ticket( ID ):

        where = { 'ID': ID }

        Database.delete( 'tickets', where )

        return True

    def get_tickets( args = {} ) :

        sql    = 'SELECT ID, title, status, created_by, date_created, last_updated FROM tickets WHERE 1=1'
        values = []

        if( len( args ) > 0 ):

            allowed = ['status', 'created_by']
            
            for key in args:

                if( key in allowed ):

                    value = args[key]

                    sql += ' AND ' + key + ' = ?'
                    values.append( value )

        values  = tuple( values )
        results = Database.get_results( sql, values )
        tickets = []

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

        sql = 'SELECT ID, title, status, created_by, date_created, last_updated FROM tickets WHERE ID = ?'

        id  = int( id )
        id  = [id]
        id  = tuple( id )
        
        result = Database.get_row( sql, id )

        if( result == None ) :
            return False
            
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

        statuses = {
            'active': 'Awaiting Staff Reply',
            'pending': 'Awaiting Client Reply',
            'complete': 'Resolved'
        }

        if status in statuses:
            return statuses[status]
        
        return status