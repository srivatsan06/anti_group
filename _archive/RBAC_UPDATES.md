# Updated RBAC Rules - StudentController

## Changes Made

All methods in `StudentController` now support **flexible RBAC**:

### **Students** 
- Can only view their **own** data
- Cannot specify `stud_id` parameter (defaults to `current_user_id`)

### **Module Staff**
- Can view **any student's** attendance, grades, and analytics
- Must specify `stud_id` parameter

### **Welfare Staff**
- Can view **any student's** surveys, attendance, grades, and analytics
- Must specify `stud_id` parameter

### **Admin**
- Can view **all data** for any student
- Full access via `stud_id` parameter

## Updated Methods

1. **`get_my_attendance(mod_id, stud_id)`**
   - Students: Own attendance only
   - Staff/Admin: Any student's attendance

2. **`get_my_attendance_analytics(mod_id, stud_id)`**
   - Students: Own analytics only
   - Module/Welfare/Admin: Any student's analytics

3. **`get_my_surveys(mod_id, stud_id)`**
   - Students: Own surveys only
   - Welfare/Admin: Any student's surveys

4. **`get_my_grades(mod_id, stud_id)`**
   - Students: Own grades only
   - Module/Welfare/Admin: Any student's grades

5. **`get_my_grade_analytics(stud_id)`**
   - Students: Own analytics only
   - Module/Welfare/Admin: Any student's analytics

## Usage Examples

```python
# Student accessing their own data
controller = StudentController('STU001', 'student')
attendance = controller.get_my_attendance(mod_id='CS11001')  # Auto-uses STU001

# Module Staff accessing student data
controller = StudentController('MS001', 'module_staff')
attendance = controller.get_my_attendance(mod_id='CS11001', stud_id='STU001')  # Specify student

# Admin viewing analytics
controller = StudentController('ADMIN01', 'admin')
analytics = controller.get_my_grade_analytics(stud_id='STU001')  # Any student
```

## Security

✅ Students **cannot** access other students' data (PermissionError)  
✅ Staff can only access within their authorized scope  
✅ Unauthorized roles blocked
