from build_connection import BuildConnection
from datetime import datetime
import bcrypt
db = BuildConnection()

class Student:

    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()

    def register_student(self, stud_id, stud_name, year, course_id, hash_pass, email=None):
        try:
            query = "SELECT stud_id FROM student WHERE stud_id = %s;"
            self.cursor.execute(query, (stud_id,))
            existing = self.cursor.fetchone()

            if existing is None:
                query = "INSERT INTO student (stud_id, stud_name, year, email, course_id, hash_pass) VALUES (%s, %s, %s, %s, %s, %s);"
                self.cursor.execute(query, (stud_id, stud_name, year, email, course_id, hash_pass))
                self.conn.commit()
                print("Student registered successfully!")
            else:
                print("Student already registered!")
        except Exception as e:
            print("ERROR: ", e)

    def get_student_by_id(self, stud_id):
        try:
            query = "SELECT * FROM student WHERE stud_id = %s;"
            self.cursor.execute(query, (stud_id,))
            students = self.cursor.fetchall()
            for student in students:
                print(student)
        except Exception as e:
            print("ERROR: ", e)

    def get_student_by_name(self, stud_name):
        try:
            query = "SELECT * FROM student WHERE stud_name = %s;"
            self.cursor.execute(query, (stud_name,))
            students = self.cursor.fetchall()
            for student in students:
                print(student)
        except Exception as e:
            print("ERROR: ", e)

    def get_all_students(self):
        try:
            query = "SELECT * FROM student;"
            self.cursor.execute(query)
            students = self.cursor.fetchall()
            for student in students:
                print(student)
        except Exception as e:
            print("ERROR: ", e)

    def update_student(self, stud_id, update_col, new_var):
        try:
            allowed_cols = ["stud_id", "stud_name", "year", "email", "course_id"]
            if update_col not in allowed_cols:
                raise ValueError("Column not found !!")

            query = f"UPDATE student SET `{update_col}` = %s WHERE `stud_id` = %s;"
            self.cursor.execute(query, (new_var, stud_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Student info updated successfully!")
            else:
                print("Student not found!")
        except Exception as e:
            print("ERROR: ", e)

    def del_student(self,stud_id):
        try:
            query = "DELETE FROM student WHERE `stud_id` = %s;"
            self.cursor.execute(query, (stud_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Student info deleted successfully!")
            else:
                print("Student not found!")
        except Exception as e:
            print("ERROR: ", e)

    def del_student_info(self, stud_id, col_name):
        try:
            allowed_cols = ["stud_id", "stud_name", "year", "email", "course_id"]
            if col_name not in allowed_cols:
                raise ValueError("Column not found or restricted!!")

            query = f"UPDATE student SET `{col_name}` = NULL WHERE `stud_id` = %s;"
            self.cursor.execute(query, (stud_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Student info cleared successfully!")
            else:
                print("Student not found!")
        except Exception as e:
            print("ERROR: ", e)

    # --- NEW FEATURES ---
    def get_my_deadlines(self, stud_id):
        """Fetches deadlines for all modules in the student's course."""
        try:
            query = """
                SELECT d.ass_name, d.due_date, m.mod_name 
                FROM deadlines d
                JOIN module m ON d.mod_id = m.mod_id
                JOIN student s ON m.course_id = s.course_id
                WHERE s.stud_id = %s
                ORDER BY d.due_date
            """
            self.cursor.execute(query, (stud_id,))
            rows = self.cursor.fetchall()
            return rows # Returns list of tuples
        except Exception as e:
            print("ERROR: ", e)
            return []

    def check_survey_today(self, stud_id):
        """Checks if the student has submitted a survey today."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            query = "SELECT 1 FROM surveys WHERE stud_id = %s AND date = %s LIMIT 1"
            self.cursor.execute(query, (stud_id, today))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print("ERROR: ", e)
            return False

    def submit_daily_survey(self, stud_id, mod_id, stress, sleep, comments="NO COMMENTS"):
        """Submits a daily wellbeing survey."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            # Note: week_no is required by schema, calculating based on date or passing 0/NULL if allowed
            # Assuming week_no is mandatory, we might need logic to calculate it. For now, using 1 as placeholder or user input.
            # Ideally, week_no should be derived. Let's assume the user passes it or we default to 1.
            week_no = 1 
            
            query = """
                INSERT INTO surveys (week_no, stud_id, mod_id, stress_levels, hours_slept, comments, date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (week_no, stud_id, mod_id, stress, sleep, comments, today))
            self.conn.commit()
            print("Survey submitted successfully!")
        except Exception as e:
            print("ERROR: ", e)

class Analytics:
    """New Class for Director/Officer Features"""
    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()

    def get_course_statistics(self, mod_id):
        """Aggregates grades and attendance for a module."""
        try:
            query = """
                SELECT s.stud_name, g.score, AVG(a.att_per) as avg_attendance
                FROM student s
                LEFT JOIN grades g ON s.stud_id = g.stud_id AND g.mod_id = %s
                LEFT JOIN attendance a ON s.stud_id = a.stud_id AND a.mod_id = %s
                WHERE s.course_id = (SELECT course_id FROM module WHERE mod_id = %s)
                GROUP BY s.stud_id
            """
            self.cursor.execute(query, (mod_id, mod_id, mod_id))
            return self.cursor.fetchall()
        except Exception as e:
            print("ERROR: ", e)
            return []

    def get_wellbeing_by_module(self, mod_id):
        """Gets average stress and sleep for a module."""
        try:
            query = """
                SELECT AVG(stress_levels) as avg_stress, AVG(hours_slept) as avg_sleep
                FROM surveys
                WHERE mod_id = %s
            """
            self.cursor.execute(query, (mod_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print("ERROR: ", e)
            return (0, 0)

    def get_at_risk_students(self, threshold_stress=4, threshold_attendance=50):
        """Identifies students with high stress or low attendance."""
        try:
            query = """
                SELECT s.stud_name, AVG(su.stress_levels) as avg_stress, AVG(a.att_per) as avg_att
                FROM student s
                LEFT JOIN surveys su ON s.stud_id = su.stud_id
                LEFT JOIN attendance a ON s.stud_id = a.stud_id
                GROUP BY s.stud_id
                HAVING avg_stress >= %s OR avg_att <= %s
            """
            self.cursor.execute(query, (threshold_stress, threshold_attendance))
            return self.cursor.fetchall()
        except Exception as e:
            print("ERROR: ", e)
            return []

# --- EXISTING CLASSES (Kept for compatibility) ---

class Users:
    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()

    def register_user(self, user_id, user_name, role, password, email=None):
        try:
            query = "SELECT user_id FROM users WHERE user_id = %s;"
            self.cursor.execute(query, (user_id,))
            existing = self.cursor.fetchone()

            if existing is None:
                hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                query = "INSERT INTO users (user_id, user_name, role, email, hash_pass) VALUES (%s, %s, %s, %s, %s);"
                self.cursor.execute(query, (user_id, user_name, role, email, hash_pass))
                self.conn.commit()
                print("User registered successfully!")
            else:
                print("User already registered!")
        except Exception as e:
            print("ERROR: ", e)

    def get_user_by_id(self, user_id):
        try:
            query = "SELECT * FROM users WHERE user_id = %s;"
            self.cursor.execute(query, (user_id,))
            users = self.cursor.fetchall()
            for user in users:
                print(user)
        except Exception as e:
            print("ERROR: ", e)

    def get_user_by_name(self, user_name):
        try:
            query = "SELECT * FROM users WHERE user_name = %s;"
            self.cursor.execute(query, (user_name,))
            users = self.cursor.fetchall()
            for user in users:
                print(user)
        except Exception as e:
            print("ERROR: ", e)

    def get_all_users(self):
        try:
            query = "SELECT * FROM users;"
            self.cursor.execute(query)
            users = self.cursor.fetchall()
            for user in users:
                print(user)
        except Exception as e:
            print("ERROR: ", e)

    def get_user_by_role(self, role):
        try:
            if role not in ['module_staff', 'welfare_staff','admin']:
                raise ValueError("Role must be either 'module_staff' or 'welfare_staff' or 'admin'")
            query = "SELECT * FROM users WHERE role = %s;"
            self.cursor.execute(query, (role,))
            users = self.cursor.fetchall()
            for user in users:
                print(user)
        except Exception as e:
            print("ERROR: ", e)

    def del_user(self,user_id):
        try:
            query = "DELETE FROM users WHERE `user_id` = %s;"
            self.cursor.execute(query, (user_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("User info deleted successfully!")
            else:
                print("User not found!")
        except Exception as e:
            print("ERROR: ", e)

    def update_user(self, user_id, update_col, new_var):
        try:
            allowed_cols = ["user_id", "user_name", "role", "email"]
            if update_col not in allowed_cols:
                raise ValueError(f"Column {update_col} not found or restricted!!")

            query = f"UPDATE users SET `{update_col}` = %s WHERE `user_id` = %s;"
            self.cursor.execute(query, (new_var, user_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("User info updated successfully!")
            else:
                print("User not found!")
        except Exception as e:
            print("ERROR: ", e)
        
    def del_user_info(self, user_id, col_name):
        
        if col_name not in ["user_name", "role", "email"]:
            raise ValueError(f"Invalid or restricted column name provided: '{col_name}'. Only allowed columns can be cleared.")        
        try:
            query = f"UPDATE users SET `{col_name}` = NULL WHERE `user_id` = %s;"
            self.cursor.execute(query, (user_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("User info cleared successfully!")
            else:
                print("User not found!")
        except Exception as e:
            print("ERROR: ", e)

class Course:

    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()

    def register_course(self, course_id, course_name):
        try:
            query = "SELECT course_id FROM course WHERE course_id = %s;"
            self.cursor.execute(query, (course_id,))
            existing = self.cursor.fetchone()

            if existing is None:
                query = "INSERT INTO course (course_id, course_name) VALUES (%s, %s);"
                self.cursor.execute(query, (course_id, course_name))
                self.conn.commit()
                print("Course registered successfully!")
            else:
                print("Course already registered!")
        except Exception as e:
            print("ERROR: ", e)

    def get_course_by_id(self, course_id):
        try:
            query = "SELECT * FROM course WHERE course_id = %s;"
            self.cursor.execute(query, (course_id,))
            courses = self.cursor.fetchall()
            for course in courses:
                print(course)
        except Exception as e:
            print("ERROR: ", e)
    
    def get_course_by_name(self, course_name):
        try:
            query = "SELECT * FROM course WHERE course_name = %s;"
            self.cursor.execute(query, (course_name,))
            courses = self.cursor.fetchall()
            for course in courses:
                print(course)
        except Exception as e:
            print("ERROR: ", e)

    def get_all_courses(self):
        try:
            query = "SELECT * FROM course;"
            self.cursor.execute(query)
            courses = self.cursor.fetchall()
            for course in courses:
                print(course)
        except Exception as e:
            print("ERROR: ", e)

    def del_course_by_course_id(self,course_id):
        try:
            query = "DELETE FROM course WHERE `course_id` = %s;"
            self.cursor.execute(query, (course_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Course info deleted successfully!")
            else:
                print("Course not found!")
        except Exception as e:
            print("ERROR: ", e)

    def del_course_by_course_name(self,course_name):
        try:
            query = "DELETE FROM course WHERE `course_name` = %s;"
            self.cursor.execute(query, (course_name,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Course info deleted successfully!")
            else:
                print("Course not found!")
        except Exception as e:
            print("ERROR: ", e)
        
    def update_course_name(self, course_id, new_var):
        try:
            query = "UPDATE course SET `course_name` = %s WHERE `course_id` = %s;"
            self.cursor.execute(query, (new_var, course_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Course info updated successfully!")
            else:
                print("Course not found!")
        except Exception as e:
            print("ERROR: ", e)

    def update_course_id(self, course_id, new_id):
        try:
            self.cursor.execute("SELECT course_id FROM course WHERE course_id = %s;", (new_id,))
            if self.cursor.fetchone():
                print("New course_id already exists! Choose a different one.")
                return

            query = "UPDATE course SET `course_id` = %s WHERE `course_id` = %s;"
            self.cursor.execute(query, (new_id, course_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Course info updated successfully!")
            else:
                print("Course not found!")
        except Exception as e:
            print("ERROR: ", e)

class Module:

    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()
    
    def register_module(self, mod_id, mod_name, course_id, year, welfare_staff_id, module_staff_id):
        try:
            query = "SELECT mod_id FROM module WHERE mod_id = %s;"
            self.cursor.execute(query, (mod_id,))
            existing = self.cursor.fetchone()

            if existing is None:
                query = "INSERT INTO module (mod_id, mod_name, course_id, year, welfare_staff_id, module_staff_id) VALUES (%s, %s, %s, %s, %s, %s);"
                self.cursor.execute(query, (mod_id, mod_name, course_id, year, welfare_staff_id, module_staff_id))
                self.conn.commit()
                print("Module registered successfully!")
            else:
                print("Module already registered!")
        except Exception as e:
            print("ERROR: ", e) 

    def get_module_by_id(self, mod_id):
        try:
            query = "SELECT * FROM module WHERE mod_id = %s;"
            self.cursor.execute(query, (mod_id,))
            modules = self.cursor.fetchall()
            if modules is None:
                print("Module id not found!")
                return
            for module in modules:
                print(module)
        except Exception as e:
            print("ERROR: ", e)
        
    def get_module_by_name(self, mod_name):
        try:
            query = "SELECT * FROM module WHERE mod_name = %s;"
            self.cursor.execute(query, (mod_name,))
            modules = self.cursor.fetchall()
            if modules is None:
                print("Module name not found!")
                return
            for module in modules:
                print(module)
        except Exception as e:
            print("ERROR: ", e)

    def get_module_by_course_id(self, course_id):
        try:
            query = "SELECT * FROM module WHERE course_id = %s;"
            self.cursor.execute(query, (course_id,))
            modules = self.cursor.fetchall()
            if modules is None:
                print("Module id not found!")
                return
            for module in modules:
                print(module)
        except Exception as e:
            print("ERROR: ", e) 
    
    def get_module_by_year(self, year):
        try:
            query = "SELECT * FROM module WHERE year = %s;"
            self.cursor.execute(query, (year,))
            modules = self.cursor.fetchall()
            if modules is None:
                print("Module year not found!")
                return
            for module in modules:
                print(module)
        except Exception as e:
            print("ERROR: ", e)     

    def get_all_modules(self):
        try:
            query = "SELECT * FROM module;"
            self.cursor.execute(query)
            modules = self.cursor.fetchall()
            for module in modules:
                print(module)
        except Exception as e:
            print("ERROR: ", e)
    
    def del_module_by_id(self,mod_id):
        try:
            query = "DELETE FROM module WHERE `mod_id` = %s;"
            self.cursor.execute(query, (mod_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Module info deleted successfully!")
            else:
                print("Module not found!")
        except Exception as e:
            print("ERROR: ", e)

    def del_module_by_name(self,mod_name):
        try:
            query = "DELETE FROM module WHERE `mod_name` = %s;"
            self.cursor.execute(query, (mod_name,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Module info deleted successfully!")
            else:
                print("Module not found!")
        except Exception as e:
            print("ERROR: ", e)
    
    def del_module_info(self, mod_id, col_name):

        if col_name not in ["mod_name", "course_id", "year", "welfare_staff_id", "module_staff_id"]:
            raise ValueError("Invalid column name!")
        try:
            query = "SELECT * FROM module WHERE mod_id = %s;"
            self.cursor.execute(query, (mod_id,))
            existing = self.cursor.fetchone()

            if existing:
                query = f"UPDATE module SET `{col_name}` = NULL WHERE `mod_id` = %s;"
                self.cursor.execute(query, (mod_id,))
                self.conn.commit()
                print("Module info cleared successfully!")
                print("Module not found!")
        except Exception as e:
            print("ERROR: ", e)

    def update_module(self, mod_id, update_col, new_var):  
        allowed_cols = ["mod_id", "mod_name", "course_id", "year", "welfare_staff_id", "module_staff_id"]
        if update_col not in allowed_cols:
            raise ValueError(f"Invalid column name! Allowed: {allowed_cols}")

        try:
            if update_col == "mod_id":
                self.cursor.execute("SELECT mod_id FROM module WHERE mod_id = %s;", (new_var,))
                if self.cursor.fetchone():
                    raise ValueError(f"Module ID '{new_var}' already exists!")

            query = f"UPDATE module SET `{update_col}` = %s WHERE mod_id = %s;"
            self.cursor.execute(query, (new_var, mod_id))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print("Module info updated successfully!")
            else:
                print("Module not found!")

        except Exception as e:
            print("ERROR: ", e)
    
class Deadlines:

    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()

    def set_deadlines(self, dead_id, mod_id, week_no, due_date, ass_name="Assessment"):
        try:
            query = "SELECT 1 FROM deadlines WHERE dead_id = %s;"
            self.cursor.execute(query, (dead_id,))
            existing = self.cursor.fetchone()

            if existing is None:
                query = "INSERT INTO deadlines (dead_id, mod_id, week_no, ass_name, due_date) VALUES (%s, %s, %s, %s, %s);"
                self.cursor.execute(query, (dead_id, mod_id, week_no, ass_name, due_date))
                self.conn.commit()
                print("Deadline set successfully!")
            else:
                print("Deadline already set!")
        except Exception as e:
            print("ERROR: ", e)
    
    def get_deadlines(self):
        try:
            query = "SELECT * FROM deadlines;"
            self.cursor.execute(query)
            deadlines = self.cursor.fetchall()
            for deadline in deadlines:
                print(deadline)
        except Exception as e:
            print("ERROR: ", e)

    def get_deadline_by_dead_id(self,dead_id):
        try:
            query = "SELECT * FROM deadlines WHERE dead_id = %s;"
            self.cursor.execute(query,(dead_id,))
            deadline = self.cursor.fetchone()
            if deadline:
                print("Deadline Found!: ", deadline)     
            else:
                print(f"Deadline Not Found for the id: {dead_id}!!")       
        except Exception as e:
            print("ERROR:",e)
    
    def get_deadline_by_mod_id(self,mod_id):
        try:
            query = "SELECT * FROM deadlines WHERE mod_id = %s;"
            self.cursor.execute(query,(mod_id,))
            deadlines = self.cursor.fetchall()
            if deadlines:
                for deadline in deadlines:
                    print("Deadline Found!: ", deadline)     
            else:
                print(f"Deadline Not Found for the module id: {mod_id}!!")    
        except Exception as e:
            print("ERROR:",e)
    
    def get_deadline_by_week_no(self,week_no):
        try:
            query = "SELECT * FROM deadlines WHERE week_no = %s;"
            self.cursor.execute(query,(week_no,))
            deadlines = self.cursor.fetchall()
            if deadlines:
                for deadline in deadlines:
                    print("Deadline Found!: ", deadline)     
            else:
                print(f"Deadline Not Found for the week no: {week_no}!!")    
        except Exception as e:
            print("ERROR:",e)

    def get_deadline_by_ass_name(self,ass_name):
        try:
            query = "SELECT * FROM deadlines WHERE ass_name = %s;"
            self.cursor.execute(query,(ass_name,))
            deadlines = self.cursor.fetchall()
            if deadlines:
                for deadline in deadlines:
                    print("Deadline Found!: ", deadline)     
            else:
                print(f"Deadline Not Found for the assessment name: {ass_name}!!")    
        except Exception as e:
            print("ERROR:",e)

    def get_deadline_by_due_date(self, due_date):
        try:
            query = "SELECT * FROM deadlines WHERE due_date = %s;"
            self.cursor.execute(query,(due_date,))
            deadlines = self.cursor.fetchall()
            if deadlines:
                for deadline in deadlines:
                    print("Deadline Found!: ", deadline)     
            else:
                print(f"Deadline Not Found for the assessment name: {due_date}!!")    
        except Exception as e:
            print("ERROR:",e)

    def del_deadline_by_dead_id(self, dead_id):
        try:
            query = "DELETE FROM deadlines WHERE `dead_id` = %s;"
            self.cursor.execute(query, (dead_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline deleted successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)
        
    def del_deadline_by_ass_name(self, ass_name):
        try:
            query = "DELETE FROM deadlines WHERE `ass_name` = %s;"
            self.cursor.execute(query, (ass_name,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline deleted successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)

    def del_deadline_by_due_date(self, due_date):
        try:
            query = "DELETE FROM deadlines WHERE `due_date` = %s;"
            self.cursor.execute(query, (due_date,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline deleted successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)
    
    def del_deadline_by_mod_id(self, mod_id):
        try:
            query = "DELETE FROM deadlines WHERE `mod_id` = %s;"
            self.cursor.execute(query, (mod_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline deleted successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)
    
    def del_deadline_info(self, dead_id, col_name):
        try:
            allowed_cols = ["mod_id", "week_no", "ass_name", "due_date"]
            if col_name not in allowed_cols:
                raise ValueError("Column not found !!")


            query = f"UPDATE deadlines SET `{col_name}` = NULL WHERE `dead_id` = %s;"
            self.cursor.execute(query, (dead_id,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline info cleared successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)

    def update_deadline_by_dead_id(self, dead_id, update_col, new_var):   
        try:
            allowed_cols = ["dead_id", "mod_id", "week_no", "ass_name", "due_date"]
            if update_col not in allowed_cols:
                raise ValueError("Column not found !!")

            if update_col == "dead_id":
                query = "SELECT dead_id FROM deadlines WHERE dead_id = %s;"
                self.cursor.execute(query, (new_var,))
                existing = self.cursor.fetchone()
                if existing:
                    raise ValueError("Deadline ID already exists and duplicates are not allowed!!")
                else:
                    query = "UPDATE deadlines SET `dead_id` = %s WHERE `dead_id` = %s;"
                    self.cursor.execute(query, (new_var, dead_id))
                    self.conn.commit()

            else:        
                query = f"UPDATE deadlines SET `{update_col}` = %s WHERE `dead_id` = %s;"
                self.cursor.execute(query, (new_var, dead_id))
                self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline info updated successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)
    
    def update_deadline_by_mod_id(self, mod_id, update_col, new_var):   
        try:
            allowed_cols = ["dead_id", "mod_id", "week_no", "ass_name", "due_date"]
            if update_col not in allowed_cols:
                print("Column not found !!")
                return

            query = f"UPDATE deadlines SET `{update_col}` = %s WHERE `mod_id` = %s;"
            self.cursor.execute(query, (new_var, mod_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Deadline info updated successfully!")
            else:
                print("Deadline not found!")
        except Exception as e:
            print("ERROR: ", e)

class attendance:

    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()

    def set_attendance(self,stud_id, mod_id, week_no, att_per, date=None):
        try:
            query = "SELECT 1 FROM attendance WHERE stud_id = %s AND mod_id = %s AND week_no = %s;"
            self.cursor.execute(query, (stud_id, mod_id, week_no))
            existing = self.cursor.fetchone()

            if existing is None:
                if date is None:
                    date = datetime.now().strftime("%Y-%m-%d")
                query = "INSERT INTO attendance (week_no, mod_id, stud_id, att_per, date) VALUES (%s, %s, %s, %s, %s);"
                self.cursor.execute(query, (week_no, mod_id, stud_id, att_per, date))
                self.conn.commit()
                print("Attendance set successfully!")
            else:
                print("Attendance already set!")
        except Exception as e:
            print("ERROR: ", e)
        
    def get_attendance_by_mod_id(self, mod_id):
        try:
            query = "SELECT * FROM attendance WHERE mod_id = %s;"
            self.cursor.execute(query, (mod_id,))
            attendance = self.cursor.fetchall()
            if attendance:
                for att in attendance:
                    print("Attendance Found!: ", att)
            else:
                print("Attendance Not Found for the module id: ", mod_id)
        except Exception as e:
            print("ERROR: ", e)

    def get_attendance_by_stud_id(self, stud_id):
        try:
            query = "SELECT * FROM attendance WHERE stud_id = %s;"
            self.cursor.execute(query, (stud_id,))
            attendance = self.cursor.fetchall()
            if attendance:
                for att in attendance:
                    print("Attendance Found!: ", att)
            else:
                print("Attendance Not Found for the student id: ", stud_id)
        except Exception as e:
            print("ERROR: ", e)

    def get_attendance_by_week_no(self, week_no):
        try:
            query = "SELECT * FROM attendance WHERE week_no = %s;"
            self.cursor.execute(query, (week_no,))
            attendance = self.cursor.fetchall()
            if attendance:
                for att in attendance:
                    print("Attendance Found!: ", att)
            else:
                print("Attendance Not Found for the week number: ", week_no)
        except Exception as e:
            print("ERROR: ", e)

    def update_att_by_stud_id(self, stud_id, update_col, new_var):
        try:
            allowed_cols = ["stud_id", "mod_id", "week_no"]
            if update_col not in allowed_cols:
                raise ValueError(f"Column {update_col} not found !!")
    
            query = f"UPDATE attendance SET `{update_col}` = %s WHERE `stud_id` = %s;"
            self.cursor.execute(query, (new_var, stud_id))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("Attendance info updated successfully!")
            else:
                print("Attendance not found!")
        except Exception as e:
            print("ERROR: ", e)
    
class Surveys:

    def __init__(self, conn=None, cursor=None):
        if conn and cursor:
            self.conn = conn
            self.cursor = cursor
        else:
            self.conn, self.cursor = db.make_connection()
    
    def set_survey(self, week_no, stud_id, mod_id, stress_levels, hours_slept, comments="NO COMMENTS", date=None):
        try:
            query = "SELECT 1 FROM surveys WHERE week_no = %s AND stud_id = %s AND mod_id = %s;"
            self.cursor.execute(query, (week_no, stud_id, mod_id))
            existing = self.cursor.fetchone()

            if existing is None:
                if date is None:
                    date = datetime.now().strftime("%Y-%m-%d")
                query = "INSERT INTO surveys (week_no, stud_id, mod_id, stress_levels, hours_slept, comments, date) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                self.cursor.execute(query, (week_no, stud_id, mod_id, stress_levels, hours_slept, comments, date))
                self.conn.commit()
                print("Survey submitted successfully!")
            else:
                print("Survey already submitted for this week/module!")
        except Exception as e:
            print("ERROR: ", e)
