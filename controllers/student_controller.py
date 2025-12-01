"""
Student Controller - Business logic and RBAC for student operations.
Implements comprehensive role-based access control for student role.
"""
from models import (StudentModel, CourseModel, ModuleModel, AttendanceModel, 
                     SurveyModel, DeadlineModel, GradeModel)
from utils.db_connection import get_connection


class StudentController:
    """
    Controller for student-specific operations with RBAC.
    
    RBAC Rules for Students:
    - Can view their own data only
    - Can submit surveys
    - Can view their own modules (via course)
    - Can view their own deadlines
    - Can view their own grades and analytics
    - Can view their own attendance analytics
    """
    
    def __init__(self, current_user_id, current_user_role):
        """
        Initialize with current user context.
        
        Args:
            current_user_id (str): ID of currently logged-in user
            current_user_role (str): Role of currently logged-in user
        """
        self.current_user_id = current_user_id
        self.current_user_role = current_user_role
        
        # Initialize models
        conn, cursor = get_connection()
        self.student_model = StudentModel(conn, cursor)
        self.course_model = CourseModel(conn, cursor)
        self.module_model = ModuleModel(conn, cursor)
        self.attendance_model = AttendanceModel(conn, cursor)
        self.survey_model = SurveyModel(conn, cursor)
        self.deadline_model = DeadlineModel(conn, cursor)
        self.grade_model = GradeModel(conn, cursor)
    
    def _check_student_access(self, stud_id):
        """
        Verify student can only access their own data.
        
        Raises:
            PermissionError: If student tries to access another student's data
        """
        if self.current_user_role == 'student' and self.current_user_id != stud_id:
            raise PermissionError(f"Students can only access their own data")
    
    # --- Student Profile Operations ---
    
    def get_my_profile(self):
        """Get current student's profile (students only)."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can view student profiles")
        
        return self.student_model.find_by_id(self.current_user_id)
    
    def update_my_year(self, new_year):
        """Update current student's year (students only)."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can update their profile")
        
        return self.student_model.update(self.current_user_id, 'year', new_year)
    
    # --- Module Operations ---
    
    def get_my_modules(self):
        """Get modules for current student's course."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can view their modules")
        
        # Get student's course
        student = self.student_model.find_by_id(self.current_user_id)
        if not student:
            return []
        
        course_id = student[2]  # Assuming course_id is 3rd column
        return self.module_model.find_by_course(course_id)
    
    # --- Attendance Operations ---
    
    def get_my_attendance(self, mod_id=None, stud_id=None):
        """
        Get attendance records.
        
        RBAC:
            - Students: Can only view their own attendance
            - Staff/Admin: Can view any student's attendance
        """
        if stud_id is None:
            stud_id = self.current_user_id
        
        # RBAC check
        if self.current_user_role == 'student' and stud_id != self.current_user_id:
            raise PermissionError("Students can only view their own attendance")
        elif self.current_user_role not in ['student', 'module_staff', 'welfare_staff', 'admin']:
            raise PermissionError("Unauthorized role")
        
        if mod_id:
            return self.attendance_model.find_by_student_module(stud_id, mod_id)
        else:
            return self.attendance_model.find_by_student(stud_id)
    
    def get_my_attendance_analytics(self, mod_id, stud_id=None):
        """
        Get attendance statistics for a module.
        
        Args:
            mod_id: Module ID
            stud_id: Student ID (optional, defaults to current user for students)
        
        RBAC:
            - Students: Can only view their own attendance
            - Module Staff/Welfare Staff/Admin: Can view any student's attendance
        """
        # Determine which student's data to retrieve
        if stud_id is None:
            stud_id = self.current_user_id
        
        # RBAC check
        if self.current_user_role == 'student':
            # Students can only view their own data
            if stud_id != self.current_user_id:
                raise PermissionError("Students can only view their own attendance")
        elif self.current_user_role not in ['module_staff', 'welfare_staff', 'admin']:
            raise PermissionError("Unauthorized role")
        
        stats = self.attendance_model.get_attendance_stats(stud_id, mod_id)
        return {
            'module_id': mod_id,
            'student_id': stud_id,
            'attended': stats['attended'],
            'missed': stats['missed'],
            'total': stats['total'],
            'percentage': stats['percentage'],
            'message': f"Attended {stats['attended']}/{stats['total']} classes ({stats['percentage']}%)"
        }
    
    # --- Survey Operations ---
    
    def submit_survey(self, mod_id, stress_levels, hours_slept, week_no, comments='NO COMMENTS'):
        """Submit a wellbeing survey (students only)."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can submit surveys")
        
        from datetime import datetime
        date = datetime.now().date()
        
        return self.survey_model.create(
            week_no, self.current_user_id, mod_id, 
            stress_levels, hours_slept, date, comments
        )
    
    def get_my_surveys(self, mod_id=None, stud_id=None):
        """
        Get survey history.
        
        RBAC:
            - Students: Can only view their own surveys
            - Welfare Staff/Admin: Can view any student's surveys
        """
        if stud_id is None:
            stud_id = self.current_user_id
        
        # RBAC check
        if self.current_user_role == 'student' and stud_id != self.current_user_id:
            raise PermissionError("Students can only view their own surveys")
        elif self.current_user_role not in ['student', 'welfare_staff', 'admin']:
            raise PermissionError("Unauthorized role")
        
        if mod_id:
            return self.survey_model.find_by_student_module(stud_id, mod_id)
        else:
            return self.survey_model.find_by_student(stud_id)
    
    # --- Deadline Operations ---
    
    def get_my_deadlines(self, mod_id=None):
        """Get deadlines for current student."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can view their deadlines")
        
        if mod_id:
            return self.deadline_model.find_by_student_module(self.current_user_id, mod_id)
        else:
            return self.deadline_model.find_by_student(self.current_user_id)
    
    def get_upcoming_deadlines(self, days=7):
        """Get upcoming deadlines within specified days."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can view their deadlines")
        
        return self.deadline_model.find_upcoming(self.current_user_id, days)
    
    def mark_deadline_submitted(self, mod_id, ass_name, due_date):
        """Mark a deadline as submitted."""
        if self.current_user_role != 'student':
            raise PermissionError("Only students can mark deadlines")
        
        return self.deadline_model.mark_submitted(self.current_user_id, mod_id, ass_name, due_date)
    
    # --- Grade Operations ---
    
    def get_my_grades(self, mod_id=None, stud_id=None):
        """
        Get grades.
        
        RBAC:
            - Students: Can only view their own grades
            - Staff/Admin: Can view any student's grades
        """
        if stud_id is None:
            stud_id = self.current_user_id
        
        # RBAC check
        if self.current_user_role == 'student' and stud_id != self.current_user_id:
            raise PermissionError("Students can only view their own grades")
        elif self.current_user_role not in ['student', 'module_staff', 'welfare_staff', 'admin']:
            raise PermissionError("Unauthorized role")
        
        if mod_id:
            return self.grade_model.find_by_student_module(stud_id, mod_id)
        else:
            return self.grade_model.find_by_student(stud_id)
    
    def get_my_grade_analytics(self, stud_id=None):
        """
        Get grade analytics with module details.
        
        RBAC:
            - Students: Can only view their own analytics
            - Staff/Admin: Can view any student's analytics
        """
        if stud_id is None:
            stud_id = self.current_user_id
        
        # RBAC check
        if self.current_user_role == 'student' and stud_id != self.current_user_id:
            raise PermissionError("Students can only view their own analytics")
        elif self.current_user_role not in ['student', 'module_staff', 'welfare_staff', 'admin']:
            raise PermissionError("Unauthorized role")
        
        # Get all grades
        all_grades = self.grade_model.find_by_student(stud_id)
        
        if not all_grades:
            return {
                'student_id': stud_id,
                'average_grade': 0,
                'total_modules': 0,
                'modules': []
            }
        
        # Get module details for each grade
        modules_with_grades = []
        total_grade = 0
        
        for grade_record in all_grades:
            rec_stud_id, mod_id, grade = grade_record
            # Get module info
            module = self.module_model.find_by_id(mod_id)
            if module:
                mod_name = module[1]  # Assuming mod_name is 2nd column
                modules_with_grades.append({
                    'module_id': mod_id,
                    'module_name': mod_name,
                    'grade': grade
                })
                total_grade += grade
        
        avg_grade = total_grade / len(all_grades) if all_grades else 0
        
        return {
            'student_id': stud_id,
            'average_grade': round(avg_grade, 2),
            'total_modules': len(all_grades),
            'modules': modules_with_grades
        }
