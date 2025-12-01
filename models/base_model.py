class BaseModel:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Query execution error: {e}")
            raise
    def execute_insert(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Insert error: {e}")
            raise
    def execute_update(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"Update error: {e}")
            raise
    def execute_delete(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"Delete error: {e}")
            raise
    def find_by_id(self, table, id_column, id_value):
        query = f"SELECT * FROM {table} WHERE {id_column} = %s"
        results = self.execute_query(query, (id_value,))
        return results[0] if results else None
    def find_all(self, table):
        query = f"SELECT * FROM {table}"
        return self.execute_query(query)
