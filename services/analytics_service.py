"""
Analytics Service - Handles complex aggregations and visualizations.
"""
from utils.db_connection import get_connection

class AnalyticsService:
    def __init__(self):
        self.conn, self.cursor = get_connection()

    def _execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    # --- Attendance Analytics ---

    def get_module_attendance_avg(self, mod_id):
        """Get average attendance percentage for a module."""
        # Calculate total attended / total sessions * 100
        # We need to consider 'missed' column: missed=0 is attended
        query = """
            SELECT 
                (SUM(CASE WHEN missed = 0 THEN 1 ELSE 0 END) / COUNT(*)) * 100 as avg_attendance
            FROM attendance
            WHERE mod_id = %s
        """
        result = self._execute(query, (mod_id,))
        return float(result[0][0]) if result and result[0][0] else 0.0

    def get_weekly_attendance_avg(self, mod_id, week_no):
        """Get average attendance for a specific week in a module."""
        query = """
            SELECT 
                (SUM(CASE WHEN missed = 0 THEN 1 ELSE 0 END) / COUNT(*)) * 100 as avg_attendance
            FROM attendance
            WHERE mod_id = %s AND week_no = %s
        """
        result = self._execute(query, (mod_id, week_no))
        return float(result[0][0]) if result and result[0][0] else 0.0

    def get_student_weekly_attendance_avg(self, stud_id):
        """Get average attendance per week for a student across all modules."""
        query = """
            SELECT week_no,
                (SUM(CASE WHEN missed = 0 THEN 1 ELSE 0 END) / COUNT(*)) * 100 as avg_attendance
            FROM attendance
            WHERE stud_id = %s
            GROUP BY week_no
            ORDER BY week_no
        """
        return self._execute(query, (stud_id,))

    # --- Grade Analytics ---

    def get_student_grade_avg(self, stud_id):
        """Get average grade for a student across all modules."""
        query = "SELECT AVG(grade) FROM module_grades WHERE stud_id = %s"
        result = self._execute(query, (stud_id,))
        return float(result[0][0]) if result and result[0][0] else 0.0

    def get_module_grade_avg(self, mod_id):
        """Get average grade for a module."""
        query = "SELECT AVG(grade) FROM module_grades WHERE mod_id = %s"
        result = self._execute(query, (mod_id,))
        return float(result[0][0]) if result and result[0][0] else 0.0

    # --- Visualization ---

    def _ensure_output_dir(self):
        import os
        if not os.path.exists('analytics_output'):
            os.makedirs('analytics_output')

    def generate_bar_chart_png(self, title, labels, values, filename):
        """Generate a bar chart and save as PNG."""
        try:
            import matplotlib.pyplot as plt
            import os
            
            self._ensure_output_dir()
            filepath = os.path.join('analytics_output', filename)
            
            plt.figure(figsize=(10, 6))
            plt.bar(labels, values, color='skyblue')
            plt.title(title)
            plt.ylabel('Value')
            plt.ylim(0, 100)
            
            # Add value labels on top
            for i, v in enumerate(values):
                plt.text(i, v + 1, f"{v:.1f}%", ha='center')
                
            plt.savefig(filepath)
            plt.close()
            return filepath
        except ImportError:
            return "Matplotlib not installed - cannot generate PNG"

    def generate_trend_chart_png(self, title, x_labels, y_values, filename):
        """Generate a line chart for trends and save as PNG."""
        try:
            import matplotlib.pyplot as plt
            import os
            
            self._ensure_output_dir()
            filepath = os.path.join('analytics_output', filename)
            
            plt.figure(figsize=(10, 6))
            plt.plot(x_labels, y_values, marker='o', linestyle='-', color='green')
            plt.title(title)
            plt.xlabel('Week')
            plt.ylabel('Attendance %')
            plt.ylim(0, 100)
            plt.grid(True)
            
            plt.savefig(filepath)
            plt.close()
            return filepath
        except ImportError:
            return "Matplotlib not installed - cannot generate PNG"

    def identify_at_risk_students(self, stress_threshold=4, sleep_threshold=6, grade_threshold=50):
        """
        Identify students who are at risk based on:
        - High stress (> threshold)
        - Low sleep (< threshold)
        - Low grades (< threshold)
        
        Returns list of dicts with student details and risk factors.
        """
        # This query joins surveys, grades, and users to find correlations
        query = """
            SELECT 
                u.user_id, u.user_name, u.email,
                AVG(s.stress_levels) as avg_stress,
                AVG(s.hours_slept) as avg_sleep,
                AVG(g.grade) as avg_grade
            FROM users u
            JOIN surveys s ON u.user_id = s.stud_id
            LEFT JOIN module_grades g ON u.user_id = g.stud_id
            GROUP BY u.user_id
            HAVING 
                avg_stress >= %s OR 
                avg_sleep <= %s OR 
                avg_grade <= %s
        """
        results = self._execute(query, (stress_threshold, sleep_threshold, grade_threshold))
        
        at_risk = []
        for r in results:
            at_risk.append({
                'student_id': r[0],
                'name': r[1],
                'email': r[2],
                'avg_stress': float(r[3]),
                'avg_sleep': float(r[4]),
                'avg_grade': float(r[5]) if r[5] else 0.0,
                'risk_factors': []
            })
            
            # Determine specific risks
            student = at_risk[-1]
            if student['avg_stress'] >= stress_threshold:
                student['risk_factors'].append('High Stress')
            if student['avg_sleep'] <= sleep_threshold:
                student['risk_factors'].append('Low Sleep')
            if student['avg_grade'] <= grade_threshold:
                student['risk_factors'].append('Low Grades')
                
        return at_risk
