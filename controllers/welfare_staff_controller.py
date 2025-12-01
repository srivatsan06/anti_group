from models import (StudentModel, ModuleModel, AttendanceModel, 
                     DeadlineModel, GradeModel, SurveyModel, CourseModel)
from services.analytics_service import AnalyticsService
from utils.db_connection import get_connection


class WelfareStaffController:
    """
    Controller for welfare staff operations with RBAC.
    """
    
    def __init__(self, current_user_id, current_user_role):
        self.current_user_id = current_user_id
        self.current_user_role = current_user_role
        
        conn, cursor = get_connection()
        self.student_model = StudentModel(conn, cursor)
        self.course_model = CourseModel(conn, cursor)
        self.module_model = ModuleModel(conn, cursor)
        self.attendance_model = AttendanceModel(conn, cursor)
        self.survey_model = SurveyModel(conn, cursor)
        self.grade_model = GradeModel(conn, cursor)
        self.deadline_model = DeadlineModel(conn, cursor)
        self.analytics_service = AnalyticsService()

    def _check_role(self):
        if self.current_user_role not in ['welfare_staff', 'admin']:
            raise PermissionError("Unauthorized: Requires Welfare Staff or Admin role")

    # --- View Operations (All Read-Only) ---

    def get_all_students(self):
        """View all students with full details."""
        self._check_role()
        # Use the detailed query from StudentModel (we might need to expose a generic one)
        # Or just use the one we added to StudentModel but for all students
        # Let's add a find_all_with_details to StudentModel first, or just do a custom query here via model
        # For now, let's assume we update StudentModel or use the existing find_all and enrich it
        # Actually, let's update StudentModel to have find_all_with_details
        return self.student_model.find_all_with_details()

    def get_at_risk_students(self):
        """Identify students in danger zone."""
        self._check_role()
        return self.analytics_service.identify_at_risk_students()

    def get_student_profile(self, stud_id):
        """View specific student profile."""
        self._check_role()
        return self.student_model.find_by_id(stud_id)

    def get_all_courses(self):
        """View all courses."""
        self._check_role()
        return self.course_model.find_all()

    def get_all_modules(self):
        """View all modules."""
        self._check_role()
        return self.module_model.find_all()

    # --- Survey Access ---

    def get_student_surveys(self, stud_id):
        """View surveys for a student."""
        self._check_role()
        return self.survey_model.find_by_student(stud_id)

    def get_survey_analytics(self):
        """Get overall stress and sleep averages."""
        self._check_role()
        avg_stress = self.survey_model.get_average_stress()
        avg_sleep = self.survey_model.get_average_sleep()
        return {
            'average_stress': round(avg_stress, 2),
            'average_sleep': round(avg_sleep, 2)
        }

    # --- Attendance Access ---

    def get_student_attendance(self, stud_id):
        """View attendance for a student."""
        self._check_role()
        return self.attendance_model.find_by_student(stud_id)

    def get_attendance_analytics(self, stud_id, mod_id):
        """View attendance stats for a student in a module."""
        self._check_role()
        return self.attendance_model.get_attendance_stats(stud_id, mod_id)

    # --- Grade Access ---

    def get_student_grades(self, stud_id):
        """View grades for a student."""
        self._check_role()
        return self.grade_model.find_by_student(stud_id)

    def get_grade_analytics(self, stud_id=None):
        """View grade analytics (overall or per student)."""
        self._check_role()
        avg = self.grade_model.get_average_grade(stud_id=stud_id)
        return {'average_grade': round(avg, 2)}

    def get_student_comprehensive_report(self, stud_id):
        """Get a full report for a student including attendance trends as PNG."""
        self._check_role()
        
        # Weekly attendance trend
        weekly_att = self.analytics_service.get_student_weekly_attendance_avg(stud_id)
        # weekly_att is list of (week, avg)
        weeks = [f"Week {w[0]}" for w in weekly_att]
        att_values = [float(w[1]) for w in weekly_att]
        
        # Overall grade
        avg_grade = self.analytics_service.get_student_grade_avg(stud_id)
        
        # Generate Charts
        trend_chart = self.analytics_service.generate_trend_chart_png(
            f"Attendance Trend: {stud_id}",
            weeks,
            att_values,
            f"student_{stud_id}_trend.png"
        )
        
        return {
            'student_id': stud_id,
            'avg_grade': avg_grade,
            'weekly_attendance': weekly_att,
            'chart_path': trend_chart
        }

    # --- Module Analytics (Similar to Module Staff) ---

    def get_module_analytics(self, mod_id):
        """Get analytics for a specific module."""
        self._check_role()
        
        avg_attendance = self.analytics_service.get_module_attendance_avg(mod_id)
        avg_grade = self.analytics_service.get_module_grade_avg(mod_id)
        
        # Generate PNG Chart
        chart_path = self.analytics_service.generate_bar_chart_png(
            f"Module Analytics: {mod_id}",
            ['Attendance', 'Avg Grade'],
            [avg_attendance, avg_grade],
            f"welfare_module_{mod_id}_analytics.png"
        )
        
        return {
            'module_id': mod_id,
            'avg_attendance': avg_attendance,
            'avg_grade': avg_grade,
            'chart_path': chart_path
        }

    def get_survey_details(self, stud_id=None):
        """Get detailed survey information, optionally for a specific student."""
        self._check_role()
        
        if stud_id:
            # Surveys for specific student
            return self.survey_model.find_by_student(stud_id)
        else:
            # All surveys
            return self.survey_model.find_all()
