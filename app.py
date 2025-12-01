"""
Streamlit Application - Main Entry Point
"""
import streamlit as st
import pandas as pd
import os
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.module_staff_controller import ModuleStaffController
from controllers.welfare_staff_controller import WelfareStaffController
from controllers.admin_controller import AdminController

# Page Config
st.set_page_config(page_title="University Management System", layout="wide")

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.user_name = None

# --- Auth Functions ---
def login():
    st.title("🎓 University Management System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Login")
        user_id = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            auth = AuthController()
            if auth.login(user_id, password):

                from models.user import UserModel
                from utils.db_connection import get_connection
                conn, cursor = get_connection()
                user_model = UserModel(conn, cursor)
                user = user_model.find_by_id(user_id)
                
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_name = user[1]
                st.session_state.role = user[2]
                st.rerun()
            else:
                st.error("Invalid credentials")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.rerun()


def student_dashboard():
    st.sidebar.title(f"Welcome, {st.session_state.user_name}")
    st.sidebar.write(f"Role: {st.session_state.role}")
    if st.sidebar.button("Logout"):
        logout()

    controller = StudentController(st.session_state.user_id, 'student')
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([" Profile", "My Modules", "Attendance", "Grades", "Deadlines", "Surveys"])
    
    with tab1:
        st.header("My Profile")
        profile = controller.get_my_profile()
        if profile:
            st.write(f"**Name:** {st.session_state.user_name}")
            st.write(f"**Student ID:** {profile[0]}")
            st.write(f"**Year:** {profile[1]}")
            st.write(f"**Course:** {profile[2]}")
    
    with tab2:
        st.header("Enrolled Modules")
        modules = controller.get_my_modules()
        if modules:
            df = pd.DataFrame(modules, columns=['ID', 'Name', 'Course', 'Welfare Staff', 'Module Staff'])
            st.dataframe(df[['ID', 'Name', 'Module Staff']])
        else:
            st.info("No modules found.")

    with tab3:
        st.header("Attendance Analytics")
        modules = controller.get_my_modules()
        if modules:
            mod_id = st.selectbox("Select Module", [m[0] for m in modules], key='att_mod')
            if mod_id:
                stats = controller.get_my_attendance_analytics(mod_id)
                col1, col2, col3 = st.columns(3)
                col1.metric("Attended", stats['attended'])
                col2.metric("Missed", stats['missed'])
                col3.metric("Percentage", f"{stats['percentage']}%")
                st.progress(stats['percentage'] / 100)

    with tab4:
        st.header("Grade Analytics")
        analytics = controller.get_my_grade_analytics()
        st.metric("Average Grade", f"{analytics['average_grade']:.2f}")
        
        if analytics['modules']:
            st.subheader("Module Breakdown")
            df = pd.DataFrame(analytics['modules'])
            st.dataframe(df)
            st.bar_chart(df.set_index('module_name')['grade'])

    with tab5:
        st.header("Upcoming Deadlines")
        deadlines = controller.get_my_deadlines()
        if deadlines:
            upcoming = [d for d in deadlines if d[5] == 0]
            if upcoming:
                df = pd.DataFrame(upcoming, columns=['Stud ID', 'Mod ID', 'Week', 'Assignment', 'Due Date', 'Submitted'])
                st.dataframe(df[['Mod ID', 'Assignment', 'Due Date', 'Week']])
            else:
                st.success("No pending deadlines!")
        else:
            st.info("No deadlines found.")
    
    with tab6:
        st.header("Wellbeing Surveys")
        
        st.subheader("Submit Survey")
        modules = controller.get_my_modules()
        if modules:
            with st.form("survey_form"):
                survey_mod = st.selectbox("Module", [m[0] for m in modules], format_func=lambda x: f"{x} - {[m[1] for m in modules if m[0] == x][0]}")
                week_no = st.number_input("Week Number", min_value=1, max_value=12, value=1)
                stress = st.slider("Stress Level (1-5)", 1, 5, 3)
                sleep = st.number_input("Hours Slept", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
                comments = st.text_area("Comments (optional)")
                
                if st.form_submit_button("Submit Survey"):
                    try:
                        controller.submit_survey(survey_mod, stress, sleep, week_no, comments if comments else 'NO COMMENTS')
                        st.success("Survey submitted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No modules found. Please enroll in a module first.")
        
        st.divider()
        st.subheader("My Survey History")
        surveys = controller.get_my_surveys()
        if surveys:
            survey_df = pd.DataFrame(surveys, columns=['Week', 'Student', 'Module', 'Stress', 'Sleep', 'Comments', 'Date'])
            st.dataframe(survey_df[['Week', 'Module', 'Stress', 'Sleep', 'Date', 'Comments']])
        else:
            st.info("No surveys submitted yet.")

def module_staff_dashboard():
    st.sidebar.title(f"Staff: {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        logout()

    controller = ModuleStaffController(st.session_state.user_id, 'module_staff')
    
    my_modules = controller.get_my_modules()
    if not my_modules:
        st.warning("No modules assigned.")
        return

    mod_options = {m[0]: m[1] for m in my_modules}
    selected_mod_id = st.sidebar.selectbox("Select Module", list(mod_options.keys()), format_func=lambda x: f"{x} - {mod_options[x]}")
    
    st.title(f"Manage {selected_mod_id}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Class List", "Attendance", "Grades", "Analytics", "Student Details"])
    
    with tab1:
        st.subheader("Enrolled Students")
        students = controller.get_module_students(selected_mod_id)
        if students:
            df = pd.DataFrame(students, columns=['ID', 'Name', 'Email', 'Year', 'Course'])
            st.dataframe(df)
        else:
            st.info("No students enrolled.")

    with tab2:
        st.subheader("Attendance Management")
        col1, col2 = st.columns(2)
        with col1:
            week_no = st.number_input("Week Number", min_value=1, max_value=12, value=1)
            date = st.date_input("Date")
        
        with col2:
            stud_id_att = st.text_input("Student ID for Attendance")
            status = st.radio("Status", ["Present", "Missed"])
            missed_val = True if status == "Missed" else False
            
        if st.button("Record Attendance"):
            try:
                controller.record_attendance(week_no, selected_mod_id, stud_id_att, date, missed_val)
                st.success("Attendance recorded!")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        st.subheader("Grade Management")
        col1, col2 = st.columns(2)
        with col1:
            stud_id_grade = st.text_input("Student ID for Grade")
        with col2:
            grade_val = st.number_input("Grade", min_value=0.0, max_value=100.0)
            
        if st.button("Submit Grade"):
            try:
                try:
                    controller.update_grade(stud_id_grade, selected_mod_id, grade_val)
                    st.success("Grade updated!")
                except:
                    controller.add_grade(stud_id_grade, selected_mod_id, grade_val)
                    st.success("Grade added!")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab4:
        st.subheader("Module Analytics")
        if st.button("Generate Report"):
            analytics = controller.get_advanced_module_analytics(selected_mod_id)
            
            c1, c2 = st.columns(2)
            c1.metric("Avg Attendance", f"{analytics['avg_attendance']:.1f}%")
            c2.metric("Avg Grade", f"{analytics['avg_grade']:.1f}")
            
            st.image(analytics['chart_path'], caption="Performance Overview")

    with tab5:
        st.subheader("Individual Student Details")
        students = controller.get_module_students(selected_mod_id)
        if students:
            student_ids = [s[0] for s in students]
            selected_student = st.selectbox("Select Student", student_ids, format_func=lambda x: f"{x} - {[s[1] for s in students if s[0] == x][0]}")
            
            if selected_student:
                st.write(f"### {selected_student}")
                
                st.write("**Grade:**")
                grade_result = controller.get_student_grades_in_module(selected_mod_id, selected_student)
                if grade_result:
                    st.metric("Grade", grade_result[0][2])
                else:
                    st.info("No grade recorded yet.")
                
                st.write("**Attendance:**")
                week_filter = st.selectbox("Filter by Week (0 = All)", [0] + list(range(1, 13)))
                
                if week_filter == 0:
                    att_result = controller.get_student_attendance_in_module(selected_mod_id, selected_student)
                else:
                    att_result = controller.get_student_attendance_in_module(selected_mod_id, selected_student, week_filter)
                
                if att_result:
                    att_df = pd.DataFrame(att_result, columns=['Week', 'Date', 'Missed'])
                    att_df['Status'] = att_df['Missed'].apply(lambda x: 'Absent' if x else 'Present')
                    st.dataframe(att_df[['Week', 'Date', 'Status']])
                else:
                    st.info("No attendance records.")
        else:
            st.info("No students enrolled.")

def welfare_staff_dashboard():
    st.sidebar.title(f"Welfare: {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        logout()

    controller = WelfareStaffController(st.session_state.user_id, 'welfare_staff')
    
    st.title("Student Welfare Monitoring")
    
    tab1, tab2, tab3, tab4 = st.tabs(["At-Risk Monitor", "Student Search", "Module Analytics", "Survey Details"])
    
    with tab1:
        st.subheader("⚠️ At-Risk Students")
        st.write("Students with High Stress (>4), Low Sleep (<6h), or Low Grades (<50%)")
        
        at_risk = controller.get_at_risk_students()
        if at_risk:
            for s in at_risk:
                with st.expander(f"{s['name']} ({s['student_id']}) - {', '.join(s['risk_factors'])}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Stress", f"{s['avg_stress']:.1f}")
                    c2.metric("Sleep", f"{s['avg_sleep']:.1f}h")
                    c3.metric("Grade", f"{s['avg_grade']:.1f}")
                    st.write(f"Email: {s['email']}")
        else:
            st.success("No students currently flagged as at-risk.")

    with tab2:
        st.subheader("Student Details")
        stud_id_search = st.text_input("Enter Student ID")
        if st.button("Search"):
            try:
                report = controller.get_student_comprehensive_report(stud_id_search)
                st.metric("Overall Average Grade", f"{report['avg_grade']:.1f}")
                st.image(report['chart_path'], caption="Attendance Trend")
                
                st.subheader("Survey History")
                surveys = controller.get_student_surveys(stud_id_search)
                if surveys:

                    survey_data = []
                    for surv in surveys:
                        survey_data.append({
                            'Week': surv[0],
                            'Stress': surv[3],
                            'Sleep': surv[4],
                            'Comment': surv[5]
                        })
                    st.dataframe(pd.DataFrame(survey_data))
                else:
                    st.info("No surveys found.")
                    
            except Exception as e:
                st.error(f"Could not find student or data: {e}")

    with tab3:
        st.subheader("Module Performance Analytics")
        from models.module import ModuleModel
        from utils.db_connection import get_connection
        conn, cursor = get_connection()
        mod_model = ModuleModel(conn, cursor)
        all_modules = mod_model.find_all()
        
        if all_modules:
            mod_ids = [m[0] for m in all_modules]
            selected_mod = st.selectbox("Select Module", mod_ids, format_func=lambda x: f"{x} - {[m[1] for m in all_modules if m[0] == x][0]}")
            
            if st.button("Generate Module Report"):
                analytics = controller.get_module_analytics(selected_mod)
                c1, c2 = st.columns(2)
                c1.metric("Avg Attendance", f"{analytics['avg_attendance']:.1f}%")
                c2.metric("Avg Grade", f"{analytics['avg_grade']:.1f}")
                st.image(analytics['chart_path'], caption="Module Performance")

    with tab4:
        st.subheader("Survey Analytics")
        
        analytics = controller.get_survey_analytics()
        c1, c2 = st.columns(2)
        c1.metric("Avg Stress Level", analytics['average_stress'])
        c2.metric("Avg Sleep Hours", analytics['average_sleep'])
        
        st.divider()
        st.write("**All Survey Responses:**")
        all_surveys = controller.get_survey_details()
        if all_surveys:
            survey_df = pd.DataFrame(all_surveys, columns=['Week', 'Student', 'Module', 'Stress', 'Sleep', 'Comment', 'Date'])
            st.dataframe(survey_df)
        else:
            st.info("No surveys submitted yet.")

def admin_dashboard():
    st.sidebar.title(f"Admin: {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        logout()

    controller = AdminController(st.session_state.user_id, 'admin')
    
    st.title("System Administration")
    
    tab1, tab2 = st.tabs(["User Management", "System Overview"])
    
    with tab1:
        st.subheader("Register New User")
        with st.form("register_form"):
            new_uid = st.text_input("User ID")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            new_role = st.selectbox("Role", ["student", "module_staff", "welfare_staff", "admin"])
            new_pass = st.text_input("Password", type="password")
            
            if st.form_submit_button("Register User"):
                try:
                    controller.register_user(new_uid, new_name, new_role, new_email, new_pass)
                    st.success(f"User {new_uid} created successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        st.subheader("All Users")
        users = controller.get_all_users()
        if users:
            df = pd.DataFrame(users, columns=['User ID', 'Name', 'Role', 'Email', 'Password Hash'])
            st.dataframe(df[['User ID', 'Name', 'Role', 'Email']])
            
            st.divider()
            st.subheader("Update User")
            update_uid = st.text_input("User ID to Update")
            update_col = st.selectbox("Field to Update", ["user_name", "role", "email"])
            update_val = st.text_input("New Value")
            if st.button("Update User"):
                try:
                    controller.update_user(update_uid, update_col, update_val)
                    st.success(f"User {update_uid} updated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            
            st.divider()
            del_uid = st.text_input("Delete User ID")
            if st.button("Delete User"):
                try:
                    controller.delete_user(del_uid)
                    st.success(f"User {del_uid} deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        st.subheader("System Stats")
        st.metric("Total Users", len(users) if users else 0)

def main():
    if not st.session_state.logged_in:
        login()
    else:
        if st.session_state.role == 'student':
            student_dashboard()
        elif st.session_state.role == 'module_staff':
            module_staff_dashboard()
        elif st.session_state.role == 'welfare_staff':
            welfare_staff_dashboard()
        elif st.session_state.role == 'admin':
            admin_dashboard()
        else:
            st.error("Unknown role")

if __name__ == "__main__":
    main()
