from build_connection import BuildConnection
import mysql.connector

def test_triggers():
    db = BuildConnection()
    conn, cursor = db.make_connection()
    
    print("--- Starting Trigger Test ---")
    
    # Test Data
    admin_id = "TEST_ADM"
    student_id = "TEST_STU"
    course_id = "TST101"
    mod_id = "TST_MOD"
    
    try:
        # 1. Setup: Create Course and Module
        cursor.execute("INSERT IGNORE INTO course (course_id, course_name) VALUES (%s, %s)", (course_id, "Test Course"))
        # Need a module for attendance/grades/surveys
        # We need valid staff for module creation (or disable triggers temporarily, but let's use valid staff)
        welfare_id = "TEST_WEL"
        module_staff_id = "TEST_MOD"
        cursor.execute("INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) VALUES (%s, %s, %s, %s, %s)", 
                       (welfare_id, "Test Welfare", "welfare_staff", "welfare@test.com", "pass"))
        cursor.execute("INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) VALUES (%s, %s, %s, %s, %s)", 
                       (module_staff_id, "Test ModStaff", "module_staff", "modstaff@test.com", "pass"))
        
        cursor.execute("INSERT IGNORE INTO module (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id) VALUES (%s, %s, %s, %s, %s)", 
                       (mod_id, "Test Module", course_id, welfare_id, module_staff_id))
        
        # 2. Setup: Create Users
        # Admin User
        cursor.execute("INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) VALUES (%s, %s, %s, %s, %s)", 
                       (admin_id, "Test Admin", "admin", "admin@test.com", "pass"))
        # Student User
        cursor.execute("INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) VALUES (%s, %s, %s, %s, %s)", 
                       (student_id, "Test Student", "student", "student@test.com", "pass"))
        conn.commit()
        
        # 3. Test Failure Case: Insert Admin into Student Table
        print(f"Attempting to insert Admin ({admin_id}) into Student table...")
        try:
            cursor.execute("INSERT INTO student (stud_id, year, course_id) VALUES (%s, %s, %s)", (admin_id, 1, course_id))
            conn.commit()
            print("FAILURE: Admin was inserted into Student table! Trigger failed.")
        except mysql.connector.Error as err:
            print(f"SUCCESS: Admin insertion failed as expected. Error: {err}")
            
        # 4. Test Success Case: Insert Student into Student Table
        print(f"Attempting to insert Student ({student_id}) into Student table...")
        try:
            cursor.execute("INSERT INTO student (stud_id, year, course_id) VALUES (%s, %s, %s)", (student_id, 1, course_id))
            conn.commit()
            print("SUCCESS: Student inserted successfully.")
        except mysql.connector.Error as err:
            print(f"FAILURE: Student insertion failed! Error: {err}")

        # 5. Test Extended Triggers (Attendance, Surveys, Grades)
        print("\n--- Testing Extended Triggers ---")
        
        # A. Attendance
        print("Testing Attendance Insert (Admin ID)...")
        try:
            cursor.execute("INSERT INTO attendance (week_no, mod_id, stud_id, date) VALUES (1, %s, %s, '2023-01-01')", (mod_id, admin_id))
            print("FAILURE: Admin inserted into Attendance! Trigger failed.")
        except mysql.connector.Error as err:
            print(f"SUCCESS: Admin blocked from Attendance. Error: {err}")

        print("Testing Attendance Insert (Student ID)...")
        try:
            cursor.execute("INSERT INTO attendance (week_no, mod_id, stud_id, date) VALUES (1, %s, %s, '2023-01-01')", (mod_id, student_id))
            print("SUCCESS: Student inserted into Attendance.")
        except mysql.connector.Error as err:
            print(f"FAILURE: Student blocked from Attendance! Error: {err}")

        # B. Surveys
        print("Testing Survey Insert (Admin ID)...")
        try:
            cursor.execute("INSERT INTO surveys (week_no, stud_id, mod_id, stress_levels, hours_slept, date) VALUES (1, %s, %s, 3, 8, '2023-01-01')", (admin_id, mod_id))
            print("FAILURE: Admin inserted into Surveys! Trigger failed.")
        except mysql.connector.Error as err:
            print(f"SUCCESS: Admin blocked from Surveys. Error: {err}")

        # C. Grades
        print("Testing Grades Insert (Admin ID)...")
        try:
            cursor.execute("INSERT INTO module_grades (stud_id, mod_id, grade) VALUES (%s, %s, 85)", (admin_id, mod_id))
            print("FAILURE: Admin inserted into Grades! Trigger failed.")
        except mysql.connector.Error as err:
            print(f"SUCCESS: Admin blocked from Grades. Error: {err}")

        # D. Deadlines
        print("Testing Deadlines Insert (Admin ID)...")
        try:
            # dead_id, stud_id, mod_id, week_no, ass_name, due_date
            cursor.execute("INSERT INTO deadlines (dead_id, stud_id, mod_id, week_no, due_date) VALUES ('D1', %s, %s, 1, '2023-01-01')", (admin_id, mod_id))
            print("FAILURE: Admin inserted into Deadlines! Trigger failed.")
        except mysql.connector.Error as err:
            print(f"SUCCESS: Admin blocked from Deadlines. Error: {err}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Cleanup
        
        print("Cleaning up test data...")
        cursor.execute("DELETE FROM attendance WHERE mod_id = %s", (mod_id,))
        cursor.execute("DELETE FROM surveys WHERE mod_id = %s", (mod_id,))
        cursor.execute("DELETE FROM module_grades WHERE mod_id = %s", (mod_id,))
        cursor.execute("DELETE FROM deadlines WHERE mod_id = %s", (mod_id,))
        cursor.execute("DELETE FROM student WHERE stud_id IN (%s, %s)", (admin_id, student_id))
        cursor.execute("DELETE FROM module WHERE mod_id = %s", (mod_id,))
        cursor.execute("DELETE FROM users WHERE user_id IN (%s, %s, 'TEST_WEL', 'TEST_MOD')", (admin_id, student_id))
        cursor.execute("DELETE FROM course WHERE course_id = %s", (course_id,))
        conn.commit()
        conn.close()
        print("--- Test Complete ---")

if __name__ == "__main__":
    test_triggers()
