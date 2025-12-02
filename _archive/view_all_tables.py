import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': 'sql8.freesqldatabase.com',
    'database': 'sql8810071',
    'user': 'sql8810071',
    'password': 'QTS5mGlaDF',
    'port': 3306
}

def view_all_tables():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("DATABASE CONTENTS - ALL TABLES")
        print("=" * 80)
        
        tables = [
            'course',
            'users',
            'student',
            'module',
            'attendance',
            'surveys',
            'deadlines',
            'module_grades'
        ]
        
        for table_name in tables:
            print(f"\n{'='*80}")
            print(f"TABLE: {table_name.upper()}")
            print('='*80)
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if rows:
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                print(df.to_string(index=False))
                print(f"\nTotal rows: {len(rows)}")
            else:
                print("(empty table)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("END OF DATABASE CONTENTS")
        print("="*80)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_all_tables()
