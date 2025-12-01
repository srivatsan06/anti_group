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
        
        # Create tables
        print("\n[2/2] Creating tables...")
        
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
    courses = [
        ('CS101', 'Computer Science'),
        ('MATH01', 'Mathematics'),
        ('ENG001', 'Engineering')
    ]
    for course_id, course_name in courses:
        cursor.execute("INSERT IGNORE INTO course VALUES (%s, %s)", (course_id, course_name))
    
    # Users
    users = [
        ('ADMIN01', 'Admin User', 'admin', 'admin@university.edu', 'admin123'),
        ('WS001', 'Dr. Sarah Johnson', 'welfare_staff', 'sarah.j@university.edu', 'pass123'),
        ('MS001', 'Prof. John Smith', 'module_staff', 'john.smith@university.edu', 'pass123'),
        ('STU001', 'Alice Cooper', 'student', 'alice.c@student.edu', 'pass123'),
        ('STU002', 'Bob Martinez', 'student', 'bob.m@student.edu', 'pass123'),
        ('STU003', 'Charlie Lee', 'student', 'charlie.l@student.edu', 'pass123'),
    ]
    
    for user_id, user_name, role, email, password in users:
        hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT IGNORE INTO users (user_id, user_name, role, email, hash_pass) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, user_name, role, email, hash_pass))
    
    # Students
    students = [
        ('STU001', 1, 'CS101'),
        ('STU002', 1, 'CS101'),
        ('STU003', 2, 'MATH01'),
    ]
    for stud_id, year, course_id in students:
        cursor.execute("INSERT IGNORE INTO student VALUES (%s, %s, %s)", (stud_id, year, course_id))
    
    # Modules
    modules = [
        ('CS11001', 'Database Systems', 'CS101', 'WS001', 'MS001'),
        ('MATH101', 'Calculus I', 'MATH01', 'WS001', 'MS001'),
    ]
    for mod_id, mod_name, course_id, welfare_id, module_id in modules:
        cursor.execute("""
            INSERT IGNORE INTO module (mod_id, mod_name, course_id, welfare_staff_id, module_staff_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (mod_id, mod_name, course_id, welfare_id, module_id))
    
    conn.commit()
    print("✓ Seeded courses, users, students, and modules")

if __name__ == "__main__":
    response = input("\nInitialize remote database? (yes/no): ")
    if response.lower() == 'yes':
        setup_remote_database()
    else:
        print("Cancelled.")
