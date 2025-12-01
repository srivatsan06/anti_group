import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': 'sql8.freesqldatabase.com',
    'database': 'sql8810071',
    'user': 'sql8810071',
    'password': 'QTS5mGlaDF',
    'port': 3306
}

def view_table_schemas():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 100)
        print("DATABASE SCHEMA - ALL TABLES")
        print("=" * 100)
        
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
            print(f"\n{'='*100}")
            print(f"TABLE: {table_name.upper()}")
            print('='*100)
            
            cursor.execute(f"DESCRIBE {table_name}")
            schema = cursor.fetchall()
            
            df = pd.DataFrame(schema, columns=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'])
            print(df.to_string(index=False))
            
            print(f"\n--- Foreign Keys & Constraints for {table_name} ---")
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    CONSTRAINT_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}'
                AND TABLE_NAME = '{table_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            fks = cursor.fetchall()
            
            if fks:
                fk_df = pd.DataFrame(fks, columns=['Column', 'Constraint', 'References Table', 'References Column'])
                print(fk_df.to_string(index=False))
            else:
                print("No foreign keys")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*100)
        print("END OF SCHEMA INFORMATION")
        print("="*100)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    view_table_schemas()
