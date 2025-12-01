"""
Admin Controller - Business logic and RBAC for admin operations.
"""
from models import (UserModel, StudentModel, CourseModel, ModuleModel, 
                     AttendanceModel, SurveyModel, DeadlineModel, GradeModel)
from utils.db_connection import get_connection
import bcrypt


class AdminController:
    """
    Controller for admin operations with RBAC.
    
    RBAC Rules for Admin:
    - Full access to view and edit anything
    - Only role permitted to view users table
    - Only role permitted to register new users
    """
    
    def __init__(self, current_user_id, current_user_role):
        self.current_user_id = current_user_id
        self.current_user_role = current_user_role
        
        conn, cursor = get_connection()
        self.user_model = UserModel(conn, cursor)
        self.student_model = StudentModel(conn, cursor)
        self.course_model = CourseModel(conn, cursor)
        self.module_model = ModuleModel(conn, cursor)
        self.attendance_model = AttendanceModel(conn, cursor)
        self.survey_model = SurveyModel(conn, cursor)
        self.deadline_model = DeadlineModel(conn, cursor)
        self.grade_model = GradeModel(conn, cursor)

    def _check_admin(self):
        if self.current_user_role != 'admin':
            raise PermissionError("Unauthorized: Requires Admin role")

    # --- User Management (Admin Only) ---

    def register_user(self, user_id, user_name, role, email, password):
        """Register a new user."""
        self._check_admin()
        
        # Hash password
        hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        return self.user_model.create(user_id, user_name, role, email, hash_pass)

    def get_all_users(self):
        """View all users."""
        self._check_admin()
        return self.user_model.find_all()

    def delete_user(self, user_id):
        """Delete a user."""
        self._check_admin()
        return self.user_model.delete(user_id)

    def update_user(self, user_id, column, new_value):
        """Update user details."""
        self._check_admin()
        return self.user_model.update(user_id, column, new_value)

    # --- Course & Module Management ---

    def create_course(self, course_id, course_name):
        self._check_admin()
        return self.course_model.create(course_id, course_name)

    def create_module(self, mod_id, mod_name, course_id, welfare_id, module_id):
        self._check_admin()
        return self.module_model.create(mod_id, mod_name, course_id, welfare_id, module_id)

    # --- Universal Access ---
    # Admin can use methods from other controllers or access models directly.
    # Since Admin has full access, we can expose generic CRUD wrappers or specific logic.
    # For simplicity, we'll expose direct model access via specific methods if needed, 
    # but usually Admin uses the UI to perform specific actions that map to these models.
    
    # Example: Admin overriding a grade
    def override_grade(self, stud_id, mod_id, new_grade):
        self._check_admin()
        return self.grade_model.update(stud_id, mod_id, new_grade)
        
    # Example: Admin deleting a survey (moderation)
    def delete_survey(self, week_no, stud_id, mod_id):
        self._check_admin()
        return self.survey_model.delete(week_no, stud_id, mod_id)
