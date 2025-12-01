from .base_model import BaseModel
class AttendanceModel(BaseModel):
    TABLE_NAME = 'attendance'
    def create(self, week_no, mod_id, stud_id, date, missed=False):
        query = """
            INSERT INTO attendance (week_no, mod_id, stud_id, date, missed) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_insert(query, (week_no, mod_id, stud_id, date, missed))
        return True
    def find_by_student(self, stud_id):
        query = "SELECT * FROM attendance WHERE stud_id = %s ORDER BY date DESC"
        return self.execute_query(query, (stud_id,))
    def find_by_module(self, mod_id):
        query = "SELECT * FROM attendance WHERE mod_id = %s ORDER BY date DESC"
        return self.execute_query(query, (mod_id,))
    def find_by_student_module(self, stud_id, mod_id):
        query = "SELECT * FROM attendance WHERE stud_id = %s AND mod_id = %s ORDER BY date DESC"
        return self.execute_query(query, (stud_id, mod_id))
    def get_attendance_stats(self, stud_id, mod_id):
        query_attended = """
            SELECT COUNT(*) as attended 
            FROM attendance 
            WHERE stud_id = %s AND mod_id = %s AND missed = FALSE
        """
        attended_result = self.execute_query(query_attended, (stud_id, mod_id))
        attended = attended_result[0][0] if attended_result else 0
        query_total = """
            SELECT COUNT(*) as total 
            FROM attendance 
            WHERE stud_id = %s AND mod_id = %s
        """
        total_result = self.execute_query(query_total, (stud_id, mod_id))
        total = total_result[0][0] if total_result else 0
        percentage = (attended / total * 100) if total > 0 else 0
        return {
            'attended': attended,
            'missed': total - attended,
            'total': total,
            'percentage': round(percentage, 2)
        }
    def update(self, mod_id, stud_id, date, new_week_no):
        query = """
            UPDATE attendance SET week_no = %s 
            WHERE mod_id = %s AND stud_id = %s AND date = %s
        """
        return self.execute_update(query, (new_week_no, mod_id, stud_id, date))
    def delete(self, mod_id, stud_id, date):
        query = "DELETE FROM attendance WHERE mod_id = %s AND stud_id = %s AND date = %s"
        return self.execute_delete(query, (mod_id, stud_id, date))
