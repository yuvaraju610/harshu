import streamlit as st
import pandas as pd
import hashlib
import base64
import requests
import sqlite3

# Utility functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Database functions
def create_connection(mentor_mentee_app):
    conn = None
    try:
        conn = sqlite3.connect(mentor_mentee_app)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    );''')
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                        username TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        roll_no TEXT NOT NULL,
                        phone TEXT CHECK(length(phone) == 10),
                        test_marks TEXT NOT NULL,
                        certifications TEXT,
                        projects TEXT,
                        academic_issues TEXT,
                        FOREIGN KEY (username) REFERENCES users (username)
                    );''')
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        mentor_username TEXT NOT NULL,
                        student_username TEXT NOT NULL,
                        feedback TEXT NOT NULL,
                        FOREIGN KEY (mentor_username) REFERENCES users (username),
                        FOREIGN KEY (student_username) REFERENCES users (username)
                    );''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def save_user_data(user_data, conn):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  (user_data['username'], user_data['password'], user_data['role']))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def load_user_data(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        rows = c.fetchall()
        return pd.DataFrame(rows, columns=['username', 'password', 'role'])
    except sqlite3.Error as e:
        print(e)
        return pd.DataFrame(columns=['username', 'password', 'role'])

def save_student_details(student_details, conn):
    try:
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO students (username, name, roll_no, phone, test_marks, certifications, projects, academic_issues) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (student_details['username'], student_details['name'], student_details['roll_no'], 
                   student_details['phone'], student_details['test_marks'], student_details['certifications'], 
                   student_details['projects'], student_details['academic_issues']))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def load_student_details(conn, username=None):
    try:
        c = conn.cursor()
        if username:
            c.execute("SELECT * FROM students WHERE username = ?", (username,))
        else:
            c.execute("SELECT * FROM students")
        rows = c.fetchall()
        return pd.DataFrame(rows, columns=['username', 'name', 'roll_no', 'phone', 'test_marks', 
                                           'certifications', 'projects', 'academic_issues'])
    except sqlite3.Error as e:
        print(e)
        return pd.DataFrame(columns=['username', 'name', 'roll_no', 'phone', 'test_marks', 
                                     'certifications', 'projects', 'academic_issues'])

