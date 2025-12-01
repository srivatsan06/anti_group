from .base_model import BaseModel
class ModuleModel(BaseModel):
    TABLE_NAME = 'module'
    def create(self, mod_id, mod_name, course_id, welfare_staff_id, module_staff_id):
        query = """
            INSERT INTO module (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_insert(query, (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id))
        return True
    def find_by_id(self, mod_id):
        return super().find_by_id('module', 'mod_id', mod_id)
    def find_by_course(self, course_id):
        query = "SELECT * FROM module WHERE course_id = %s"
        return self.execute_query(query, (course_id,))
    def find_by_staff(self, staff_id):
        query = """
            SELECT * FROM module 
            WHERE welfare_staff_id = %s OR module_staff_id = %s
        """
        return self.execute_query(query, (staff_id, staff_id))
    def find_all(self):
        return super().find_all('module')
    def update(self, mod_id, column, new_value):
        allowed_columns = ['mod_name', 'course_id', 'welfare_staff_id', 'module_staff_id']
        if column not in allowed_columns:
            raise ValueError(f"Column '{column}' cannot be updated")
        query = f"UPDATE module SET `{column}` = %s WHERE mod_id = %s"
        return self.execute_update(query, (new_value, mod_id))
    def delete(self, mod_id):
        query = "DELETE FROM module WHERE mod_id = %s"
        return self.execute_delete(query, (mod_id,))
