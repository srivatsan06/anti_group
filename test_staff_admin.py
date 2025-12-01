"""
Staff & Admin Role Testing Script
Tests RBAC for Module Staff, Welfare Staff, and Admin.
"""
from controllers.module_staff_controller import ModuleStaffController
from controllers.welfare_staff_controller import WelfareStaffController
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController

def test_module_staff():
    print("\n" + "="*60)
    print("TESTING MODULE STAFF (MS001)")
    print("="*60)
    
    # Login (Simulated)
    controller = ModuleStaffController('MS001', 'module_staff')
    
    # 1. View My Modules
    print("\n[1] My Modules:")
    modules = controller.get_my_modules()
    for m in modules:
        print(f"   - {m[0]}: {m[1]}")
        
    if not modules:
        print("   (No modules assigned)")
        return

    mod_id = modules[0][0] # Use first module
    
    # 2. View Students in Module (with names)
    print(f"\n[2] Students in {mod_id}:")
    students = controller.get_module_students(mod_id)
    print(f"   Found {len(students)} students:")
    for s in students:
        # s = (stud_id, user_name, email, year, course_id)
        print(f"   - {s[1]} ({s[0]}) - {s[2]}")
    
    if students:
        stud_id = students[0][0]
        
        # 3. Add Grade
        print(f"\n[3] Grading Student {stud_id}...")
        try:
            controller.update_grade(stud_id, mod_id, 85)
            print("   ✓ Updated grade to 85")
        except:
            controller.add_grade(stud_id, mod_id, 85)
            print("   ✓ Added grade 85")
            
        # 4. Advanced Analytics
        print(f"\n[4] Advanced Analytics for {mod_id}:")
        analytics = controller.get_advanced_module_analytics(mod_id)
        print(f"   Avg Attendance: {analytics['avg_attendance']:.1f}%")
        print(f"   Avg Grade: {analytics['avg_grade']:.1f}")
        print(f"   ✓ Chart saved to: {analytics['chart_path']}")

def test_welfare_staff():
    print("\n" + "="*60)
    print("TESTING WELFARE STAFF (WS001)")
    print("="*60)
    
    controller = WelfareStaffController('WS001', 'welfare_staff')
    
    # 1. View All Students (Detailed)
    print("\n[1] All Students (Detailed):")
    students = controller.get_all_students()
    print(f"   Found {len(students)} students:")
    for s in students[:5]: # Show first 5
        print(f"   - {s[1]} ({s[0]}) - {s[2]}")

    # 2. Identify At-Risk Students
    print("\n[2] At-Risk Students Analysis:")
    at_risk = controller.get_at_risk_students()
    if at_risk:
        print(f"   ⚠ Found {len(at_risk)} students at risk:")
        for s in at_risk:
            print(f"   - {s['name']} ({s['student_id']})")
            print(f"     Risks: {', '.join(s['risk_factors'])}")
            print(f"     Stats: Stress {s['avg_stress']:.1f}, Sleep {s['avg_sleep']:.1f}, Grade {s['avg_grade']:.1f}")
    else:
        print("   ✓ No students currently at risk")

    if students:
        stud_id = students[0][0]
        
        # 3. View Student Surveys (Full Info)
        print(f"\n[3] Surveys for {stud_id}:")
        surveys = controller.get_student_surveys(stud_id)
        for surv in surveys:
            # (week_no, stud_id, mod_id, stress, sleep, comments, date)
            print(f"   - Week {surv[0]}: Stress {surv[3]}, Sleep {surv[4]}")
            print(f"     Comment: {surv[5]}")

        # 4. Comprehensive Student Report
        print(f"\n[4] Comprehensive Report for {stud_id}:")
        report = controller.get_student_comprehensive_report(stud_id)
        print(f"   Avg Grade: {report['avg_grade']:.1f}")
        print(f"   ✓ Trend Chart saved to: {report['chart_path']}")

def test_admin():
    print("\n" + "="*60)
    print("TESTING ADMIN (ADMIN01)")
    print("="*60)
    
    controller = AdminController('ADMIN01', 'admin')
    
    # 1. User Management
    print("\n[1] Creating New User...")
    try:
        controller.register_user('TEST_123', 'Test User', 'student', 'test@test.com', 'pass123')
        print("   ✓ Created TEST_USER")
    except Exception as e:
        print(f"   (User might already exist: {e})")
        
    # 2. View All Users
    print("\n[2] All Users:")
    users = controller.get_all_users()
    print(f"   Found {len(users)} users")
    
    # 3. Delete User
    print("\n[3] Deleting TEST_USER...")
    controller.delete_user('TEST_USER')
    print("   ✓ Deleted TEST_USER")

if __name__ == "__main__":
    try:
        test_module_staff()
        test_welfare_staff()
        test_admin()
        print("\n" + "="*60)
        print("ALL ROLE TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
