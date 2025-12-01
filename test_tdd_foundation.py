"""
TDD Foundation Test Suite
=========================

If we were starting this project from scratch using Test-Driven Development (TDD),
this is the file we would write FIRST.

It defines the core "Contract" of the application:
1. Users must be able to be registered securely (Passwords hashed).
2. Users must be able to authenticate (Login).
3. Invalid credentials must be rejected.
4. Role-based access must be enforced.

To run this: python -m unittest test_tdd_foundation.py
"""

import unittest
from unittest.mock import MagicMock, patch
import bcrypt

# In TDD, we import the modules we *intend* to create.
# Since they exist, we import them now.
from controllers.auth_controller import AuthController
from controllers.admin_controller import AdminController
from models.user import UserModel

class TestCoreIdentity(unittest.TestCase):
    """
    Tests the Identity Management (Authentication & Authorization).
    This is the foundation of the entire system.
    """

    def setUp(self):
        """
        Setup runs before EACH test.
        We mock the database so we can test LOGIC without a real DB.
        """
        # 1. Mock the User Model to intercept database calls
        self.mock_user_model = MagicMock(spec=UserModel)
        
        # 2. Initialize Controllers with the mocked model
        # (We patch the internal creation of UserModel if necessary, 
        # but here we'll inject it if the design allowed, or patch it)
        pass

    @patch('controllers.admin_controller.UserModel')
    def test_registration_hashes_password(self, MockUserModel):
        """
        CRITICAL REQUIREMENT: Passwords must be hashed before storage.
        """
        # Arrange
        # Setup the mock to return our specific mock instance
        mock_instance = MockUserModel.return_value
        mock_instance.create.return_value = True
        
        admin_controller = AdminController('ADMIN01', 'admin')
        
        # Act
        # Try to register a user with a plain text password
        plain_password = "my_secret_password"
        admin_controller.register_user(
            user_id="NEW001", 
            user_name="Test User", 
            role="student", 
            email="test@test.com", 
            password=plain_password
        )
        
        # Assert
        # Verify that 'create' was called
        args, _ = mock_instance.create.call_args
        
        # Args are: (user_id, user_name, role, hash_pass, email)
        # Note: We recently fixed the order to be hash_pass then email
        passed_hash = args[3] 
        
        # 1. Verify the passed password is NOT the plain text one
        self.assertNotEqual(passed_hash, plain_password)
        
        # 2. Verify it IS a valid bcrypt hash
        # bcrypt.checkpw throws error if not a valid hash format
        self.assertTrue(bcrypt.checkpw(plain_password.encode(), passed_hash))

    @patch('controllers.auth_controller.UserModel')
    def test_login_success(self, MockUserModel):
        """
        Requirement: Valid credentials should return user info.
        """
        # Arrange
        mock_instance = MockUserModel.return_value
        auth_controller = AuthController()
        
        # Simulate a user found in the database
        # Structure: (user_id, user_name, role, email, hash_pass)
        real_password = "password123"
        hashed_pw = bcrypt.hashpw(real_password.encode(), bcrypt.gensalt()).decode()
        
        mock_user_row = ('STU001', 'Alice', 'student', 'alice@test.com', hashed_pw)
        mock_instance.find_by_id.return_value = mock_user_row
        
        # Act
        user = auth_controller.login('STU001', real_password)
        
        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user['user_id'], 'STU001')
        self.assertEqual(user['role'], 'student')

    @patch('controllers.auth_controller.UserModel')
    def test_login_failure_wrong_password(self, MockUserModel):
        """
        Requirement: Invalid password must return None.
        """
        # Arrange
        mock_instance = MockUserModel.return_value
        auth_controller = AuthController()
        
        real_password = "password123"
        hashed_pw = bcrypt.hashpw(real_password.encode(), bcrypt.gensalt()).decode()
        
        mock_user_row = ('STU001', 'Alice', 'student', 'alice@test.com', hashed_pw)
        mock_instance.find_by_id.return_value = mock_user_row
        
        # Act
        user = auth_controller.login('STU001', 'WRONG_PASSWORD')
        
        # Assert
        self.assertIsNone(user)

    @patch('controllers.admin_controller.UserModel')
    def test_admin_only_action(self, MockUserModel):
        """
        Requirement: Non-admins cannot perform admin actions.
        """
        # Arrange
        # Create a controller for a 'student' role
        student_controller = AdminController('STU001', 'student')
        
        # Act & Assert
        # Expect a PermissionError (or whatever exception your app raises)
        with self.assertRaises(PermissionError):
            student_controller.register_user('NEW', 'Name', 'student', 'e@e.com', 'pass')

if __name__ == '__main__':
    unittest.main()
