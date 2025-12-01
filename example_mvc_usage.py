"""
Example demonstrating the new MVC architecture.
Shows how to use models and controllers with RBAC.
"""
from controllers.auth_controller import AuthController
from models.user import UserModel
from utils.db_connection import get_connection


def example_usage():
    """Demonstrate MVC usage with RBAC."""
    
    # 1. Authentication Example
    print("=" * 50)
    print("1. AUTHENTICATION EXAMPLE")
    print("=" * 50)
    
    auth = AuthController()
    
    # Try to login as admin
    print("\nAttempting admin login...")
    user = auth.login('TEST_ADM', 'pass')  # Replace with actual hash
    if user:
        print(f"✓ Logged in as: {user['user_name']} (Role: {user['role']})")
    else:
        print("✗ Login failed")
    
    # 2. RBAC Permission Check Example
    print("\n" + "=" * 50)
    print("2. RBAC PERMISSION CHECK")
    print("=" * 50)
    
    if auth.check_permission('edit_grades'):
        print("✓ Admin can edit grades")
    else:
        print("✗ Admin cannot edit grades")
    
    # 3. Model Usage Example (Direct DB access)
    print("\n" + "=" * 50)
    print("3. MODEL USAGE (Direct DB Access)")
    print("=" * 50)
    
    conn, cursor = get_connection()
    user_model = UserModel(conn, cursor)
    
    # Get all users
    print("\nFetching all users...")
    all_users = user_model.find_all()
    for user in all_users:
        print(f"  - {user[0]}: {user[1]} ({user[2]})")
    
    # Find user by role
    print("\nFetching students...")
    students = user_model.find_by_role('student')
    for student in students:
        print(f"  - {student[0]}: {student[1]}")
    
    # 4. Protected Action Example
    print("\n" + "=" * 50)
    print("4. PROTECTED ACTION")
    print("=" * 50)
    
    try:
        # Only admin/module_staff can register users
        result = auth.register_user(
            user_id='NEW_USER',
            user_name='New User',
            role='student',
            hash_pass='hashed_password',
            email='newuser@example.com'
        )
        print(f"Registration: {result['message']}")
    except PermissionError as e:
        print(f"✗ Permission denied: {e}")
    
    # Logout
    auth.logout()
    print("\n✓ Logged out")


if __name__ == "__main__":
    example_usage()
