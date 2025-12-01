"""
Drop All Tables Script - Safely drops all tables in the database.
Use this to reset the database completely.
"""
from build_connection import BuildConnection

db = BuildConnection()
conn, cursor = db.make_connection()

def drop_all_tables():
    """Drop all tables in the correct order (respecting foreign keys)."""
    
    print("=" * 60)
    print("DROPPING ALL TABLES")
    print("=" * 60)
    
    try:
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Get all table names
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        if not tables:
            print("\nNo tables found in database.")
            return
        
        print(f"\nFound {len(tables)} tables to drop:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
        
        # Drop each table
        print("\nDropping tables...")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
            print(f"  ✓ Dropped {table_name}")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("ALL TABLES DROPPED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python Definition_new.py   # Recreate tables")
        print("  python seed_data.py        # Populate with test data")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    # Confirmation prompt
    print("\n⚠️  WARNING: This will DELETE ALL TABLES in the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        drop_all_tables()
    else:
        print("Operation cancelled.")
