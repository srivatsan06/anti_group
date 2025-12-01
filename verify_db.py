"""
Verify database population by counting rows in each table.
"""
import mysql.connector

# Remote database credentials
DB_CONFIG = {
    'host': 'sql8.freesqldatabase.com',
    'user': 'sql8810071',
    'password': 'QTS5mGlaDF',
    'database': 'sql8810071',
    'port': 3306
}

def verify_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        tables = ['course', 'users', 'student', 'module', 'attendance', 'surveys', 'deadlines', 'module_grades']
        
        print("=" * 40)
        print("DATABASE VERIFICATION")
        print("=" * 40)
        print(f"{'TABLE':<15} | {'ROWS':<10}")
        print("-" * 28)
        
        total_rows = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<15} | {count:<10}")
            total_rows += count
            
        print("-" * 28)
        print(f"TOTAL RECORDS   | {total_rows}")
        print("=" * 40)
        
        if total_rows > 50:
            print("\n✅ Database seems fully populated!")
        else:
            print("\n⚠ Database seems empty or partially populated.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_db()
