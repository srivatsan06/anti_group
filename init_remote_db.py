"""
Script to initialize the remote database with tables and seed data.
Run this ONCE to set up your FreeSQLDatabase instance.
"""
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
        
        # We need to temporarily modify the database connection to use remote settings
        # Import after setting config
        import mysql.connector
        import bcrypt
        from datetime import datetime, timedelta
        import random
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        print("✓ Connected successfully!")
        
        # Create tables using Definition_new logic
        print("\nCreating tables...")
        exec(open('Definition_new.py').read())
        
        print("✓ Tables should be created!")
        
        # Now run seed_data but we need to modify it to use our connection
        print("\nSeeding data...")
        print("⚠ Running modified seed script...")
        
        # We'll need to manually run the seeding since seed_data uses BuildConnection
        # Let's import and run it
        exec(open('seed_data.py').read().replace('from build_connection import BuildConnection', '').replace('db = BuildConnection()', '').replace('conn, cursor = db.make_connection()', ''))
        
        print("✓ Data seeded!")
        print("\n🎉 Remote database initialized successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Remote Database Initialization")
    print("=" * 60)
    
    response = input("\nThis will CREATE TABLES and SEED DATA on the remote database.\nContinue? (yes/no): ")
    
    if response.lower() == 'yes':
        init_remote_db()
    else:
        print("Cancelled.")
