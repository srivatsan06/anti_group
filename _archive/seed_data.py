"""
Data Seeding Script - Populates database with test data.
Creates 10 rows in each table for testing RBAC operations.
"""
from build_connection import BuildConnection
import bcrypt
from datetime import datetime, timedelta
import random

db = BuildConnection()
conn, cursor = db.make_connection()

def seed_data():
    """Seed all tables with test data."""
    
    print("=" * 60)
    print("STARTING DATA SEEDING")
    print("=" * 60)
    
    try:
        # === 1. COURSES (3 courses) ===
        print("\n[1/8] Seeding courses...")
        courses = [
            ('CS101', 'Computer Science'),
            ('MATH01', 'Mathematics'),
            ('ENG001', 'Engineering')
        ]
        for course_id, course_name in courses:
            cursor.execute("INSERT IGNORE INTO course (course_id, course_name) VALUES (%s, %s)", 
                          (course_id, course_name))
        conn.commit()
        print(f"   ✓ Created {len(courses)} courses")
        
        # === 2. USERS (14 users: 1 admin, 3 welfare_staff, 3 module_staff, 7 students) ===
        print("\n[2/8] Seeding users...")
        users = [
            # Admin
            ('ADMIN01', 'Admin User', 'admin', 'admin@university.edu', 'admin123'),
            # Welfare Staff
            ('WS001', 'Dr. Sarah Johnson', 'welfare_staff', 'sarah.j@university.edu', 'welfare123'),
            ('WS002', 'Dr. Mark Williams', 'welfare_staff', 'mark.w@university.edu', 'welfare123'),
            ('WS003', 'Dr. Lisa Brown', 'welfare_staff', 'lisa.b@university.edu', 'welfare123'),
            # Module Staff
            ('MS001', 'Prof. John Smith', 'module_staff', 'john.smith@university.edu', 'module123'),
            ('MS002', 'Prof. Emily Davis', 'module_staff', 'emily.d@university.edu', 'module123'),
            ('MS003', 'Prof. Robert Taylor', 'module_staff', 'robert.t@university.edu', 'module123'),
            # Students
            ('STU001', 'Alice Cooper', 'student', 'alice.c@student.edu', 'student123'),
            ('STU002', 'Bob Martinez', 'student', 'bob.m@student.edu', 'student123'),
            ('STU003', 'Charlie Lee', 'student', 'charlie.l@student.edu', 'student123'),
            ('STU004', 'Diana Wang', 'student', 'diana.w@student.edu', 'student123'),
            ('STU005', 'Eva Garcia', 'student', 'eva.g@student.edu', 'student123'),
            ('STU006', 'Frank Miller', 'student', 'frank.m@student.edu', 'student123'),
            ('STU007', 'Grace Chen', 'student', 'grace.c@student.edu', 'student123'),
        ]
        
        for user_id, user_name, role, email, password in users:
            hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, user_name, role, email, hash_pass))
        conn.commit()
        print(f"   ✓ Created {len(users)} users")
        
        # === 3. STUDENTS (7 students) ===
        print("\n[3/8] Seeding students...")
        students = [
            ('STU001', 1, 'CS101'),
            ('STU002', 1, 'CS101'),
            ('STU003', 2, 'CS101'),
            ('STU004', 2, 'MATH01'),
            ('STU005', 3, 'MATH01'),
            ('STU006', 3, 'ENG001'),
            ('STU007', 1, 'ENG001'),
        ]
        for stud_id, year, course_id in students:
            cursor.execute("INSERT IGNORE INTO student (stud_id, year, course_id) VALUES (%s, %s, %s)", 
                          (stud_id, year, course_id))
        conn.commit()
        print(f"   ✓ Created {len(students)} student records")
        
        # === 4. MODULES (9 modules) ===
        print("\n[4/8] Seeding modules...")
        modules = [
            ('CS11001', 'Database Systems', 'CS101', 'WS001', 'MS001'),
            ('CS11002', 'Algorithms', 'CS101', 'WS001', 'MS002'),
            ('CS11003', 'Web Development', 'CS101', 'WS002', 'MS003'),
            ('MATH101', 'Calculus I', 'MATH01', 'WS002', 'MS001'),
            ('MATH102', 'Linear Algebra', 'MATH01', 'WS003', 'MS002'),
            ('MATH103', 'Statistics', 'MATH01', 'WS003', 'MS003'),
            ('ENG1001', 'Engineering Mechanics', 'ENG001', 'WS001', 'MS001'),
            ('ENG1002', 'Circuit Theory', 'ENG001', 'WS002', 'MS002'),
            ('ENG1003', 'Thermodynamics', 'ENG001', 'WS003', 'MS003'),
        ]
        for mod_id, mod_name, course_id, welfare_id, module_id in modules:
            cursor.execute("""
                INSERT IGNORE INTO module (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (mod_id, mod_name, course_id, welfare_id, module_id))
        conn.commit()
        print(f"   ✓ Created {len(modules)} modules")
        
        # === 5. ATTENDANCE (30 records) ===
        print("\n[5/8] Seeding attendance...")
        attendance_count = 0
        base_date = datetime.now().date() - timedelta(days=60)
        
        for stud_id, _, course_id in students:
            # Get modules for student's course
            student_modules = [m for m in modules if m[2] == course_id]
            
            for mod_id, _, _, _, _ in student_modules[:2]:  # First 2 modules
                # Create 3 attendance records per module
                for week in range(1, 4):
                    date = base_date + timedelta(days=week*7)
                    missed = random.choice([False, False, False, True])  # 75% attendance rate
                    cursor.execute("""
                        INSERT IGNORE INTO attendance (week_no, mod_id, stud_id, date, missed) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (week, mod_id, stud_id, date, missed))
                    attendance_count += 1
        
        conn.commit()
        print(f"   ✓ Created {attendance_count} attendance records")
        
        # === 6. SURVEYS (25 records) ===
        print("\n[6/8] Seeding surveys...")
        survey_count = 0
        
        for stud_id, _, course_id in students:
            student_modules = [m for m in modules if m[2] == course_id]
            
            for mod_id, _, _, _, _ in student_modules[:2]:
                # 2 surveys per student per module
                for week in range(1, 3):
                    date = base_date + timedelta(days=week*7)
                    stress = random.randint(1, 5)
                    sleep = round(random.uniform(4.0, 9.0), 1)
                    comments = f"Week {week} feedback" if random.random() > 0.5 else "NO COMMENTS"
                    
                    cursor.execute("""
                        INSERT IGNORE INTO surveys 
                        (week_no, stud_id, mod_id, stress_levels, hours_slept, comments, date) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (week, stud_id, mod_id, stress, sleep, comments, date))
                    survey_count += 1
        
        conn.commit()
        print(f"   ✓ Created {survey_count} survey records")
        
        # === 7. DEADLINES (35 records) ===
        print("\n[7/8] Seeding deadlines...")
        deadline_count = 0
        
        for stud_id, _, course_id in students:
            student_modules = [m for m in modules if m[2] == course_id]
            
            for mod_id, _, _, _, _ in student_modules:
                # 5 deadlines per student per module
                for i in range(1, 6):
                    due_date = datetime.now().date() + timedelta(days=i*10)
                    submitted = random.choice([True, False])
                    
                    cursor.execute("""
                        INSERT IGNORE INTO deadlines 
                        (stud_id, mod_id, week_no, ass_name, due_date, Submitted) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (stud_id, mod_id, i*2, f"Assignment {i}", due_date, submitted))
                    deadline_count += 1
        
        conn.commit()
        print(f"   ✓ Created {deadline_count} deadline records")
        
        # === 8. GRADES (20 records) ===
        print("\n[8/8] Seeding grades...")
        grade_count = 0
        
        for stud_id, _, course_id in students:
            student_modules = [m for m in modules if m[2] == course_id]
            
            for mod_id, _, _, _, _ in student_modules[:2]:  # Grade for first 2 modules
                grade = random.randint(50, 100)
                cursor.execute("""
                    INSERT IGNORE INTO module_grades (stud_id, mod_id, grade) 
                    VALUES (%s, %s, %s)
                """, (stud_id, mod_id, grade))
                grade_count += 1
        
        conn.commit()
        print(f"   ✓ Created {grade_count} grade records")
        
        print("\n" + "=" * 60)
        print("DATA SEEDING COMPLETE!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  • {len(courses)} courses")
        print(f"  • {len(users)} users (1 admin, 3 welfare, 3 module_staff, 7 students)")
        print(f"  • {len(students)} student profiles")
        print(f"  • {len(modules)} modules")
        print(f"  • {attendance_count} attendance records")
        print(f"  • {survey_count} survey responses")
        print(f"  • {deadline_count} deadlines")
        print(f"  • {grade_count} grades")
        print("\nTest Credentials:")
        print("  Admin    -> User: ADMIN01, Pass: admin123")
        print("  Welfare  -> User: WS001, Pass: welfare123")
        print("  Module   -> User: MS001, Pass: module123")
        print("  Student  -> User: STU001, Pass: student123")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    seed_data()
