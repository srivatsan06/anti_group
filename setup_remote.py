"""
Remote Database Setup Script
Initializes FreeSQLDatabase with tables and seed data.
"""
import mysql.connector
import bcrypt
from datetime import datetime, timedelta
import random

# Remote database credentials
DB_CONFIG = {
    'host': 'sql8.freesqldatabase.com',
    'user': 'sql8810071',
    'password': 'QTS5mGlaDF',
    'database': 'sql8810071',
    'port': 3306
}

def setup_remote_database():
    """Create tables and seed data on remote database."""
    
    print("=" * 60)
    print("REMOTE DATABASE SETUP")
    print("=" * 60)
    
    try:
        # Connect
        print("\n[1/2] Connecting to remote database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        print("✓ Connected to sql8.freesqldatabase.com")
        
        # Set timeout to fail fast if locked (5 seconds)
        cursor.execute("SET SESSION lock_wait_timeout = 5")
        
        # Drop existing tables first
        print("\n[2/3] Dropping existing tables...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        tables = ['module_grades', 'deadlines', 'surveys', 'attendance', 
                  'module', 'student', 'users', 'course']
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"  → Dropped {table}")
            except Exception as e:
                print(f"  ⚠ Could not drop {table}: {e}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("✓ Old tables dropped")
        
        # Create tables
        print("\n[3/3] Creating tables...")
        
        # Course
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course(
                `course_id` varchar(6) PRIMARY KEY, 
                `course_name` varchar(100) NOT NULL
            );
        """)
        
        # Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                `user_id` varchar(8) PRIMARY KEY, 
                `user_name` varchar(30) NOT NULL, 
                `role` ENUM ('module_staff','welfare_staff','admin','student') NOT NULL, 
                `email` varchar(40), 
                `hash_pass` varchar(255) NOT NULL
            );
        """)
        
        # Student
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                `stud_id` varchar(8) PRIMARY KEY, 
                `year` INT NOT NULL, 
                `course_id` varchar(6),
                FOREIGN KEY (course_id) REFERENCES course(course_id) ON UPDATE CASCADE,
                FOREIGN KEY (stud_id) REFERENCES users(user_id) ON UPDATE CASCADE
            );
        """)
        
        # Module
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS module (
                `mod_id` varchar(8) PRIMARY KEY, 
                `mod_name` varchar(100) NOT NULL, 
                `course_id` varchar(6) NOT NULL, 
                `welfare_staff_id` varchar(8) NOT NULL, 
                `module_staff_id` varchar(8) NOT NULL, 
                FOREIGN KEY (welfare_staff_id) REFERENCES users(user_id) ON UPDATE CASCADE,
                FOREIGN KEY (module_staff_id) REFERENCES users(user_id) ON UPDATE CASCADE,
                FOREIGN KEY (course_id) REFERENCES course(course_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """)
        
        # Attendance
        cursor.execute("""
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
        
        # Surveys
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS surveys (
                `week_no` INT, 
                `stud_id` varchar(8), 
                `mod_id` varchar(8), 
                `stress_levels` INT, 
                `hours_slept` DECIMAL(3,1), 
                `comments` varchar(200) DEFAULT 'NO COMMENTS', 
                `date` DATE,
                PRIMARY KEY (week_no, stud_id, mod_id), 
                FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """)
        
        # Deadlines
        cursor.execute("""
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
        
        # Grades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_grades (
                `stud_id` varchar(8) NOT NULL,
                `mod_id` varchar(8) NOT NULL,
                `grade` INT NOT NULL,
                PRIMARY KEY (stud_id, mod_id),
                FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
            );
        """)
        
        conn.commit()
        print("✓ Tables created")
        
        # Seed data
        print("\n[3/3] Seeding data...")
        seed_remote_data(conn, cursor)
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print("\nLogin Credentials:")
        print("  Admin:   ADMIN01 / admin123")
        print("  Welfare: WS001 / pass123")
        print("  Module:  MS001 / pass123")
        print("  Student: STU001 / pass123")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def seed_remote_data(conn, cursor):
    """Seed the database with test data."""
    
    # Courses
    print("  → Courses...")
    courses = [
        ('CS1010', 'Computer Science for ai'),
        ('MATH001', 'advanced Mathematics'),
        ('ENG0021', 'Engineering chemistry')
    ]
    for course_id, course_name in courses:
        cursor.execute("INSERT IGNORE INTO course VALUES (%s, %s)", (course_id, course_name))
    
    # Users (more staff + students)
    print("  → Users...")
    users = [
        ('ADMIN02', 'Admin User 2', 'admin', 'admin@university.edu', 'admin123'),
        # Welfare Staff
        ('ws20001', 'Dr. Sarah Johnson', 'welfare_staff', 'sarah.j@university.edu', 'pass123'),
        ('ws20002', 'Dr. Mark Williams', 'welfare_staff', 'mark.w@university.edu', 'pass123'),
        ('ws20003', 'Dr. Lisa Brown', 'welfare_staff', 'lisa.b@university.edu', 'pass123'),
        # Module Staff
        ('ms90001', 'Prof. John Smith', 'module_staff', 'john.smith@university.edu', 'pass123'),
        ('ms90002', 'Prof. Emily Davis', 'module_staff', 'emily.d@university.edu', 'pass123'),
        ('ms90003', 'Prof. Robert Taylor', 'module_staff', 'robert.t@university.edu', 'pass123'),
        # Students
        ('56900001', 'Alice Cooper', 'student', 'alice.c@student.edu', 'pass123'),
        ('56900002', 'Bob Martinez', 'student', 'bob.m@student.edu', 'pass123'),
        ('56900003', 'Charlie Lee', 'student', 'charlie.l@student.edu', 'pass123'),
        ('56900004', 'Diana Wang', 'student', 'diana.w@student.edu', 'pass123'),
        ('56900005', 'Eva Garcia', 'student', 'eva.g@student.edu', 'pass123'),
    ]
    
    for user_id, user_name, role, email, password in users:
        hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, user_name, role, email, hash_pass))
    
    # Students
    print("  → Students...")
    students = [
        ('56900001', 1, 'CS1010'),
        ('56900002', 1, 'CS1010'),
        ('56900003', 2, 'CS1010'),
        ('56900004', 2, 'MATH001'),
        ('56900005', 3, 'ENG0021'),
    ]
    for stud_id, year, course_id in students:
        cursor.execute("INSERT IGNORE INTO student VALUES (%s, %s, %s)", (stud_id, year, course_id))
    
    # Modules
    print("  → Modules...")
    modules = [
        ('CS110001', 'Database Systems', 'CS1010', 'ws20001', 'ms90001'),
        ('CS110002', 'Algorithms', 'CS1010', 'ws20001', 'ms90002'),
        ('CS110003', 'Web Development', 'CS1010', 'ws20002', 'ms90003'),
        ('MATH1001', 'Calculus I', 'MATH001', 'ws20002', 'ms90001'),
        ('MATH1002', 'Linear Algebra', 'MATH001', 'ws20003', 'ms90002'),
        ('ENG10001', 'Engineering Mechanics', 'ENG0021', 'ws20003', 'ms90001'),
    ]
    for mod_id, mod_name, course_id, welfare_id, module_id in modules:
        cursor.execute("""
            INSERT IGNORE INTO module (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (mod_id, mod_name, course_id, welfare_id, module_id))
    
    conn.commit()
    
    # Attendance
    print("  → Attendance...")
    base_date = datetime.now().date() - timedelta(days=60)
    attendance_count = 0
    
    for stud_id, year, course_id in students:
        # Get modules for student's course
        student_modules = [m for m in modules if m[2] == course_id]
        
        for mod_id, _, _, _, _ in student_modules[:2]:  # First 2 modules
            for week in range(1, 6):  # 5 weeks
                date = base_date + timedelta(days=week*7)
                missed = random.choice([False, False, False, True])  # 75% attendance
                cursor.execute("""
                    INSERT IGNORE INTO attendance (week_no, mod_id, stud_id, date, missed) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (week, mod_id, stud_id, date, missed))
                attendance_count += 1
    
    conn.commit()
    print(f"     Created {attendance_count} attendance records")
    
    # Surveys
    print("  → Surveys...")
    survey_count = 0
    
    for stud_id, year, course_id in students:
        student_modules = [m for m in modules if m[2] == course_id]
        
        for mod_id, _, _, _, _ in student_modules[:2]:
            for week in range(1, 4):  # 3 weeks
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
    print(f"     Created {survey_count} survey records")
    
    # Deadlines
    print("  → Deadlines...")
    deadline_count = 0
    
    for stud_id, year, course_id in students:
        student_modules = [m for m in modules if m[2] == course_id]
        
        for mod_id, _, _, _, _ in student_modules[:2]:
            for i in range(1, 4):  # 3 deadlines per module
                due_date = datetime.now().date() + timedelta(days=i*15)
                submitted = random.choice([True, False])
                
                cursor.execute("""
                    INSERT IGNORE INTO deadlines 
                    (stud_id, mod_id, week_no, ass_name, due_date, Submitted) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (stud_id, mod_id, i*2, f"Assignment {i}", due_date, submitted))
                deadline_count += 1
    
    conn.commit()
    print(f"     Created {deadline_count} deadline records")
    
    # Grades
    print("  → Grades...")
    grade_count = 0
    
    for stud_id, year, course_id in students:
        student_modules = [m for m in modules if m[2] == course_id]
        
        for mod_id, _, _, _, _ in student_modules[:2]:
            grade = random.randint(50, 100)
            cursor.execute("""
                INSERT IGNORE INTO module_grades (stud_id, mod_id, grade) 
                VALUES (%s, %s, %s)
            """, (stud_id, mod_id, grade))
            grade_count += 1
    
    conn.commit()
    print(f"     Created {grade_count} grade records")
    
    print("\n✓ All data seeded successfully!")

if __name__ == "__main__":
    response = input("\nInitialize remote database? (yes/no): ")
    if response.lower() == 'yes':
        setup_remote_database()
    else:
        print("Cancelled.")
