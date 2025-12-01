"""
Database connection utility module.
Refactored from build_connection.py for better organization.
Supports both local development and Streamlit Cloud deployment.
"""
import mysql.connector
import os

# Try to import streamlit for secrets management
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


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
            # Try to get config from Streamlit secrets (Cloud deployment)
            if HAS_STREAMLIT and hasattr(st, 'secrets') and 'mysql' in st.secrets:
                config = {
                    'host': st.secrets['mysql']['host'],
                    'database': st.secrets['mysql']['database'],
                    'user': st.secrets['mysql']['user'],
                    'password': st.secrets['mysql']['password']
                }
            # Fallback to hardcoded values (Local development)
            else:
                config = {
                    'host': 'localhost',
                    'database': 'APP',
                    'user': 'warlord',
                    'password': 'Warlord@200206'
                }
            
            self._conn = mysql.connector.connect(**config)
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
