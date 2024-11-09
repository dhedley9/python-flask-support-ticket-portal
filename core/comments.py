from core.database import database
from models.comment import Comment
from datetime import datetime

class Comments():

    """
    Class containing useful methods for comments
    """

    def create_comment( ticket_id, user_id, content ):

        """
        Create a new comment
        
        :param ticket_id: (int) ID of the ticket to add the comment to
        :param user_id: (int) ID of the user adding the comment
        :param content: (string) the comment content, should be sanitised

        :return comment_id
        """

        date = datetime.today()

        data = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'content': content,
            'date_created': date,
        }
        
        comment = Comment( data )

        database.add_model( comment )

        return comment.ID
    
    def get_comments_by_ticket_id( ticket_id ):

        """
        Retrieve all of a ticket's comments
        
        :param ticket_id: (int) ID of the ticket

        :return list - containing dictionaries
        """

        comments = database.get_models( Comment, { 'ticket_id': ticket_id } )

        return comments
