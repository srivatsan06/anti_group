from Definition_new import TableDefinition
from CRUD_new import Student, Course, Module, Deadlines, Analytics, Surveys
import datetime

def test_features():
    print("--- Initializing DB ---")
    # Initialize Tables (Safe to run multiple times due to IF NOT EXISTS)
    td = TableDefinition()
    td.table_definition()

    print("\n--- Setting up Test Data ---")
    # 1. Register Course
    course = Course()
    course.register_course("CS101", "Computer Science")

    # 2. Register Student
    student = Student()
    # Note: Using a random ID to avoid collision if running multiple times, or just handle error
    stud_id = "S99999"
    student.register_student(stud_id, "Test Student", 1, "CS101", "pass123", "test@example.com")

    # 3. Register Module
    module = Module()
    mod_id = "M99999"
    # We need valid welfare/module staff IDs. Assuming 'admin' exists or we need to create them.
    # Let's try to create a dummy admin/staff first.
    from CRUD_new import Users
    users = Users()
    users.register_user("U99999", "Test Staff", "module_staff", "pass123", "staff@example.com")
    
    module.register_module(mod_id, "Test Module", "CS101", 1, "U99999", "U99999")

    # 4. Set Deadline
    deadlines = Deadlines()
    dead_id = "D99999"
    deadlines.set_deadlines(dead_id, mod_id, 10, "2025-12-25", "Final Project")

    print("\n--- Testing Student Features ---")
    # Test get_my_deadlines
    my_deadlines = student.get_my_deadlines(stud_id)
    print(f"Deadlines for {stud_id}: {my_deadlines}")
    assert len(my_deadlines) > 0, "Should have at least one deadline"

    # Test Survey
    surveys = Surveys()
    # Submit survey (using the new method in Student or Surveys class? Student has submit_daily_survey)
    student.submit_daily_survey(stud_id, mod_id, 3, 7.5, "Feeling okay")
    
    # Check if submitted
    has_submitted = student.check_survey_today(stud_id)
    print(f"Survey submitted today? {has_submitted}")
    assert has_submitted == True

    print("\n--- Testing Analytics ---")
    analytics = Analytics()
    stats = analytics.get_course_statistics(mod_id)
    print(f"Course Stats for {mod_id}: {stats}")
    
    wellbeing = analytics.get_wellbeing_by_module(mod_id)
    print(f"Wellbeing for {mod_id}: {wellbeing}")

    print("\n--- SUCCESS: All tests passed! ---")

if __name__ == "__main__":
    test_features()
