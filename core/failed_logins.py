import math

from core.database import database
from models.failed_login import Failed_Login
from datetime import datetime

class Failed_Logins():

    def log_failed_login( ip_address ):

        date   = datetime.today()

        record = database.get_model( Failed_Login, { 'ip_address': ip_address } )

        # No previous record
        if record == None:

            data = {
                'ip_address': ip_address,
                'attempts': 1,
                'last_attempt': date 
            }

            record = Failed_Login( data )
            database.add_model( record )
        
        else:
            
            record.attempts     = record.attempts + 1
            record.last_attempt = date
    
    def is_ip_locked( ip_address ):

        record = database.get_model( Failed_Login, { 'ip_address': ip_address } )

        # No previous record
        if record == None:
            return False

        # Check if the last attempt was within the last 5 minutes
        now          = datetime.today()
        difference   = now - record.last_attempt

        if difference.total_seconds() > 300:
            return False

        # Check the number of attempts
        if int( record.attempts ) > 4:
            return True
        
        return False
    
    def clear_failed_logins( ip_address ):

        record = database.get_model( Failed_Login, { 'ip_address': ip_address } )

        if record != None:
            database.delete_model( record )

    def get_failed_logins():

        results = database.get_models( Failed_Login, {} )
        now     = datetime.today()

        for result in results:

            difference = now - result.last_attempt

            if difference.total_seconds() > 300:
                status = 'Unlocked'
            else:
                unlock_time = 300 - difference.total_seconds()
                unlock_time = math.ceil( unlock_time / 60 )

                if( unlock_time == 1 ):
                    status = 'Locked for ' + str( unlock_time ) + ' minute'
                else:
                    status = 'Locked for ' + str( unlock_time ) + ' minutes'

            result.status = status
        
        return results
