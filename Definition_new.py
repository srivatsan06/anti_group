from build_connection import BuildConnection
db = BuildConnection()

class TableDefinition:
    def __init__(self):
        self.conn, self.cursor = db.make_connection()

    def create_triggers(self):
        try:
            # --- Module Role Checks ---
            self.cursor.execute("DROP PROCEDURE IF EXISTS check_module_roles;")
            proc_module_sql = """
            CREATE PROCEDURE check_module_roles(IN welfare_staff_id VARCHAR(8), IN module_staff_id VARCHAR(8))
            BEGIN
                DECLARE welfare_staff_role_check VARCHAR(20);
                DECLARE module_staff_role_check VARCHAR(20);

                SELECT role INTO welfare_staff_role_check FROM users WHERE user_id = welfare_staff_id;
                IF welfare_staff_role_check IS NULL OR welfare_staff_role_check != 'welfare_staff' THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid welfare_staff_id: user is not welfare staff';
                END IF;

                SELECT role INTO module_staff_role_check FROM users WHERE user_id = module_staff_id;
                IF module_staff_role_check IS NULL OR module_staff_role_check != 'module_staff' THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid module_staff_id: user is not module staff';
                END IF;
            END;
            """
            self.cursor.execute(proc_module_sql)

            self.cursor.execute("DROP TRIGGER IF EXISTS module_insert_trigger;")
            trig_module_insert = """
            CREATE TRIGGER module_insert_trigger
            BEFORE INSERT ON module
            FOR EACH ROW
            BEGIN
                CALL check_module_roles(NEW.welfare_staff_id, NEW.module_staff_id);
            END;
            """
            self.cursor.execute(trig_module_insert)

            self.cursor.execute("DROP TRIGGER IF EXISTS module_update_trigger;")
            trig_module_update = """
            CREATE TRIGGER module_update_trigger
            BEFORE UPDATE ON module
            FOR EACH ROW
            BEGIN
                CALL check_module_roles(NEW.welfare_staff_id, NEW.module_staff_id);
            END;
            """
            self.cursor.execute(trig_module_update)

            # --- Student Role Checks ---
            self.cursor.execute("DROP PROCEDURE IF EXISTS check_student_role;")
            proc_student_sql = """
            CREATE PROCEDURE check_student_role(IN stud_id VARCHAR(8))
            BEGIN
                DECLARE student_role_check VARCHAR(20);

                SELECT role INTO student_role_check FROM users WHERE user_id = stud_id;
                IF student_role_check IS NULL OR student_role_check != 'student' THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid stud_id: user is not a student';
                END IF;
            END;
            """
            self.cursor.execute(proc_student_sql)

            self.cursor.execute("DROP TRIGGER IF EXISTS student_insert_trigger;")
            trig_student_insert = """
            CREATE TRIGGER student_insert_trigger
            BEFORE INSERT ON student
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_student_insert)

            self.cursor.execute("DROP TRIGGER IF EXISTS student_update_trigger;")
            trig_student_update = """
            CREATE TRIGGER student_update_trigger
            BEFORE UPDATE ON student
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_student_update)

            # --- Attendance Role Checks ---
            self.cursor.execute("DROP TRIGGER IF EXISTS attendance_insert_trigger;")
            trig_att_insert = """
            CREATE TRIGGER attendance_insert_trigger
            BEFORE INSERT ON attendance
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_att_insert)

            self.cursor.execute("DROP TRIGGER IF EXISTS attendance_update_trigger;")
            trig_att_update = """
            CREATE TRIGGER attendance_update_trigger
            BEFORE UPDATE ON attendance
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_att_update)

            # --- Surveys Role Checks ---
            self.cursor.execute("DROP TRIGGER IF EXISTS surveys_insert_trigger;")
            trig_surv_insert = """
            CREATE TRIGGER surveys_insert_trigger
            BEFORE INSERT ON surveys
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_surv_insert)

            self.cursor.execute("DROP TRIGGER IF EXISTS surveys_update_trigger;")
            trig_surv_update = """
            CREATE TRIGGER surveys_update_trigger
            BEFORE UPDATE ON surveys
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_surv_update)

            # --- Module Grades Role Checks ---
            self.cursor.execute("DROP TRIGGER IF EXISTS grades_insert_trigger;")
            trig_grades_insert = """
            CREATE TRIGGER grades_insert_trigger
            BEFORE INSERT ON module_grades
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_grades_insert)

            self.cursor.execute("DROP TRIGGER IF EXISTS grades_update_trigger;")
            trig_grades_update = """
            CREATE TRIGGER grades_update_trigger
            BEFORE UPDATE ON module_grades
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_grades_update)

            # --- Deadlines Role Checks ---
            self.cursor.execute("DROP TRIGGER IF EXISTS deadlines_insert_trigger;")
            trig_dead_insert = """
            CREATE TRIGGER deadlines_insert_trigger
            BEFORE INSERT ON deadlines
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_dead_insert)

            self.cursor.execute("DROP TRIGGER IF EXISTS deadlines_update_trigger;")
            trig_dead_update = """
            CREATE TRIGGER deadlines_update_trigger
            BEFORE UPDATE ON deadlines
            FOR EACH ROW
            BEGIN
                CALL check_student_role(NEW.stud_id);
            END;
            """
            self.cursor.execute(trig_dead_update)

            self.conn.commit()
            print("Procedure and triggers created successfully!")
            
        except Exception as e:
            print(f"Error creating triggers: {e}")

    def table_definition(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS course(
                `course_id` varchar(6) PRIMARY KEY, 
                `course_name` varchar(100) NOT NULL
                );
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                `user_id` varchar(8) PRIMARY KEY, 
                `user_name` varchar(30) NOT NULL, 
                `role` ENUM ('module_staff','welfare_staff','admin','student') NOT NULL, 
                `email` varchar(40) , 
                `hash_pass` varchar(255) NOT NULL
                );
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                `stud_id` varchar(8) PRIMARY KEY, 
                `year` INT NOT NULL, 
                `course_id` varchar(6) ,
                FOREIGN KEY (course_id) REFERENCES course(course_id) ON UPDATE CASCADE,
                FOREIGN KEY (stud_id) REFERENCES users(user_id) ON UPDATE CASCADE
                );
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS module (
                `mod_id` varchar(8) PRIMARY KEY, 
                `mod_name` varchar(100) NOT NULL, 
                `course_id` varchar(6) NOT NULL, 
                `welfare_staff_id` varchar(8) NOT NULL, 
                `module_staff_id` varchar(8) NOT NULL, 
                FOREIGN KEY (welfare_staff_id) REFERENCES users(user_id) ON UPDATE CASCADE ,
                FOREIGN KEY (module_staff_id) REFERENCES users(user_id) ON UPDATE CASCADE,
                FOREIGN KEY (course_id) REFERENCES course(course_id) ON UPDATE CASCADE ON DELETE CASCADE
                );
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    `week_no` INT, 
                    `mod_id` varchar(8), 
                    `stud_id` varchar(8), 
                    `date` DATE,
                    `missed` BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (mod_id, stud_id, date), 
                    FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                    FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
                );
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS surveys (
                    `week_no` INT, 
                    `stud_id` varchar(8), 
                    `mod_id` varchar(8), 
                    `stress_levels` INT CHECK(`stress_levels` > 0 AND `stress_levels` <=5), 
                    `hours_slept` DECIMAL(3,1) CHECK(`hours_slept` < 24), 
                    `comments` varchar(200) DEFAULT 'NO COMMENTS', 
                    `date` DATE,
                    PRIMARY KEY (week_no, stud_id, mod_id), 
                    FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                    FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
                );
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS deadlines (
                    `stud_id` varchar(8) NOT NULL, 
                    `mod_id` varchar(8) NOT NULL, 
                    `week_no` INT, 
                    `ass_name` varchar(100) DEFAULT 'Assessment', 
                    `due_date` DATE NOT NULL, 
                    `Submitted` BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (stud_id, mod_id, ass_name, due_date),
                    FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE,
                    FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS module_grades (
                    `stud_id` varchar(8) NOT NULL,
                    `mod_id` varchar(8) NOT NULL,
                    `grade` INT CHECK(`grade` >= 0 AND `grade` <= 100) NOT NULL,
                    PRIMARY KEY (stud_id, mod_id),
                    FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE ON DELETE CASCADE,
                    FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
                );
            """)
            
            self.conn.commit()
            print("Tables created successfully (with new features) !!")
            self.create_triggers()
        except Exception as e:
            print("ERROR: ",e)
