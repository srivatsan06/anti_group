-- University Management System Database Schema

-- 1. Course Table
CREATE TABLE IF NOT EXISTS course (
    `course_id` varchar(6) PRIMARY KEY,
    `course_name` varchar(100) NOT NULL
);

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
    `user_id` varchar(8) PRIMARY KEY,
    `user_name` varchar(30) NOT NULL,
    `role` ENUM ('module_staff', 'welfare_staff', 'admin', 'student') NOT NULL,
    `email` varchar(40),
    `hash_pass` varchar(255) NOT NULL
);

-- 3. Student Table
CREATE TABLE IF NOT EXISTS student (
    `stud_id` varchar(8) PRIMARY KEY,
    `year` INT NOT NULL,
    `course_id` varchar(6),
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON UPDATE CASCADE,
    FOREIGN KEY (stud_id) REFERENCES users(user_id) ON UPDATE CASCADE
);

-- 4. Module Table
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

-- 5. Attendance Table
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

-- 6. Surveys Table
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

-- 7. Deadlines Table
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

-- 8. Module Grades Table
CREATE TABLE IF NOT EXISTS module_grades (
    `stud_id` varchar(8) NOT NULL,
    `mod_id` varchar(8) NOT NULL,
    `grade` INT NOT NULL,
    PRIMARY KEY (stud_id, mod_id),
    FOREIGN KEY (stud_id) REFERENCES student(stud_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (mod_id) REFERENCES module(mod_id) ON UPDATE CASCADE ON DELETE CASCADE
);
