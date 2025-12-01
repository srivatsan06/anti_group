"""
Script to initialize the remote database with tables and seed data.
Run this ONCE to set up your FreeSQLDatabase instance.
"""
import mysql.connector
import sys

# Remote database credentials
DB_CONFIG = {
    'host': 'sql8.freesqldatabase.com',
    'user': 'sql8810071',
    'password': 'QTS5mGlaDF',
    'database': 'sql8810071',
    'port': 3306
}

def init_remote_db():
    """Initialize the remote database."""
    try:
        print("Connecting to remote database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        
        # Import table definitions
        print("\nCreating tables...")
        from Definition_new import TableDefinition
        
        # Create a custom definition that uses our remote connection
        class RemoteTableDefinition(TableDefinition):
            def __init__(self, conn, cursor):
                self.conn = conn
                self.cursor = cursor
        
        table_def = RemoteTableDefinition(conn, cursor)
        table_def.table_definition()
        
        print("✓ Tables created!")
        
        # Seed data
        print("\nSeeding data...")
        from seed_data import seed_all_data
        seed_all_data()
        
        print("✓ Data seeded!")
        print("\n🎉 Remote database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Remote Database Initialization")
    print("=" * 60)
    
    response = input("\nThis will CREATE TABLES and SEED DATA on the remote database.\nContinue? (yes/no): ")
    
    if response.lower() == 'yes':
        init_remote_db()
    else:
        print("Cancelled.")
