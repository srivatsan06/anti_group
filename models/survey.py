from .base_model import BaseModel
class SurveyModel(BaseModel):
    TABLE_NAME = 'surveys'
    def create(self, week_no, stud_id, mod_id, stress_levels, hours_slept, date, comments='NO COMMENTS'):
        query = """
            INSERT INTO surveys (week_no, stud_id, mod_id, stress_levels, hours_slept, comments, date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.execute_insert(query, (week_no, stud_id, mod_id, stress_levels, hours_slept, comments, date))
        return True
    def find_by_student(self, stud_id):
        query = "SELECT * FROM surveys WHERE stud_id = %s ORDER BY date DESC"
        return self.execute_query(query, (stud_id,))
    def find_by_module(self, mod_id):
        query = "SELECT * FROM surveys WHERE mod_id = %s ORDER BY date DESC"
        return self.execute_query(query, (mod_id,))
    def find_by_student_module(self, stud_id, mod_id):
        query = "SELECT * FROM surveys WHERE stud_id = %s AND mod_id = %s ORDER BY date DESC"
        return self.execute_query(query, (stud_id, mod_id))
    def find_all(self):
        query = "SELECT * FROM surveys ORDER BY date DESC"
        return self.execute_query(query)
    def get_average_stress(self, stud_id=None, mod_id=None):
        if stud_id and mod_id:
            query = "SELECT AVG(stress_levels) FROM surveys WHERE stud_id = %s AND mod_id = %s"
            params = (stud_id, mod_id)
        elif stud_id:
            query = "SELECT AVG(stress_levels) FROM surveys WHERE stud_id = %s"
            params = (stud_id,)
        elif mod_id:
            query = "SELECT AVG(stress_levels) FROM surveys WHERE mod_id = %s"
            params = (mod_id,)
        else:
            query = "SELECT AVG(stress_levels) FROM surveys"
            params = None
        result = self.execute_query(query, params)
        return float(result[0][0]) if result and result[0][0] else 0.0
    def get_average_sleep(self, stud_id=None, mod_id=None):
        if stud_id and mod_id:
            query = "SELECT AVG(hours_slept) FROM surveys WHERE stud_id = %s AND mod_id = %s"
            params = (stud_id, mod_id)
        elif stud_id:
            query = "SELECT AVG(hours_slept) FROM surveys WHERE stud_id = %s"
            params = (stud_id,)
        elif mod_id:
            query = "SELECT AVG(hours_slept) FROM surveys WHERE mod_id = %s"
            params = (mod_id,)
        else:
            query = "SELECT AVG(hours_slept) FROM surveys"
            params = None
        result = self.execute_query(query, params)
        return float(result[0][0]) if result and result[0][0] else 0.0
    def update(self, week_no, stud_id, mod_id, column, new_value):
        allowed_columns = ['stress_levels', 'hours_slept', 'comments']
        if column not in allowed_columns:
            raise ValueError(f"Column '{column}' cannot be updated")
        query = f"""
            UPDATE surveys SET `{column}` = %s 
            WHERE week_no = %s AND stud_id = %s AND mod_id = %s
        """
        return self.execute_update(query, (new_value, week_no, stud_id, mod_id))
    def delete(self, week_no, stud_id, mod_id):
        query = "DELETE FROM surveys WHERE week_no = %s AND stud_id = %s AND mod_id = %s"
        return self.execute_delete(query, (week_no, stud_id, mod_id))
