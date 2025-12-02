import mysql.connector
import os
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
class DBConnection:
    def __init__(self):
        self._conn = None
        self._cursor = None
    def make_connection(self):
        try:
            if HAS_STREAMLIT and hasattr(st, 'secrets') and 'mysql' in st.secrets:
                config = {
                    'host': st.secrets['mysql']['host'],
                    'database': st.secrets['mysql']['database'],
                    'user': st.secrets['mysql']['user'],
                    'password': st.secrets['mysql']['password']
                }
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
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            print("Database connection closed.")
db_instance = DBConnection()
def get_connection():
    return db_instance.make_connection()
