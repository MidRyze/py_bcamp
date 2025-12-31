import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import urllib.parse
import time
# import json


# 2. Define the Dialog Function
@st.dialog("Edit Task Information", width="large")
def show_dialog_task(email, title, description, t_status, task_number):
    if t_status == 'Incomplete':
        t_status = ['Incomplete', 'Complete']
    else:
        t_status = ['Complete', 'Incomplete']

    with st.form("update_user_form"):
        edit_task_col_l, edit_task_col_r = st.columns(2)
        edit_task_submit_col, edit_task_cancel_col, edit_task_delete_col = st.columns(3)
        
        with edit_task_col_l:
            # st.write(f"Task number: {title}")
            st.write(f"Task number: {task_number}")
            new_task_description = st.text_input("Edit description", value=description)

        with edit_task_col_r:
            # st.write(f"Task number: {description}")
            new_task_title = st.text_input("Edit title", value=title)
            new_task_status = st.selectbox("Update status", options=t_status)

        with edit_task_submit_col:
            # button_label = "Save Changes" if st.session_state.edit_user else "Edit Profile"
            task_edit_submit = st.form_submit_button("Save Changes", type="secondary", width='stretch')

        with edit_task_cancel_col:
            task_edit_cancel = st.form_submit_button("Cancel", type="secondary", width='stretch')
        
        with edit_task_delete_col:
            task_edit_delete = st.form_submit_button("Delete Task", type="primary", width='stretch')

        if task_edit_submit:
            new_task_status = 1 if new_task_status == "Complete" else 0
            if new_task_title == "":
                new_task_title = title
            if new_task_description == "":
                new_task_description = description
            # if not st.session_state.edit_user:
            #     st.session_state.edit_user = True
            # else:
            st.info("⏳ Saving changes, please wait ...")
            result, success = update_user_task(email, task_number, new_task_title, new_task_description, new_task_status)
            if success:
                st.success("User updated successfully!")
                st.session_state.edit_user_task = None
                st.session_state.edit_mode_active = False
                st.rerun()
            else:
                st.error(f"❌ Error: {result.get('detail', 'Unknown error')}")
            # st.rerun() # This reruns the whole script
        elif task_edit_cancel:
            st.session_state.edit_user_task = None
            st.session_state.edit_mode_active = False
            st.rerun()
        elif task_edit_delete:
            # if not st.session_state.edit_user:
            #     st.session_state.edit_user = True
                st.rerun() # This reruns the whole script
            # else:
            #     result, success = update_user(entry, user_password, new_email, new_name, new_age)
            #     if success:
            #         st.success("User updated successfully!")
            #         st.session_state.edit_user = False
            #         st.session_state.show_dialog = False # Close dialog
            #         st.rerun()
            #     else:
            #         st.error(f"❌ Error: {result.get('detail', 'Unknown error')}")


# Configure the page
st.set_page_config(
    page_title="💾 MongoDB Database Manager",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded")

# API base URL (make sure your FastAPI server is running on this port)
API_BASE_URL = "http://localhost:8001"


def check_api_connection(): # Check if the FastAPI server is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False
    
# =============================CODE BEGINS HERE================================ #
def create_user(email, name, password, age): # Create a new user via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/users/", # <<< This command connects to the FAPI function, as per function
            params = {"email": email, "name": name, "password": password, "age": age}
            )
        return response. json(), response.status_code == 201
    except Exception as e:
        return {"error": str(e)}, False

def get_user(email): # Get all users via API
    try:
        response = requests.get(f"{API_BASE_URL}/users/{email}")
        if response.status_code == 200:
            return response. json()
        return [], False
    except Exception as e:
        return [], False

def get_all_users(): # Get all users via API
    try:
        response = requests.get(f"{API_BASE_URL}/users/")
        if response.status_code == 200:
            return response. json(), True
        return [], False
    except Exception as e:
        return [], False

