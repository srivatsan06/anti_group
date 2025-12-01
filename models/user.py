from .base_model import BaseModel
class UserModel(BaseModel):
    TABLE_NAME = 'users'
    VALID_ROLES = ['module_staff', 'welfare_staff', 'admin', 'student']
    UPDATE_ALLOWED_COLUMNS = ['user_id', 'user_name', 'role', 'email']
    DELETE_ALLOWED_COLUMNS = ['user_name', 'role', 'email']
    def create(self, user_id, user_name, role, hash_pass, email=None):
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {self.VALID_ROLES}")
        check_query = "SELECT user_id FROM users WHERE user_id = %s"
        existing = self.execute_query(check_query, (user_id,))
        if existing:
            return False  
        insert_query = """
            INSERT INTO users (user_id, user_name, role, email, hash_pass) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_insert(insert_query, (user_id, user_name, role, email, hash_pass))
        return True
    def find_by_id(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    def find_by_name(self, user_name):
        query = "SELECT * FROM users WHERE user_name = %s"
        return self.execute_query(query, (user_name,))
    def find_all(self):
        query = "SELECT * FROM users"
        return self.execute_query(query)
    def find_by_role(self, role):
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {self.VALID_ROLES}")
        query = "SELECT * FROM users WHERE role = %s"
        return self.execute_query(query, (role,))
    def update(self, user_id, column, new_value):
        if column not in self.UPDATE_ALLOWED_COLUMNS:
            raise ValueError(f"Column '{column}' cannot be updated. Allowed: {self.UPDATE_ALLOWED_COLUMNS}")
        query = f"UPDATE users SET `{column}` = %s WHERE `user_id` = %s"
        return self.execute_update(query, (new_value, user_id))
    def delete(self, user_id):
        query = "DELETE FROM users WHERE `user_id` = %s"
        return self.execute_delete(query, (user_id,))
    def clear_column(self, user_id, column):
        if column not in self.DELETE_ALLOWED_COLUMNS:
            raise ValueError(f"Column '{column}' cannot be cleared. Allowed: {self.DELETE_ALLOWED_COLUMNS}")
        query = f"UPDATE users SET `{column}` = NULL WHERE `user_id` = %s"
        return self.execute_update(query, (user_id,))
    def authenticate(self, user_id, hash_pass):
        query = "SELECT * FROM users WHERE user_id = %s AND hash_pass = %s"
        results = self.execute_query(query, (user_id, hash_pass))
        return results[0] if results else None
