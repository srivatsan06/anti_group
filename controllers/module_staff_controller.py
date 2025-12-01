from models import (StudentModel, ModuleModel, AttendanceModel, 
                     DeadlineModel, GradeModel, SurveyModel)
from services.analytics_service import AnalyticsService
from utils.db_connection import get_connection


class ModuleStaffController:
    """
    Controller for module staff operations with RBAC.
    """
    
    def __init__(self, current_user_id, current_user_role):
        self.current_user_id = current_user_id
        self.current_user_role = current_user_role
        
        # Initialize models
        conn, cursor = get_connection()
        self.student_model = StudentModel(conn, cursor)
        self.module_model = ModuleModel(conn, cursor)
        self.attendance_model = AttendanceModel(conn, cursor)
        self.deadline_model = DeadlineModel(conn, cursor)
        self.grade_model = GradeModel(conn, cursor)
        self.survey_model = SurveyModel(conn, cursor)
        self.analytics_service = AnalyticsService()
        
    def _check_role(self):
        if self.current_user_role not in ['module_staff', 'admin']:
            raise PermissionError("Unauthorized: Requires Module Staff or Admin role")

    def _check_module_access(self, mod_id):
        """Verify staff is assigned to this module (or is admin)."""
        self._check_role()
        if self.current_user_role == 'admin':
            return True
            
        # Check if staff is assigned to module
        module = self.module_model.find_by_id(mod_id)
        if not module:
            raise ValueError("Module not found")
            
        # module_staff_id is column 4 (0-indexed) based on previous inserts
        # (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id)
        if module[4] != self.current_user_id:
             raise PermissionError(f"You are not assigned to module {mod_id}")
        return True

    # --- Module Operations ---
    
    def get_my_modules(self):
        """Get modules assigned to this staff member."""
        self._check_role()
        return self.module_model.find_by_staff(self.current_user_id)

    def get_module_students(self, mod_id):
        """Get all students enrolled in a specific module with details."""
        self._check_module_access(mod_id)
        
        # Get module to find course_id
        module = self.module_model.find_by_id(mod_id)
        course_id = module[2]
        
        # Get students in that course with details
        return self.student_model.find_by_course_with_details(course_id)

    # --- Attendance Operations ---

    def record_attendance(self, week_no, mod_id, stud_id, date, missed=False):
        """Record attendance for a student."""
        self._check_module_access(mod_id)
        return self.attendance_model.create(week_no, mod_id, stud_id, date, missed)

    def update_attendance(self, mod_id, stud_id, date, new_week_no):
        """Update attendance record."""
        self._check_module_access(mod_id)
        return self.attendance_model.update(mod_id, stud_id, date, new_week_no)
        
    def get_module_attendance_analytics(self, mod_id):
        """Get attendance analytics for all students in a module."""
        self._check_module_access(mod_id)
        
        students = self.get_module_students(mod_id)
        analytics = []
        
        for student in students:
            stud_id = student[0]
            stats = self.attendance_model.get_attendance_stats(stud_id, mod_id)
            analytics.append({
                'student_id': stud_id,
                'stats': stats
            })
            
        return analytics

    # --- Grade Operations ---

    def add_grade(self, stud_id, mod_id, grade):
        """Add a grade for a student."""
        self._check_module_access(mod_id)
        return self.grade_model.create(stud_id, mod_id, grade)

    def update_grade(self, stud_id, mod_id, new_grade):
        """Update a student's grade."""
        self._check_module_access(mod_id)
        return self.grade_model.update(stud_id, mod_id, new_grade)

    def get_module_grades(self, mod_id):
        """Get all grades for a module."""
        self._check_module_access(mod_id)
        return self.grade_model.find_by_module(mod_id)
        
    def get_advanced_module_analytics(self, mod_id):
        """Get comprehensive analytics for a module with PNG charts."""
        self._check_module_access(mod_id)
        
        avg_attendance = self.analytics_service.get_module_attendance_avg(mod_id)
        avg_grade = self.analytics_service.get_module_grade_avg(mod_id)
        
        # Generate PNG Chart
        chart_path = self.analytics_service.generate_bar_chart_png(
            f"Module Analytics: {mod_id}",
            ['Attendance', 'Avg Grade'],
            [avg_attendance, avg_grade],
            f"module_{mod_id}_analytics.png"
        )
        
        return {
            'module_id': mod_id,
            'avg_attendance': avg_attendance,
            'avg_grade': avg_grade,
            'chart_path': chart_path
        }

    # --- Deadline Operations ---

    def create_deadline(self, mod_id, week_no, ass_name, due_date):
        """Create a new deadline."""
        self._check_module_access(mod_id)
        # stud_id is part of PK, but deadlines are usually per module.
        # The schema has (stud_id, mod_id, ass_name, due_date) as PK.
        # This implies assignments are assigned to specific students?
        # Or does the user want to assign to ALL students in the module?
        # Based on schema, we must insert for each student.
        
        students = self.get_module_students(mod_id)
        count = 0
        for student in students:
            stud_id = student[0]
            self.deadline_model.create(stud_id, mod_id, week_no, ass_name, due_date)
            count += 1
        return count

    def update_deadline(self, mod_id, ass_name, due_date, column, new_value):
        """Update deadline details for all students in the module."""
        self._check_module_access(mod_id)
        
        # We need to update for all students who have this assignment
        # This is a bulk update based on mod_id, ass_name, and OLD due_date
        # But the model's update takes specific PKs. 
        # Let's add a bulk update method to DeadlineModel or iterate.
        # Iterating is safer for now to ensure we hit the right records.
        students = self.get_module_students(mod_id)
        count = 0
        for student in students:
            stud_id = student[0]
            try:
                self.deadline_model.update(stud_id, mod_id, ass_name, due_date, column, new_value)
                count += 1
            except:
                pass 
        return count

    def delete_deadline(self, mod_id, ass_name, due_date):
        """Delete a deadline for all students in the module."""
        self._check_module_access(mod_id)
        
        students = self.get_module_students(mod_id)
        count = 0
        for student in students:
            stud_id = student[0]
            self.deadline_model.delete(stud_id, mod_id, ass_name, due_date)
            count += 1
        return count