def get_user_todo(email, task_number): # Get posts for a specific user"""
    try:
        params = {"task_number": task_number}
        response = requests.get(f"{API_BASE_URL}/todo/{email}",
                                params = params
                                )
        if response.status_code == 200:
            return response. json(), True
        return [], False
    except Exception as e:
        # Logging the error helps you see WHY it failed
        print(f"DEBUG: Request failed due to: {e}")
        return [], False
    
def get_single_task(email, task_number): # Get posts for a specific user"""
    try:
        # params = {"task_number": task_number}
        response = requests.get(f"{API_BASE_URL}/todo/{email}/{task_number}",
                                # params = params
                                )
        if response.status_code == 200:
            return response. json(), True
        return [], False
    except Exception as e:
        print(f"DEBUG: Request failed due to: {e}")
        return [], False

def create_task(email, title, description): # Create a new post via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/todo/",
            params={"email": email, "title": title, "description": description}
        )
        return response. json(), response.status_code == 201
    except Exception as e:
        return {"error": str(e)}, False

def get_user_todo_list(email): # Get all posts via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/todo/{email}")
        if response.status_code == 200:
            return response. json(), True
        return [], False
    except Exception as e:
        return [], False

def update_task_status(email, task_number): # Delete a task via API"""
    status = get_single_task(email, task_number)
    if status == 'Incomplete':
        status = True
    elif status == 'Complete':
        status = False
    try:
        params = {"task_number":email, 
                  "task_number":task_number,
                  "task_status":status
        }
        response = requests.put(f"{API_BASE_URL}/todo/{email}/{task_number}/status",
                                   params = params)
        return response. json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False
    
def delete_task(email, task_number = 0, delete_all = False): # Delete a task via API"""
    try:
        is_delete_all = 1 if task_number == 0 else 0
        params = {
            "task_number":task_number,
            "delete_all":is_delete_all
        }
        response = requests.delete(f"{API_BASE_URL}/todo/{email}",
                                   params = params)
        return response. json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False

def delete_user(email): # Delete a user via API"""
    try:
        encoded_email = urllib.parse.quote(email)
        response = requests.delete(f"{API_BASE_URL}/users/{email}")
        return response. json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False
    
def update_user(old_user_email, password, new_user_email, name, age): # Update a user via API"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/users/{old_user_email}",
            params={"email": old_user_email, "password": password, "new_email":new_user_email, "name": name, "age": age}
        )
        return response.json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False
    
def update_user_task(email, task_number, title, description, t_status): # Update a user via API"""
    if t_status == 'Incomplete':
        t_status = 0
    if t_status == 'Complete':
        t_status = 1
    try:
        response = requests.put(
            f"{API_BASE_URL}/todo/{email}/{task_number}/details",
            params={"email": email,
                    # "password": password,
                    "task_number":task_number,
                    "title":title,
                    "description":description,
                    "t_status":t_status}
        )
        return response.json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False
        
def main():
    st.title("My List []")
    st.write("Making To-Do Lists Great Again")
    # st.markdown("--test--")

    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to FastAPI server. Please make sure it's running on http://localhost:8001")
        st.info("Run: `python fastapi_mongo.py` to start the server")
        return

    st.info ("👌 Connected to FastAPI server")

    # Sidebar for navigation
    st.sidebar.title("🧭 Navbar")
    page = st.sidebar.selectbox(
        "Choose page",
        ["👤 Users", "🗒️ Tasks", "🖥️ Dashboard"]
    )

    if page == "👤 Users":
        users_page()
    elif page == "🗒️ Tasks":
        tasks_page()
    elif page == "🖥️ Dashboard":
        dashboard_page()


# ============================= USER PAGE ================================ #

