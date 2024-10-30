from core.database import Database
from datetime import datetime

class Failed_Logins():

    def log_failed_login( ip_address ):

        date   = datetime.today().strftime( '%Y-%m-%d %H:%M:%S' )
        values = tuple( [ip_address] )

        sql = 'SELECT ID, ip_address, attempts, last_attempt FROM failed_logins WHERE ip_address = ?;'

        record = Database.get_row( sql, values )

        # No previous record
        if record == None:

            data = {
                'ip_address': ip_address,
                'attempts': 1,
                'last_attempt': date 
            }

            Database.insert( 'failed_logins', data )
        
        else:

            attempts = int( record[2] ) + 1
            
            data = {
                'attempts': attempts,
                'last_attempt': date
            }

            where = {
                'ID': record[0]
            }

            Database.update( 'failed_logins', data, where )
    
    def is_ip_locked( ip_address ):

        values = tuple( [ip_address] )

        sql = 'SELECT ID, ip_address, attempts, last_attempt FROM failed_logins WHERE ip_address = ?;'

        record = Database.get_row( sql, values )

        # No previous record
        if record == None:
            return False

        # Check if the last attempt was within the last 5 minutes
        last_attempt = datetime.strptime( record[3], '%Y-%m-%d %H:%M:%S' )
        now          = datetime.today()
        difference   = now - last_attempt

        if difference.total_seconds() > 300:
            return False

        # Check the number of attempts
        if int( record[2] ) > 4:
            return True
        
        return False
    
    def clear_failed_logins( ip_address ):

        where = {
            'ip_address': ip_address
        }

        Database.delete( 'failed_logins', where )
