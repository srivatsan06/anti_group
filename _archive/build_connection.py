import mysql.connector

class BuildConnection:
    def __init__(self):
        pass
    def make_connection(self):
        try:
            conn = mysql.connector.connect(
            host="localhost",       
            database="APP",        
            user="warlord",            
            password="Warlord@200206"  
            )
            cursor = conn.cursor(buffered=True)
            print("Connection Successfully made!! ")
            return conn, cursor
        except Exception as e:
            print("ERROR: ",e)