def users_page():
    st.header("👤 User Management")

    # Create tabs for different user operations
    tab1, tab2, tab3 = st.tabs(["Create User", "View Users", "Manage Users"])

    with tab1:
        st.subheader("Register New User")
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("E-mail", placeholder="Enter e-mail address")
                password = st.text_input("Password", type="password", placeholder="Create a password")
            with col2:
                name = st.text_input("Name", placeholder="Enter user name")
                age = st.number_input("Age", min_value=1, max_value=120, value=25)

            submitted = st.form_submit_button("Create User", type="primary")

            if submitted:
                if email and name:
                    result, success = create_user(email, name, password, age)
                    # print("HEREEEEEEEE", result)
                    if success:
                        # st.success (f"✔️ User created successfully! E-mail: {result.get('email')}")
                        st.success (f"✔️ User {name} created successfully! E-mail: {email}")
                        # time.sleep(2)
                        # st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('detail', 'Unknown error') }")
                else:
                    st.error("❌ Please fill in all fields")

# ============== u2 ============== #

    with tab2:
        st.subheader("View Registered Users")
        users, success = get_all_users()
        #'''
        if success and users:
            # Convert to DataFrame for better display
            df = pd.DataFrame(users)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Display users in a nice table
            st.dataframe(
                df[['oid', 'email', 'name', 'age', 'created_at']],
                width='stretch',
                hide_index=True
            )

            # Show user count
            st.info(f"Total users: {len(users)}")
        else:
            st.error("❌ No users found")

# ============== u3 ============== #

    with tab3:
        st.subheader("Enter a User to Manage")
        users, success = get_all_users()
        # print(users)
        st.html("""
            <style>
            /* Target the 'update' button specifically */
            .st-key-update_btn button {
                background-color: lightblue !important;
                color: black !important;
            }
            /* Target the 'delete' button specifically */
            .st-key-delete_btn button {
                background-color: red !important;
                color: white !important;
            }
            </style>
        """)

        if "edit_user" not in st.session_state:
            st.session_state.edit_user = False
        if "show_dialog" not in st.session_state:
            st.session_state.show_dialog = False

        # 2. Define the Dialog Function
        def edit_profile_menu(username, user_data, entry, user_password, number_of_task):
            @st.dialog(f"{username}'s profile", width="large")
            def show_dialog_view():
                with st.form("update_user_form"):
                    edit_left_col, edit_right_col = st.columns(2)
                    submit_col, cancel_col = st.columns(2)
                    
                    with edit_left_col:
                        if not st.session_state.edit_user:
                            st.write(f"Email: {user_data['email']}")
                            st.write(f"Age: {user_data['age']}")
                            new_email, new_name = user_data['email'], user_data['name']
                        else:
                            new_email = st.text_input("New e-mail", value=user_data['email'])
                            new_age = st.number_input("New age", min_value=0, max_value=120, value=user_data['age'])

                    with edit_right_col:
                        if not st.session_state.edit_user:
                            st.write(f"Username: {username}")
                            st.write(f"Number of task(s): {number_of_task}")
                            new_age = user_data['age']
                        else:
                            new_name = st.text_input("New name", value=user_data['name'])
                            st.write(f"Number of task(s): {number_of_task}")

                    with submit_col:
                        button_label = "Save Changes" if st.session_state.edit_user else "Edit Profile"
                        submitted = st.form_submit_button(button_label, type="secondary", width='stretch')

                    with cancel_col:
                        cancel = st.form_submit_button("Cancel", type="primary", width='stretch')
                    
                    if submitted:
                        if not st.session_state.edit_user:
                            st.session_state.edit_user = True
                            st.rerun() # This reruns the whole script
                        else:
                            result, success = update_user(entry, user_password, new_email, new_name, new_age)
                            if success:
                                st.success("✔️ User updated successfully!")
                                st.session_state.edit_user = False
                                st.session_state.show_dialog = False # Close dialog
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {result.get('detail', 'Unknown error')}")

                    elif cancel:
                        st.session_state.edit_user = False
                        st.session_state.show_dialog = False
                        st.rerun()
            show_dialog_view()

        def delete_profile_menu(email):
            @st.dialog(f"Are you sure you want to delete your profile")
            def show_dialog_delete(email):
                # print(">>>>>>>>>", email)
                with st.form("delete_user_form"):
                    delete_col, cancel_col = st.columns(2)
                    with delete_col:
                        delete = st.form_submit_button("**DELETE PROFILE**", type="primary", width='stretch')
                    with cancel_col:
                        cancel = st.form_submit_button("**Cancel**", type="secondary", width='stretch')
                    if delete:
                        # print("------", email)
                        result, success = delete_user(email)
                        st.write(result, success)
                        st.write("User deleted")
                        st.rerun()
                    elif cancel:
                        st.write("Operation canceled")
                        st.rerun()
            show_dialog_delete(email)

        # 3. UI Logic
        col1, col2, col3 = st.columns([6,2,2], vertical_alignment='center')
        
        with col1:
            entry = st.text_input("E-mail address", placeholder="Enter your email", key="email_input", label_visibility="hidden")
            user_data = get_user(entry)
            task_number = 0
            data, success = get_user_todo(entry, task_number)
            number_of_task = len(data)
            user_password = st.text_input("Password", type="password", key="pw_input", placeholder="Enter your password")

        if isinstance(user_data, dict):
            name = user_data.get('name', 'User')
            with col2:
                if st.button("View Profile", key='update_btn', use_container_width='stretch'):
                    st.session_state.show_dialog = True
            with col3:
                delete_user_btn = st.button("Delete Profile", key='delete_btn', width='stretch')
                if delete_user_btn:
                    delete_profile_menu(entry)
            
            # 4. CRITICAL: Call the dialog if the state says it should be open
            if st.session_state.show_dialog:
                edit_profile_menu(name, user_data, entry, user_password, number_of_task) # PASSWORD to number_of_task as temp 
                

