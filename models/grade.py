"""
Grade Model - Handles all database operations for the module_grades table.
"""
from .base_model import BaseModel


class GradeModel(BaseModel):
    """Model for grade-related database operations."""
    
    TABLE_NAME = 'module_grades'
    
    def create(self, stud_id, mod_id, grade):
        """Create a new grade record."""
        query = """
            INSERT INTO module_grades (stud_id, mod_id, grade) 
            VALUES (%s, %s, %s)
        """
        self.execute_insert(query, (stud_id, mod_id, grade))
        return True
    
    def find_by_student(self, stud_id):
        """Get all grades for a student."""
        query = "SELECT * FROM module_grades WHERE stud_id = %s"
        return self.execute_query(query, (stud_id,))
    
    def find_by_module(self, mod_id):
        """Get all grades for a module."""
        query = "SELECT * FROM module_grades WHERE mod_id = %s"
        return self.execute_query(query, (mod_id,))
    
    def find_by_student_module(self, stud_id, mod_id):
        """Get grade for a specific student in a specific module."""
        query = "SELECT * FROM module_grades WHERE stud_id = %s AND mod_id = %s"
        results = self.execute_query(query, (stud_id, mod_id))
        return results[0] if results else None
    
    def get_average_grade(self, stud_id=None, mod_id=None):
        """Calculate average grade."""
        if stud_id and mod_id:
            query = "SELECT AVG(grade) FROM module_grades WHERE stud_id = %s AND mod_id = %s"
            params = (stud_id, mod_id)
        elif stud_id:
            query = "SELECT AVG(grade) FROM module_grades WHERE stud_id = %s"
            params = (stud_id,)
        elif mod_id:
            query = "SELECT AVG(grade) FROM module_grades WHERE mod_id = %s"
            params = (mod_id,)
        else:
            query = "SELECT AVG(grade) FROM module_grades"
            params = None
        
        result = self.execute_query(query, params)
        return float(result[0][0]) if result and result[0][0] else 0.0
    
    def update(self, stud_id, mod_id, new_grade):
        """Update a grade."""
        if not (0 <= new_grade <= 100):
            raise ValueError("Grade must be between 0 and 100")
        
        query = "UPDATE module_grades SET grade = %s WHERE stud_id = %s AND mod_id = %s"
        return self.execute_update(query, (new_grade, stud_id, mod_id))
    
    def delete(self, stud_id, mod_id):
        """Delete a grade."""
        query = "DELETE FROM module_grades WHERE stud_id = %s AND mod_id = %s"
        return self.execute_delete(query, (stud_id, mod_id))
