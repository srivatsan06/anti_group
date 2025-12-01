"""
Student Model - Handles all database operations for the student table.
"""
from .base_model import BaseModel


class StudentModel(BaseModel):
    """Model for student-related database operations."""
    
    TABLE_NAME = 'student'
    
    def create(self, stud_id, year, course_id):
        """
        Create a new student record.
        
        Args:
            stud_id (str): Student ID (must reference users table with 'student' role)
            year (int): Academic year
            course_id (str): Course ID
            
        Returns:
            bool: True if created successfully
        """
        query = """
            INSERT INTO student (stud_id, year, course_id) 
            VALUES (%s, %s, %s)
        """
        self.execute_insert(query, (stud_id, year, course_id))
        return True
    
    def find_by_id(self, stud_id):
        """Get student by ID."""
        return super().find_by_id('student', 'stud_id', stud_id)
    
    def find_all(self):
        """Get all students."""
        return super().find_all('student')
    
    def find_by_course(self, course_id):
        """Get all students in a course."""
        query = "SELECT * FROM student WHERE course_id = %s"
        return self.execute_query(query, (course_id,))

    def find_by_course_with_details(self, course_id):
        """Get all students in a course with their user details (name, email)."""
        query = """
            SELECT s.stud_id, u.user_name, u.email, s.year, s.course_id 
            FROM student s
            JOIN users u ON s.stud_id = u.user_id
            WHERE s.course_id = %s
        """
        return self.execute_query(query, (course_id,))
    
    def find_all_with_details(self):
        """Get all students with their user details."""
        query = """
            SELECT s.stud_id, u.user_name, u.email, s.year, s.course_id 
            FROM student s
            JOIN users u ON s.stud_id = u.user_id
        """
        return self.execute_query(query)
    
    def update(self, stud_id, column, new_value):
        """Update a student field."""
        allowed_columns = ['year', 'course_id']
        if column not in allowed_columns:
            raise ValueError(f"Column '{column}' cannot be updated")
        
        query = f"UPDATE student SET `{column}` = %s WHERE stud_id = %s"
        return self.execute_update(query, (new_value, stud_id))
    
    def delete(self, stud_id):
        """Delete a student."""
        query = "DELETE FROM student WHERE stud_id = %s"
        return self.execute_delete(query, (stud_id,))
