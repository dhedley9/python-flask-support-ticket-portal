import sqlite3

from sqlite3 import Error
from pathlib import Path

import core.config as config

class Database():

    def __get_connection():

        file = config.abspath

        path = Path( file ).parent.absolute()
        path = str( path )
        path = path + '/sql/database.db'

        conn = None

        try:
            conn = sqlite3.connect( path )
            return conn
        except Error as e:
            print(e)

    def create_default_tables() :

        sql = """ CREATE TABLE IF NOT EXISTS users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL,
            date_created DATETIME NOT NULL,
            last_login DATETIME
        ); """

        Database.query( sql )

        sql = """ CREATE TABLE IF NOT EXISTS tickets (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            date_created DATETIME NOT NULL,
            last_updated DATETIME NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users(ID)
        ); """

        Database.query( sql )

        sql = """ CREATE TABLE IF NOT EXISTS comments (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content LONGTEXT NOT NULL,
            date_created DATETIME NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(ID),
            FOREIGN KEY (user_id) REFERENCES users(ID)
        ); """

        Database.query( sql )

    def query( sql ):

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        cursor.execute( sql )
        connection.close()
    
    def insert( table, data ):

        columns = data.keys()
        columns = list( columns )
        columns = "', '".join( columns )

        values  = data.values()
        values  = tuple( values )

        placeholders = ['?'] * len( values )
        placeholders = ", ".join( placeholders )

        sql  = "INSERT INTO " + table
        sql += " ('" + columns + "')"
        sql += " VALUES (" + placeholders + ")"

        # insert = []

        # for x in range(0, len( values ) ) :
        #     insert.append( ( x, values[x] ) )

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        cursor.execute( sql, values )

        print(f'Last row id : {cursor.lastrowid}')

        connection.commit()
        connection.close()
       
        return cursor.lastrowid
    
    def update( table, data, where ):

        columns    = []
        conditions = []
        values     = []

        for key in data:
            columns.append( key + ' = ?' )
            values.append( data[key] )

        for key in where:
            conditions.append( key + ' = ?' )
            values.append( where[key] )

        columns    = ", ".join( columns )
        conditions = " AND ".join( conditions )

        sql    = "UPDATE " + table + " SET " + columns + " WHERE " + conditions
        values = tuple( values )

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        cursor.execute( sql, values )
        connection.commit()
        connection.close()
       
        return True
    
    def delete( table, where ):

        conditions = []
        values     = []

        for key in where:
            conditions.append( key + ' = ?' )
            values.append( where[key] )

        conditions = " AND ".join( conditions )

        sql    = "DELETE FROM " + table + " WHERE " + conditions
        values = tuple( values )

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        cursor.execute( sql, values )
        connection.commit()
        connection.close()
       
        return True

    def get_row( sql, value = () ): 

        connection = Database.__get_connection()
        cursor     = connection.cursor()
        result     = cursor.execute( sql, value ).fetchone()

        return result
    
    def get_results( sql, value = () ): 

        connection = Database.__get_connection()
        cursor     = connection.cursor()
        results    = cursor.execute( sql, value ).fetchall()

        return results
    
    def get_var( sql, value = () ):

        result = Database.get_row( sql, value )
        return result[0]