# ============================= TASK PAGE ================================ #

def tasks_page():
    st.header("🗒️ Task Management")

    # Create tabs for different post operations
    tab1, tab2, tab3 = st.tabs(["Create Task", "View Tasks", "Manage Task"])

    with tab1:
        st.subheader("Create New Task for User")
        email_t1 = st.text_input("E-mail", placeholder="Enter e-mail address", key="create_email_input")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="create_pword_input")
        user_data = get_user(email_t1)
        if isinstance(user_data, dict):
            with st.form("create_task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    task_title = st.text_input("Task Title", placeholder="Enter user name")
                    submitted = st.form_submit_button("Submit", type="primary")
                with col2:
                    task_description = st.text_input("Description", placeholder="Enter user name")

            if submitted:
                task_number = len(get_user_todo_list(email_t1)) # THIS MIGHT BE WRONG
                if task_title == "":
                    task_title = F"TASK_{task_number}"
                if task_description == "":
                    task_description = "No description provided"
                # print(task_title=="", task_description==None, task_number)
                result, success = create_task(email_t1, task_title, task_description)
                # print(result, success)
                if success:
                    st.success(f"✔️ Successfully created task for user, {email_t1}. Task #{result['Task #']}")
                    # time.sleep(2)
                    # st.rerun()
                else:
                    st.error(f"❌ Error: Something went wrong")
        elif email_t1 != "" and not isinstance(user_data, dict):
            st.error(f"❌ Error: User not found")
        else:
            st.info("Please enter a registered email to create a task said user")

# ============== t2 ============== #

    with tab2:
        st.subheader("View user's Task(s)")
        col_task_view1, col_task_view2, col_task_view3 = st.columns([6,2,2])
        with col_task_view1:
            email_id = st.text_input("E-mail", placeholder="Enter e-mail address", key="tasks_email_input", label_visibility='collapsed')
        with col_task_view2:
            fetch_view_task = st.button("Fetch task", type="primary", key="tasks_view_get", use_container_width=True)
        with col_task_view3:
            clear_view_task = st.button("Clear DB", type="secondary", key="tasks_view_clear", use_container_width=True)
        task_number = 0
        if fetch_view_task:
            # st.info("⏳ Fetching task(s), please wait ...")
            user_data = get_user(email_id)
            if isinstance(user_data, dict):
                try:
                    data, success = get_user_todo(email_id, task_number)
                    # print(data)
                    # st.info(data)
                    if success == True:
                        st.info(f"User has {len(data)} tasks")
                    df = pd.DataFrame(data)
                    # df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    df = df.rename(columns={'task_number':'Task #', 
                                    'title':'Title',
                                    'status':'Status',
                                    'description':'Description',
                                    'created_at':'Time Created'
                                    }
                    )
                    st.dataframe(
                        df[['Task #', 'Title', 'Status', 'Description', 'Time Created']],
                        width='stretch',
                        hide_index=True
                    )
                except:
                    st.warning("⚠️ User has no task")
            else:
                st.error("❌ User not found")
        elif clear_view_task:
            st.warning("⏳ Clearing shown DB ...")
            time.sleep(2)
            st.rerun()
        st.info("Enter a registered email to view assigned task(s)")

