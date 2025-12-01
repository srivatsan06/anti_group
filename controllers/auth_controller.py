"""
Authentication Controller - Handles user authentication and authorization.
Includes Role-Based Access Control (RBAC) enforcement.
"""
from models.user import UserModel
from utils.db_connection import get_connection


import bcrypt

class AuthController:
    """
    Controller for authentication and authorization logic.
    Enforces RBAC for the application.
    """
    
    RBAC_PERMISSIONS = {
        'admin': ['*'],  # Admin has all permissions
        'module_staff': [
            'view_students', 'view_attendance', 'edit_attendance',
            'view_grades', 'edit_grades', 'view_deadlines', 'edit_deadlines'
        ],
        'welfare_staff': [
            'view_students', 'view_attendance', 'view_surveys',
            'view_grades', 'view_deadlines'
        ],
        'student': [
            'view_own_data', 'submit_survey', 'view_own_deadlines',
            'view_own_grades', 'view_modules'
        ]
    }
    
    def __init__(self):
        """Initialize with database connection."""
        conn, cursor = get_connection()
        self.user_model = UserModel(conn, cursor)
        self._current_user = None
    
    def login(self, user_id, password):
        """
        Authenticate a user and set as current user.
        
        Args:
            user_id (str): User ID
            password (str): Plain text password
            
        Returns:
            dict: User info if login succeeds, None otherwise
        """
        # Get user by ID to retrieve the stored hash
        user = self.user_model.find_by_id(user_id)
        
        if user:
            # user tuple: (user_id, user_name, role, email, hash_pass)
            stored_hash = user[4]
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                self._current_user = {
                    'user_id': user[0],
                    'user_name': user[1],
                    'role': user[2],
                    'email': user[3]
                }
                return self._current_user
                
        return None
    
    def logout(self):
        """Log out the current user."""
        self._current_user = None
    
    def get_current_user(self):
        """
        Get the currently logged-in user.
        
        Returns:
            dict: Current user info or None
        """
        return self._current_user
    
    def check_permission(self, action, target_user_id=None):
        """
        Check if current user has permission for an action.
        
        Args:
            action (str): Action to check (e.g., 'edit_grades')
            target_user_id (str, optional): For student actions on own data
            
        Returns:
            bool: True if permitted, False otherwise
        """
        if not self._current_user:
            return False
        
        role = self._current_user['role']
        
        # Admin can do anything
        if role == 'admin' or '*' in self.RBAC_PERMISSIONS.get(role, []):
            return True
        
        # Check if action is in role's permissions
        if action in self.RBAC_PERMISSIONS.get(role, []):
            # For student-specific actions, verify they're accessing their own data
            if action.startswith('view_own_') or action == 'submit_survey':
                return target_user_id == self._current_user['user_id'] if target_user_id else True
            return True
        
        return False
    
    def require_permission(self, action, target_user_id=None):
        """
        Require a permission or raise an error.
        
        Args:
            action (str): Required action
            target_user_id (str, optional): Target user ID for owned resources
            
        Raises:
            PermissionError: If permission denied
        """
        if not self.check_permission(action, target_user_id):
            raise PermissionError(
                f"User '{self._current_user['user_id']}' with role '{self._current_user['role']}' "
                f"does not have permission to: {action}"
            )
    
    def require_role(self, *allowed_roles):
        """
        Require current user to have one of the specified roles.
        
        Args:
            *allowed_roles: Roles that are allowed
            
        Raises:
            PermissionError: If user doesn't have required role
        """
        if not self._current_user:
            raise PermissionError("Not authenticated")
        
        if self._current_user['role'] not in allowed_roles:
            raise PermissionError(
                f"Role '{self._current_user['role']}' not authorized. "
                f"Required one of: {allowed_roles}"
            )
    
    def register_user(self, user_id, user_name, role, hash_pass, email=None):
        """
        Register a new user (admin or module_staff only).
        
        Args:
            user_id (str): New user ID
            user_name (str): User name
            role (str): User role
            hash_pass (str): Hashed password
            email (str, optional): Email
            
        Returns:
            dict: Success/failure message
            
        Raises:
            PermissionError: If not authorized
        """
        # Only admin and module_staff can register users
        self.require_role('admin', 'module_staff')
        
        try:
            created = self.user_model.create(user_id, user_name, role, hash_pass, email)
            if created:
                return {'success': True, 'message': 'User registered successfully'}
            else:
                return {'success': False, 'message': 'User already exists'}
        except ValueError as e:
            return {'success': False, 'message': str(e)}
