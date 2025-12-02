from build_connection import BuildConnection
db = BuildConnection()
conn,cursor = db.make_connection()
from tabulate import tabulate
def table_view(cursor):
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]

    print(tabulate(rows, headers=col_names, tablefmt="grid"))

for table in ["course","student","users","module","attendance","surveys","deadlines", "module_grades"]:
    query = f"SELECT * FROM {table};"
    cursor.execute(query)
    print(f"Table: {table}")
    table_view(cursor)