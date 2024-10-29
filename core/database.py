import sqlite3

from sqlite3 import Error
from pathlib import Path

import core.config as config

class Database():

    """
    Class for handling all database interactions
    """

    def __get_connection():

        """
        INTERNAL - Open a connection to the database

        :return Connection object
        """

        file = config.abspath

        path = Path( file ).parent.absolute()

        sql_path = path / 'sql'
        db_path  = path / 'sql/database.db'

        if not sql_path.exists():
            sql_path.mkdir()

        conn = None

        try:
            conn = sqlite3.connect( db_path )
            return conn
        except Error as e:
            print(e)

    def create_default_tables() :

        """
        Create the database tables
        """

        sql = """ CREATE TABLE IF NOT EXISTS users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL,
            date_created DATETIME NOT NULL,
            secret VARCHAR(32),
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

        """
        Perform a database query

        :param sql - (string) the SQL query
        """

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        cursor.execute( sql )
        connection.close()
    
    def insert( table, data ):

        """
        Standardised method to insert some data into a database table, in a prepared query

        :param table - (string) the table name
        :param data - (dictionary) the data to insert, where key is the column

        :return int
        """

        # Get the column names
        columns = data.keys()
        columns = list( columns )
        columns = "', '".join( columns )

        # Get the values to insert
        values  = data.values()
        values  = tuple( values )

        # Generate a string of placeholders for the prepared query
        placeholders = ['?'] * len( values )
        placeholders = ", ".join( placeholders )

        # Create the query with placeholders
        sql  = "INSERT INTO " + table
        sql += " ('" + columns + "')"
        sql += " VALUES (" + placeholders + ")"

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        # Do the prepared query
        cursor.execute( sql, values )

        connection.commit()
        connection.close()

        # Return the inserted ID
        return cursor.lastrowid
    
    def update( table, data, where ):

        """
        Standardised method to update some data in a database table, in a prepared query

        :param table - (string) the table name
        :param data - (dictionary) the new data to update the table with, where key is the column
        :param where - (dictionary) the criteria to match records with, where key is the column

        :return True
        """

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

        # Assemble the query
        sql    = "UPDATE " + table + " SET " + columns + " WHERE " + conditions
        values = tuple( values )

        connection = Database.__get_connection()
        cursor     = connection.cursor()

        # Do the prepared query
        cursor.execute( sql, values )
        connection.commit()
        connection.close()
       
        return True
    
    def delete( table, where ):

        """
        Standardised method to delete some from a database table, in a prepared query

        :param table - (string) the table name
        :param where - (dictionary) the criteria to match records with, where key is the colum

        :return True
        """

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

        """
        Standardised method to retrieve a single row from the database

        :param sql - (string) the sql query
        :param value - (tuple) optional values for prepared queries

        :return list
        """

        connection = Database.__get_connection()
        cursor     = connection.cursor()
        result     = cursor.execute( sql, value ).fetchone()

        return result
    
    def get_results( sql, value = () ): 

        """
        Standardised method to retrieve a multiple rows from the database

        :param sql - (string) the sql query
        :param value - (tuple) optional values for prepared queries

        :return list
        """

        connection = Database.__get_connection()
        cursor     = connection.cursor()
        results    = cursor.execute( sql, value ).fetchall()

        return results
    
    def get_var( sql, value = () ):

        """
        Standardised method to retrieve a single value from the database

        :param sql - (string) the sql query
        :param value - (tuple) optional values for prepared queries

        :return string
        """

        result = Database.get_row( sql, value )
        return result[0]
