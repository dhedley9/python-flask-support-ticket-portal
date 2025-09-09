from core.database import Database
from datetime import datetime

class Comments():

    def create_comment( ticket_id, user_id, content ):

        date = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )

        data = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'content': content,
            'date_created': date,
        }
        
        comment_id = Database.insert( 'comments', data )

        return comment_id
    
    def get_comments_by_ticket_id( ticket_id ):

        sql = 'SELECT ID, ticket_id, user_id, content, date_created FROM comments WHERE ticket_id = ? ORDER BY date_created ASC'

        value = [ticket_id]
        value = tuple( value )

        results  = Database.get_results( sql, value )
        comments = []

        for row in results:

            comment = {
                'ID': row[0],
                'ticket_id': row[1],
                'user_id': row[2],
                'content': row[3],
                'date_created': datetime.strptime( row[4], '%Y-%m-%d %H:%M:%S' ),
            }

            comments.append( comment )

        return comments
