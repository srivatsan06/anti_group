from .base_model import BaseModel


class CourseModel(BaseModel):
    TABLE_NAME = 'course'
    
    def create(self, course_id, course_name):
        query = "INSERT INTO course (course_id, course_name) VALUES (%s, %s)"
        self.execute_insert(query, (course_id, course_name))
        return True
    
    def find_by_id(self, course_id):
        return super().find_by_id('course', 'course_id', course_id)
    
    def find_by_name(self, course_name):
        query = "SELECT * FROM course WHERE course_name = %s"
        results = self.execute_query(query, (course_name,))
        return results[0] if results else None
    
    def find_all(self):
        return super().find_all('course')
    
    def update(self, course_id, new_name):
        query = "UPDATE course SET course_name = %s WHERE course_id = %s"
        return self.execute_update(query, (new_name, course_id))
    
    def delete(self, course_id):
        query = "DELETE FROM course WHERE course_id = %s"
        return self.execute_delete(query, (course_id,))
