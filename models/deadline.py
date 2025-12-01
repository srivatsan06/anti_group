"""
Deadline Model - Handles all database operations for the deadlines table.
"""
from .base_model import BaseModel


class DeadlineModel(BaseModel):
    """Model for deadline-related database operations."""
    
    TABLE_NAME = 'deadlines'
    
    def create(self, stud_id, mod_id, week_no, ass_name, due_date, submitted=False):
        """Create a new deadline."""
        query = """
            INSERT INTO deadlines (stud_id, mod_id, week_no, ass_name, due_date, Submitted) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute_insert(query, (stud_id, mod_id, week_no, ass_name, due_date, submitted))
        return True
    
    def find_by_student(self, stud_id):
        """Get all deadlines for a student."""
        query = "SELECT * FROM deadlines WHERE stud_id = %s ORDER BY due_date ASC"
        return self.execute_query(query, (stud_id,))
    
    def find_by_module(self, mod_id):
        """Get all deadlines for a module."""
        query = "SELECT * FROM deadlines WHERE mod_id = %s ORDER BY due_date ASC"
        return self.execute_query(query, (mod_id,))
    
    def find_by_student_module(self, stud_id, mod_id):
        """Get deadlines for a specific student in a specific module."""
        query = "SELECT * FROM deadlines WHERE stud_id = %s AND mod_id = %s ORDER BY due_date ASC"
        return self.execute_query(query, (stud_id, mod_id))
    
    def find_upcoming(self, stud_id, days=7):
        """Get upcoming deadlines for a student within specified days."""
        query = """
            SELECT * FROM deadlines 
            WHERE stud_id = %s AND due_date >= CURDATE() AND due_date <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY due_date ASC
        """
        return self.execute_query(query, (stud_id, days))
    
    def mark_submitted(self, stud_id, mod_id, ass_name, due_date):
        """Mark a deadline as submitted."""
        query = """
            UPDATE deadlines SET Submitted = TRUE 
            WHERE stud_id = %s AND mod_id = %s AND ass_name = %s AND due_date = %s
        """
        return self.execute_update(query, (stud_id, mod_id, ass_name, due_date))
    
    def update(self, stud_id, mod_id, ass_name, due_date, column, new_value):
        """Update a deadline field."""
        allowed_columns = ['week_no', 'due_date', 'Submitted']
        if column not in allowed_columns:
            raise ValueError(f"Column '{column}' cannot be updated")
        
        query = f"""
            UPDATE deadlines SET `{column}` = %s 
            WHERE stud_id = %s AND mod_id = %s AND ass_name = %s AND due_date = %s
        """
        return self.execute_update(query, (new_value, stud_id, mod_id, ass_name, due_date))
    
    def delete(self, stud_id, mod_id, ass_name, due_date):
        """Delete a deadline."""
        query = "DELETE FROM deadlines WHERE stud_id = %s AND mod_id = %s AND ass_name = %s AND due_date = %s"
        return self.execute_delete(query, (stud_id, mod_id, ass_name, due_date))
