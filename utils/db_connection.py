"""
Database connection utility module.
Refactored from build_connection.py for better organization.
"""
import mysql.connector


class DBConnection:
    """Handles database connections for the application."""
    
    def __init__(self):
        self._conn = None
        self._cursor = None
    
    def make_connection(self):
        """
        Creates and returns a MySQL database connection and cursor.
        
        Returns:
            tuple: (connection, cursor) objects
            
        Raises:
            Exception: If connection fails
        """
        try:
            self._conn = mysql.connector.connect(
                host="localhost",       
                database="APP",        
                user="warlord",            
                password="Warlord@200206"  
            )
            self._cursor = self._conn.cursor(buffered=True)
            print("Connection Successfully made!!")
            return self._conn, self._cursor
        except Exception as e:
            print(f"ERROR: {e}")
            raise
    
    def close(self):
        """Close the database connection if open."""
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            print("Database connection closed.")


# Singleton instance for backward compatibility
db_instance = DBConnection()


def get_connection():
    """
    Convenience function to get a database connection.
    
    Returns:
        tuple: (connection, cursor) objects
    """
    return db_instance.make_connection()
