"""
User Model - Handles all database operations for the users table.
Extracted from CRUD_new.py Users class.
"""
from .base_model import BaseModel


class UserModel(BaseModel):
    """Model for user-related database operations."""
    
    TABLE_NAME = 'users'
    VALID_ROLES = ['module_staff', 'welfare_staff', 'admin', 'student']
    UPDATE_ALLOWED_COLUMNS = ['user_id', 'user_name', 'role', 'email']
    DELETE_ALLOWED_COLUMNS = ['user_name', 'role', 'email']
    
    def create(self, user_id, user_name, role, hash_pass, email=None):
        """
        Create a new user in the database.
        
        Args:
            user_id (str): Unique user ID
            user_name (str): User's name
            role (str): User role (must be in VALID_ROLES)
            hash_pass (str): Hashed password
            email (str, optional): User email
            
        Returns:
            bool: True if created, False if already exists
            
        Raises:
            ValueError: If role is invalid
        """
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {self.VALID_ROLES}")
        
        # Check if user already exists
        check_query = "SELECT user_id FROM users WHERE user_id = %s"
        existing = self.execute_query(check_query, (user_id,))
        
        if existing:
            return False  # User already exists
        
        # Insert new user
        insert_query = """
            INSERT INTO users (user_id, user_name, role, email, hash_pass) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_insert(insert_query, (user_id, user_name, role, email, hash_pass))
        return True
    
    def find_by_id(self, user_id):
        """
        Find a user by their ID.
        
        Args:
            user_id (str): User ID to search for
            
        Returns:
            tuple: User data or None if not found
        """
        query = "SELECT * FROM users WHERE user_id = %s"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def find_by_name(self, user_name):
        """
        Find users by name (may return multiple if names aren't unique).
        
        Args:
            user_name (str): User name to search for
            
        Returns:
            list: List of users matching the name
        """
        query = "SELECT * FROM users WHERE user_name = %s"
        return self.execute_query(query, (user_name,))
    
    def find_all(self):
        """
        Get all users from the database.
        
        Returns:
            list: All users
        """
        query = "SELECT * FROM users"
        return self.execute_query(query)
    
    def find_by_role(self, role):
        """
        Find all users with a specific role.
        
        Args:
            role (str): Role to filter by
            
        Returns:
            list: Users with the specified role
            
        Raises:
            ValueError: If role is invalid
        """
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {self.VALID_ROLES}")
        
        query = "SELECT * FROM users WHERE role = %s"
        return self.execute_query(query, (role,))
    
    def update(self, user_id, column, new_value):
        """
        Update a specific column for a user.
        
        Args:
            user_id (str): User ID to update
            column (str): Column name to update
            new_value: New value for the column
            
        Returns:
            int: Number of rows updated (0 if user not found)
            
        Raises:
            ValueError: If column is not allowed to be updated
        """
        if column not in self.UPDATE_ALLOWED_COLUMNS:
            raise ValueError(f"Column '{column}' cannot be updated. Allowed: {self.UPDATE_ALLOWED_COLUMNS}")
        
        query = f"UPDATE users SET `{column}` = %s WHERE `user_id` = %s"
        return self.execute_update(query, (new_value, user_id))
    
    def delete(self, user_id):
        """
        Delete a user from the database.
        
        Args:
            user_id (str): User ID to delete
            
        Returns:
            int: Number of rows deleted (0 if user not found)
        """
        query = "DELETE FROM users WHERE `user_id` = %s"
        return self.execute_delete(query, (user_id,))
    
    def clear_column(self, user_id, column):
        """
        Set a specific column to NULL for a user.
        
        Args:
            user_id (str): User ID
            column (str): Column to clear
            
        Returns:
            int: Number of rows updated
            
        Raises:
            ValueError: If column is not allowed to be cleared
        """
        if column not in self.DELETE_ALLOWED_COLUMNS:
            raise ValueError(f"Column '{column}' cannot be cleared. Allowed: {self.DELETE_ALLOWED_COLUMNS}")
        
        query = f"UPDATE users SET `{column}` = NULL WHERE `user_id` = %s"
        return self.execute_update(query, (user_id,))
    
    def authenticate(self, user_id, hash_pass):
        """
        Authenticate a user by ID and password.
        
        Args:
            user_id (str): User ID
            hash_pass (str): Hashed password to verify
            
        Returns:
            tuple: User data if authenticated, None otherwise
        """
        query = "SELECT * FROM users WHERE user_id = %s AND hash_pass = %s"
        results = self.execute_query(query, (user_id, hash_pass))
        return results[0] if results else None