# ============== t3 ============== #

    with tab3:
        if "edit_user_task" not in st.session_state:
            st.session_state.edit_user_task = None
        if "edit_mode_active" not in st.session_state:
            st.session_state.edit_mode_active = False

        def clear_fetch_task():
            st.session_state.current_task_data = None
        def edit_task_menu(email, title, description, status, task_number):
            # print('TESTTTTTTT')
            show_dialog_task(email, title, description, status, task_number)

        st.subheader("Update User's Task")
        col_edit_view1, col_edit_view2 = st.columns([4,6])
        with col_edit_view1:
            email_t3 = st.text_input("E-mail", placeholder="Enter e-mail address", key="edit_email_input", on_change=clear_fetch_task)
            task_number = st.text_input("Task Number", placeholder="Enter task number", on_change=clear_fetch_task)
            fetch_task = st.button("Fetch task", type="primary", key="tasks_edit_get")

        # if email_t3 and task_number and fetch_task:
        if fetch_task:
            if email_t3 and task_number:
                user_data = get_user(email_t3)
                if isinstance(user_data, dict):
                    task_data, success = get_single_task(email_t3, task_number)
                    if success and task_data:
                        st.session_state.edit_user_task = task_data[0]
                    else:
                        st.error("❌ Task not found")
                        st.session_state.edit_user_task = None
                else:
                    st.error("❌ User doesn't exists")
                    st.session_state.edit_user_task = None
            else:
                st.warning("⚠️ Form incomplete")
        # if task_found and current_task:
        if st.session_state.edit_user_task:
            task = st.session_state.edit_user_task
            with col_edit_view2:
                st.info(f"Currently viewing Task #{task_number}")
                col_edit1, col_edit2, col_edit3 = st.columns(3)
                with col_edit1:
                    # task_status = st.selectbox("Task Status", placeholder="--", options=['Incomplete','Complete'])
                    if st.button("Edit task", type="secondary", use_container_width=True):
                        # print("oooooooooooo",task)
                        edit_task_menu(email_t3, task['title'], task['description'], task['status'], task['task_number'])
                with col_edit2:
                    update = st.button("Toggle status", type="secondary", use_container_width=True)
                    if update:
                        update_task_status(email_t3, task['task_number'])
                        st.success(f"✔️ Successfully updated the task status.")
                with col_edit3:
                    if st.button("Delete Task", type="primary", use_container_width=True):
                        # st.info(f"---- {email_t3, task['task_number']} ----")
                        delete_task(email_t3, task['task_number'])
                        st.success(f"✔️ Successfully deleted task #{task['task_number']} for user, {email_t3}.")
                        st.rerun()
            st.divider()
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="edit_pword_input")
            # print("-----",task)
            df_edit = pd.DataFrame([task])
            df_edit = df_edit.rename(columns={'task_number':'Task #', 
                            'title':'Title',
                            'status':'Status',
                            'description':'Description',
                            'created_at':'Time Created'
                            }
            )
            st.dataframe(
                df_edit[['Task #', 'Title', 'Status', 'Description', 'Time Created']],
                width='stretch',
                hide_index=True
            )