def save_feedback(feedback_data, conn):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO feedback (mentor_username, student_username, feedback) VALUES (?, ?, ?)", 
                  (feedback_data['mentor_username'], feedback_data['student_username'], feedback_data['feedback']))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def load_feedback(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM feedback")
        rows = c.fetchall()
        return pd.DataFrame(rows, columns=['mentor_username', 'student_username', 'feedback'])
    except sqlite3.Error as e:
        print(e)
        return pd.DataFrame(columns=['mentor_username', 'student_username', 'feedback'])

def delete_student(username, conn):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE username = ?", (username,))
        c.execute("DELETE FROM feedback WHERE student_username = ?", (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def get_base64_of_url_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode()
    return ""
def check_role(username, role, conn):
    try:
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username = ?", (username,))
        stored_role = c.fetchone()
        if stored_role and stored_role[0] == role:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(e)
        return False
# Streamlit app
def main():
    conn = create_connection("mentor_mentee_app.db")
    create_tables(conn)
    
    # Get the base64 encoded image
    img_url = 'https://th.bing.com/th/id/R.5e808ce28c3614e93d7989cf9f8e1743?rik=ONqobzODJm2T3Q&riu=http%3a%2f%2feskipaper.com%2fimages%2fblue-background-7.jpg&ehk=Tf%2fi57oHAty4B2tEefVF09Zsa8LwgdKZRq65DNKmuuA%3d&risl=&pid=ImgRaw&r=0'
    img_base64 = get_base64_of_url_image(img_url)
    img_style = f"""
    <style>
    .main {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    }}
    h1, h2, label {{
    color: #ffffff !important; 
    font-family: 'Helvetica', Gadget, sans-serif; 
    font-weight: bold; 
    }}
    .stButton > button {{
    background-color: #0073e6; 
    color:white; 
    font-weight: bold;
    }}
    .css-1d391kg {{
    background-color: rgba(0, 0, 0, 0.5) !important; 
    padding: 20px; 
    border-radius: 10px;
    }}
    .css-10trblm {{
    font-weight: bold;
    }}
    .stSubheader {{
    color: #ffffff !important; /* Change subheader text color to white */
    }}
    .st-success {{
    background-color: #00cc66;
    color: white;
    padding: 10px;
    font-weight: bold;
    border-radius: 5px;
    }}
    .ststudent_usernames{{
     color: #ffffff !important;
    }}
    </style>
    """
    st.markdown(img_style, unsafe_allow_html=True)
    st.title("MENTOR - MENTEE APP")
    
    # Initialize session state variables
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'role' not in st.session_state:
        st.session_state['role'] = ''
    if 'selected_student' not in st.session_state:
        st.session_state['selected_student'] = None
    if 'subjects' not in st.session_state:
        st.session_state['subjects'] = [{'subject': '', 'marks': ''}]
    
    def go_to_page(page_name):
        st.session_state['page'] = page_name
        st.experimental_rerun()

    if st.session_state['page'] == 'Home':
        st.subheader("Home")
        st.write("Welcome to the Mentor-Mentee App.")
        if st.button("Go to Login"):
            go_to_page('Login')
        if st.button("Go to SignUp"):
            go_to_page('SignUp')

    elif st.session_state['page'] == 'SignUp':
        st.subheader("Create New Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Role", ["Mentor", "Student"])

        if st.button("Signup"):
            hashed_password = make_hashes(password)
            user_data = {'username': username, 'password': hashed_password, 'role': role}
            save_user_data(user_data, conn)
            st.success("You have successfully created an account")
            st.info("Go to Login Menu to login")
        if st.button("Back to Home"):
            go_to_page('Home')

    elif st.session_state['page'] == 'Login':
        st.subheader("Login Section")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Role", ["Mentor", "Student"])

        if st.button("Login"):
            user_data = load_user_data(conn)
            hashed_password = make_hashes(password)
            if username in user_data['username'].values:
                if check_hashes(password, user_data[user_data['username'] == username]['password'].values[0]) and check_role(username, role, conn):
                    st.success(f"Logged In as {role}")
                    st.session_state['login_status'] = True
                    st.session_state['username'] = username
                    st.session_state['role'] = role
                    if role == 'Student':
                        go_to_page('Student')
                    elif role == 'Mentor':
                        go_to_page('Mentor')
                else:
                    st.warning("Incorrect Username/Password or Role")
            else:
                st.warning("Incorrect Username/Password or Role")
        if st.button("Back to Home"):
            go_to_page('Home')

    elif st.session_state['page'] == 'Student':
        st.subheader("Student Details Form")
        students_data = load_student_details(conn, st.session_state['username'])
        
        if not students_data.empty:
            student_data = students_data.iloc[0]
            name = st.text_input("Name", value=student_data['name'])
            roll_no = st.text_input("Roll Number", value=student_data['roll_no'])
            phone = st.text_input("Phone Number", value=str(student_data['phone']))
            st.session_state['subjects'] = eval(student_data['test_marks'])
            certifications = st.text_area("Certifications", value=student_data['certifications'])
            projects = st.text_area("Projects", value=student_data['projects'])
            academic_issues = st.text_area("Academic Issues", value=student_data['academic_issues'])
        else:
            name = st.text_input("Name")
            roll_no = st.text_input("Roll Number")
            phone = st.text_input("Phone Number")
            certifications = st.text_area("Certifications")
            projects = st.text_area("Projects")
            academic_issues = st.text_area("Academic Issues")

        st.subheader("Test Marks")
        subjects = st.session_state['subjects']

        for i, subject in enumerate(subjects):
            cols = st.columns([3, 2, 1])
            with cols[0]:
                subject['subject'] = st.text_input(f"Subject {i+1}", subject['subject'], key=f"subject_{i}")
            with cols[1]:
                subject['marks'] = st.text_input(f"Marks {i+1}", subject['marks'], key=f"marks_{i}")
            with cols[2]:
                if st.button(f"Remove {i+1}", key=f"remove_{i}"):
                    subjects.pop(i)
                    st.experimental_rerun()
        if st.button("Add Subject", key="add_subject"):
            subjects.append({'subject': '', 'marks': ''})
        st.session_state['subjects'] = subjects
        if st.button("Submit Details", key="submit_details"):
            test_marks = str(st.session_state['subjects'])
            student_details = {
                'username': st.session_state['username'],
                'name': name,
                'roll_no': roll_no,
                'phone': phone,
                'test_marks': test_marks,
                'certifications': certifications,
                'projects': projects,
                'academic_issues': academic_issues
            }
            save_student_details(student_details, conn)
            st.success("Details Submitted Successfully")

        # Display feedback for the student
        st.subheader("Mentor Feedback")
        feedback_data = load_feedback(conn)
        student_feedback = feedback_data[feedback_data['student_username'] == st.session_state['username']]
        if not student_feedback.empty:
            for _, feedback in student_feedback.iterrows():
                st.write(f"Mentor: {feedback['mentor_username']}")
                st.write(f"Feedback: {feedback['feedback']}")
                st.write("---")
        else:
            st.write("No feedback available yet.")

        if st.session_state['login_status'] and st.button("Logout"):
            st.session_state['login_status'] = False
            st.session_state['username'] = ''
            st.session_state['role'] = ''
            st.session_state['selected_student'] = None
            st.session_state['subjects'] = [{'subject': '', 'marks': ''}]
            go_to_page('Home')

    elif st.session_state['page'] == 'Mentor':
        st.subheader("Mentor Section")
        # Provide feedback functionality
        st.subheader("Provide Feedback")
        students_data = load_student_details(conn)
        feedback_data = load_feedback(conn)
        student_usernames = students_data['username'].unique().tolist()
        if st.session_state['selected_student'] is None:
            selected_student = st.selectbox("Select a Student", student_usernames)
            if st.button("Select"):
                st.session_state['selected_student'] = selected_student
                st.experimental_rerun()
        else:
            selected_student = st.session_state['selected_student']
            st.subheader(f"Providing Feedback for {selected_student}")
            student_data = students_data[students_data['username'] == selected_student].iloc[0]
            st.write(f"Name: {student_data['name']}")
            st.write(f"Roll Number: {student_data['roll_no']}")
            st.write(f"Phone Number: {student_data['phone']}")
            st.write("Test Marks:")
            for subject in eval(student_data['test_marks']):
                st.write(f"{subject['subject']}: {subject['marks']}")
            st.write(f"Certifications: {student_data['certifications']}")
            st.write(f"Projects: {student_data['projects']}")
            st.write(f"Academic Issues: {student_data['academic_issues']}")
            feedback = st.text_area("Provide Feedback")
            if st.button("Submit Feedback"):
                feedback_data = {'mentor_username': st.session_state['username'], 'student_username': selected_student, 'feedback': feedback}
                save_feedback(feedback_data, conn)
                st.success("Feedback Submitted")

         # Remove student functionality
        st.subheader("Remove Student")
        students_data = load_student_details(conn)
        student_usernames = students_data['username'].unique().tolist()
        selected_student_to_remove = st.selectbox("Select a Student to Remove", student_usernames)
        if st.button("Remove Student"):
            if selected_student_to_remove:
                if not students_data[students_data['username'] == selected_student_to_remove].empty:
                    delete_student(selected_student_to_remove, conn)
                    st.success(f"Student {selected_student_to_remove} has been removed.")
                    st.experimental_rerun()
                else:
                    st.error("No details found for this student.")
            else:
                st.error("No student selected for removal.")


        if st.session_state['login_status'] and st.button("Logout"):
            st.session_state['login_status'] = False
            st.session_state['username'] = ''
            st.session_state['role'] = ''
            st.session_state['selected_student'] = None
            st.session_state['subjects'] = [{'subject': '', 'marks': ''}]
            go_to_page('Home')

if __name__ == "__main__":
    main()