# '''
#     with tab2:
#         st.subheader("All Posts")
#         email = st.text_input("E-mail", placeholder="Enter e-mail address")
#         posts, success = get_user_todo_list(email)

#         if success and posts:
#             for post in posts:
#                 with st.expander(f"{post['title']} (ID: {post['id'][:8]} ... )"):
#                     col1, col2 = st.columns([3, 1])
#                     with col1:
#                         st.write(f" ** Content :** {post['content']}")
#                         st.write(f" ** Created :** {pd.to_datetime(post['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
#                     with col2:
#                         st.write(f" ** User ID :** {post['user_id'] [:8]} ... ")
#                         if st.button(f"Delete", key=f"delete_post_{post['id']}", type="secondary") :
#                             result, success = delete_post(post['id'])
#                             if success:
#                                 st.success ("Post deleted!")
#                                 st.rerun()
#                             else:
#                                 st.error("❌ Failed to delete post")

#             st.info(f"Total posts: {len(posts)}")
#         else:
#             st.info("No posts found")

#     with tab3:
#         st.subheader("Posts by User")

#         users, users_success = get_all_users()

#         if users_success and users:
#             user_options = {f"{user['name']} ({user['email' ]})": user['id'] for user in users}
#             selected_user_display = st.selectbox("Select User to view posts", list(user_options.keys()))

#             if selected_user_display:
#                 user_id = user_options[selected_user_display]
#                 posts, success = get_user_posts(user_id)

#                 if success and posts:
#                     st.write(f" ** Posts by {selected_user_display} :** ")
#                     for post in posts:
#                         with st.expander(f"{post['title']}"):
#                             st.write(f" ** Content :** {post['content']}")
#                             st.write(f" ** Created :** {pd.to_datetime(post['created_at']) .strftime('%Y-%m-%d %H:%M:%S') }")
#                 else:
#                     st.info("No posts found for this user")
#'''
                 

# ============================= DASHBOARD PAGE ================================ #

def dashboard_page():
    st.header("Dashboard")
# '''
#     # Get data for dashboard
#     users, users_success = get_all_users()
#     posts, posts_success = get_all_posts()

#     if users_success and posts_success:
#         # Metrics
#         col1, col2, col3, col4 = st.columns(4)

#         with col1:
#             st.metric("Total Users", len(users))
    
#         with col2:
#             st.metric("Total Posts", len(posts))
    
#         with col3:
#             avg_age = sum(user['age'] for user in users) / len(users) if users else 0
#             st.metric("Average Age", f"{avg_age:.1f}")

#         with col4:
#             posts_per_user = len(posts) / len(users) if users else 0
#             st.metric("Posts per User", f"{posts_per_user:.1f}")
        
#         st.markdown("----")

#         # Charts
#         if users:
#             col1, col2 = st.columns(2)

#             with col1:
#                 st.subheader("Age Distribution")
#                 age_data = [user['age'] for user in users]
#                 st.bar_chart(pd.Series(age_data).value_counts().sort_index())

#             with col2:
#                 st.subheader("Recent Activity")
#                 if posts:
#                     # Posts by date
#                     posts_df = pd.DataFrame(posts)
#                     posts_df ['date'] = pd.to_datetime(posts_df['created_at']).dt.date
#                     daily_posts = posts_df.groupby('date').size()
#                     st.line_chart(daily_posts)

#         # Recent posts
#         st.subheader("Recent Posts")
#         if posts:
#             recent_posts = sorted(posts, key=lambda x: x['created_at'], reverse=True) [:5]
#             for post in recent_posts:
#                 st.write(f". ** {post['title']} ** - {pd.to_datetime(post['created_at']).strftime('%Y-%m-%d %H:%M')}")

#     else:
#         st.error("❌ Failed to load dashboard data")
#'''


if __name__ == "__main__":
    main()