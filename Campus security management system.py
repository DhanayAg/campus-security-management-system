import tkinter as tk
from tkinter import messagebox, ttk
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

# Database connection
def connect_to_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME") 
    )
    return conn

# Function Definitions
def login():
    username = username_entry.get()
    password = password_entry.get()

    conn = connect_to_db()
    cursor = conn.cursor()

    # Query to validate login credentials and fetch role + StudentID if student
    cursor.execute("SELECT Role, UserID FROM Users WHERE Email = %s AND Password = %s", (username, password))
    result = cursor.fetchone()

    conn.close()

    if result:
        role, user_id = result
        messagebox.showinfo("Login Successful", f"Welcome, {role}!")
        root.destroy()
        main_dashboard(role, user_id if role == "Student" else None)  # Pass StudentID for students
    else:
        messagebox.showerror("Login Failed", "Invalid credentials!")

def register_visitor():
    visitor_name = visitor_name_entry.get()
    visitor_contact = visitor_contact_entry.get()
    visit_purpose = visit_purpose_entry.get()

    if visitor_name and visit_purpose:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Insert visitor data into the Visitors table
        cursor.execute(
            "INSERT INTO Visitors (Name, Contact, Purpose, TimeIn) VALUES (%s, %s, %s, NOW())",
            (visitor_name, visitor_contact, visit_purpose)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Visitor {visitor_name} registered!")
    else:
        messagebox.showerror("Error", "All fields are required!")

def report_incident():
    incident_desc = incident_description_entry.get("1.0", tk.END).strip()

    if incident_desc:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Insert incident report into the Incidents table
        cursor.execute(
            "INSERT INTO Incidents (Description, ReportedBy, TimeReported) VALUES (%s, 1, NOW())",  # Assuming '1' as the user ID for simplicity
            (incident_desc,)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Incident Reported", "Thank you for reporting.")
    else:
        messagebox.showerror("Error", "Please enter a description.")

def view_logs():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch visitor logs from the Visitors table
    cursor.execute("SELECT Name, Contact, Purpose, TimeIn, TimeOut FROM Visitors")
    rows = cursor.fetchall()

    conn.close()

    # Display logs in a new window
    logs_window = tk.Toplevel()
    logs_window.title("Visitor Logs")
    logs_window.geometry("600x400")

    tree = ttk.Treeview(logs_window, columns=("Name", "Contact", "Purpose", "TimeIn", "TimeOut"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Contact", text="Contact")
    tree.heading("Purpose", text="Purpose")
    tree.heading("TimeIn", text="Time In")
    tree.heading("TimeOut", text="Time Out")
    tree.pack(fill=tk.BOTH, expand=True)

    # Insert rows into Treeview
    for row in rows:
        tree.insert("", tk.END, values=row)

# Login Screen
def register_user():
    name = reg_name_entry.get()
    role = reg_role_combobox.get()
    contact = reg_contact_entry.get()
    email = reg_email_entry.get()
    password = reg_password_entry.get()

    if name and role and email and password:
        conn = connect_to_db()
        cursor = conn.cursor()

        try:
            # Insert new user data into the Users table
            cursor.execute(
                "INSERT INTO Users (Name, Role, Contact, Email, Password) VALUES (%s, %s, %s, %s, %s)",
                (name, role, contact, email, password)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"User {name} registered successfully!")
            registration_window.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showerror("Error", "All fields are required!")

def open_registration_window():
    global reg_name_entry, reg_role_combobox, reg_contact_entry, reg_email_entry, reg_password_entry

    # Create a new window for registration
    global registration_window
    registration_window = tk.Toplevel()
    registration_window.title("New User Registration")
    registration_window.geometry("400x400")

    tk.Label(registration_window, text="Register New User", font=("Arial", 14)).pack(pady=10)

    tk.Label(registration_window, text="Name").pack()
    reg_name_entry = tk.Entry(registration_window, width=30)
    reg_name_entry.pack(pady=5)

    tk.Label(registration_window, text="Role").pack()
    reg_role_combobox = ttk.Combobox(registration_window, values=["Admin", "Security", "Student", "Other"])
    reg_role_combobox.pack(pady=5)

    tk.Label(registration_window, text="Contact").pack()
    reg_contact_entry = tk.Entry(registration_window, width=30)
    reg_contact_entry.pack(pady=5)

    tk.Label(registration_window, text="Email").pack()
    reg_email_entry = tk.Entry(registration_window, width=30)
    reg_email_entry.pack(pady=5)

    tk.Label(registration_window, text="Password").pack()
    reg_password_entry = tk.Entry(registration_window, width=30, show="*")
    reg_password_entry.pack(pady=5)

    tk.Button(registration_window, text="Register", command=register_user).pack(pady=20)

# Update the login_screen function to include a Register button
def login_screen():
    global username_entry, password_entry
    root.title("Campus Security System - Login")
    tk.Label(root, text="Login", font=("Arial", 18)).pack(pady=10)
    tk.Label(root, text="Username (Email)").pack()
    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)
    tk.Label(root, text="Password").pack()
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack(pady=5)
    tk.Button(root, text="Login", command=login).pack(pady=10)

    # Add a new button for registration
    tk.Button(root, text="New User? Register Here", command=open_registration_window).pack(pady=5)

def register_student():
    student_id = student_id_entry.get()
    student_name = student_name_entry.get()
    student_contact = student_contact_entry.get()
    visit_purpose = student_purpose_entry.get()

    if student_id and student_name and visit_purpose:
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            # Insert student data into the Students table
            cursor.execute(
                """
                INSERT INTO Students (StudentID, Name, Contact, Purpose, TimeIn)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (student_id, student_name, student_contact, visit_purpose)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Student {student_name} registered!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
    else:
        messagebox.showerror("Error", "All fields are required!")

def student_registration():
    global student_id_entry, student_name_entry, student_contact_entry, student_purpose_entry
    student_window = tk.Toplevel()
    student_window.title("Student Registration")
    student_window.geometry("400x350")

    tk.Label(student_window, text="Student Registration", font=("Arial", 14)).pack(pady=10)
    tk.Label(student_window, text="Student ID").pack()
    student_id_entry = tk.Entry(student_window, width=30)
    student_id_entry.pack(pady=5)
    tk.Label(student_window, text="Name").pack()
    student_name_entry = tk.Entry(student_window, width=30)
    student_name_entry.pack(pady=5)
    tk.Label(student_window, text="Contact").pack()
    student_contact_entry = tk.Entry(student_window, width=30)
    student_contact_entry.pack(pady=5)
    tk.Label(student_window, text="Purpose of Visit").pack()
    student_purpose_entry = tk.Entry(student_window, width=30)
    student_purpose_entry.pack(pady=5)
    tk.Button(student_window, text="Register", command=register_student).pack(pady=10)
  
# Visitor Registration Screen
def visitor_registration():
    global visitor_name_entry, visitor_contact_entry, visit_purpose_entry
    visitor_window = tk.Toplevel()
    visitor_window.title("Visitor Registration")
    visitor_window.geometry("400x300")

    tk.Label(visitor_window, text="Visitor Registration", font=("Arial", 14)).pack(pady=10)
    tk.Label(visitor_window, text="Name").pack()
    visitor_name_entry = tk.Entry(visitor_window, width=30)
    visitor_name_entry.pack(pady=5)
    tk.Label(visitor_window, text="Contact").pack()
    visitor_contact_entry = tk.Entry(visitor_window, width=30)
    visitor_contact_entry.pack(pady=5)
    tk.Label(visitor_window, text="Purpose of Visit").pack()
    visit_purpose_entry = tk.Entry(visitor_window, width=30)
    visit_purpose_entry.pack(pady=5)
    tk.Button(visitor_window, text="Register", command=register_visitor).pack(pady=10)

# Incident Reporting Screen
def incident_reporting():
    global incident_description_entry
    incident_window = tk.Toplevel()
    incident_window.title("Report Incident")
    incident_window.geometry("400x300")

    tk.Label(incident_window, text="Report Incident", font=("Arial", 14)).pack(pady=10)
    tk.Label(incident_window, text="Description").pack()
    incident_description_entry = tk.Text(incident_window, height=8, width=40)
    incident_description_entry.pack(pady=5)
    tk.Button(incident_window, text="Submit", command=report_incident).pack(pady=10)

#view student record
def view_student_record(student_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch student record using the StudentID
    query = """
        SELECT StudentID, Name, Contact, Purpose, TimeIn, TimeOut
        FROM Students
        WHERE StudentID = %s
    """
    cursor.execute(query, (student_id,))
    record = cursor.fetchone()

    conn.close()

    # Display the record in a new window
    if record:
        record_window = tk.Toplevel()
        record_window.title("My Record")
        record_window.geometry("400x300")

        tk.Label(record_window, text="Your Record", font=("Arial", 14)).pack(pady=10)
        labels = ["Student ID", "Name", "Contact", "Purpose", "Time In", "Time Out"]
        for i, value in enumerate(record):
            tk.Label(record_window, text=f"{labels[i]}: {value}", font=("Arial", 12)).pack(pady=5)
    else:
        messagebox.showerror("No Record Found", "No records found for your account!")


# Function to Update Visitor TimeOut
def update_visitor_timeout():
    visitor_id = visitor_id_entry.get()

    if visitor_id:
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            # Update the TimeOut field for the visitor
            query = "UPDATE Visitors SET TimeOut = NOW() WHERE VisitorID = %s"
            cursor.execute(query, (visitor_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Visitor's TimeOut updated successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error updating TimeOut: {err}")
    else:
        messagebox.showerror("Error", "Visitor ID is required!")

# Function to Update Student TimeIn
def update_student_timein():
    student_id = student_id_entry.get()

    if student_id:
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            # Update the TimeIn field for the student
            query = "UPDATE Students SET TimeIn = NOW() WHERE StudentID = %s"
            cursor.execute(query, (student_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Student's TimeIn updated successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error updating TimeIn: {err}")
    else:
        messagebox.showerror("Error", "Student ID is required!")


# Update Visitor TimeOut Window
def update_visitor_timeout_window():
    global visitor_id_entry
    timeout_window = tk.Toplevel()
    timeout_window.title("Update Visitor TimeOut")
    timeout_window.geometry("400x200")

    tk.Label(timeout_window, text="Enter Visitor ID to Update TimeOut", font=("Arial", 14)).pack(pady=10)
    tk.Label(timeout_window, text="Visitor ID").pack()
    visitor_id_entry = tk.Entry(timeout_window, width=30)
    visitor_id_entry.pack(pady=5)
    tk.Button(timeout_window, text="Update TimeOut", command=update_visitor_timeout).pack(pady=10)

# Update Student TimeIn Window
def update_student_timein_window():
    global student_id_entry
    timein_window = tk.Toplevel()
    timein_window.title("Update Student TimeIn")
    timein_window.geometry("400x200")

    tk.Label(timein_window, text="Enter Student ID to Update TimeIn", font=("Arial", 14)).pack(pady=10)
    tk.Label(timein_window, text="Student ID").pack()
    student_id_entry = tk.Entry(timein_window, width=30)
    student_id_entry.pack(pady=5)
    tk.Button(timein_window, text="Update TimeIn", command=update_student_timein).pack(pady=10)

def view_student_logs():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch student logs from the Students table
    cursor.execute("SELECT Name, Contact, Purpose, TimeIn, TimeOut FROM Students")
    rows = cursor.fetchall()

    conn.close()

    # Display student logs in a new window
    logs_window = tk.Toplevel()
    logs_window.title("Student Logs")
    logs_window.geometry("600x400")

    tree = ttk.Treeview(logs_window, columns=("Name", "Contact", "Purpose", "TimeIn", "TimeOut"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Contact", text="Contact")
    tree.heading("Purpose", text="Purpose")
    tree.heading("TimeIn", text="Time In")
    tree.heading("TimeOut", text="Time Out")
    tree.pack(fill=tk.BOTH, expand=True)

    # Insert rows into Treeview for student logs
    for row in rows:
        tree.insert("", tk.END, values=row)

#Main Dashboard for Security and Admin
def main_dashboard(role, user_id=None):
    dashboard = tk.Tk()
    dashboard.title("Campus Security System - Dashboard")
    dashboard.geometry("500x400")

    tk.Label(dashboard, text=f"{role} Dashboard", font=("Arial", 18)).pack(pady=10)

    if role == "Admin":
        # Create Visitors and Students options
        visitors_button = tk.Button(dashboard, text="Visitors", command=lambda: open_visitors_options(dashboard), width=20)
        students_button = tk.Button(dashboard, text="Students", command=lambda: open_students_options(dashboard), width=20)
        tk.Button(dashboard, text="View Incidents", command=view_incidents, width=20).pack(pady=10)
        tk.Button(dashboard, text="View Users", command=view_users, width=20).pack(pady=10)
        tk.Button(dashboard, text="View Access Points", command=view_access_points, width=20).pack(pady=10)
        visitors_button.pack(pady=10)
        students_button.pack(pady=10)


    elif role == "Security":
        # Create Visitors and Students options
        visitors_button = tk.Button(dashboard, text="Visitors", command=lambda: open_visitors_options(dashboard), width=20)
        students_button = tk.Button(dashboard, text="Students", command=lambda: open_students_options(dashboard), width=20)
        visitors_button.pack(pady=10)
        students_button.pack(pady=10)

        # Incident reporting
        tk.Button(dashboard, text="Report Incident", command=incident_reporting, width=20).pack(pady=10)

    elif role == "Student":
        # Only view student's own record
        tk.Button(dashboard, text="View My Record", command=lambda: view_student_record(user_id), width=20).pack(pady=10)

    # Exit button
    tk.Button(dashboard, text="Exit", command=dashboard.destroy, width=20).pack(pady=10)

# Function to open the Visitors options (Insert, Update, View)
def open_visitors_options(dashboard):
    options_window = tk.Toplevel(dashboard)
    options_window.title("Visitors Options")
    options_window.geometry("400x300")

    tk.Label(options_window, text="Visitors Options", font=("Arial", 14)).pack(pady=10)

    tk.Button(options_window, text="Register Visitor", command=visitor_registration, width=20).pack(pady=10)
    tk.Button(options_window, text="Update Visitor TimeOut", command=update_visitor_timeout_window, width=20).pack(pady=10)
    tk.Button(options_window, text="View Visitor Logs", command=view_logs, width=20).pack(pady=10)
    tk.Button(options_window, text="Delete Visitor", command=delete_visitor, width=20).pack(pady=10)

# Function to open the Students options (Insert, Update, View)
def open_students_options(dashboard):
    options_window = tk.Toplevel(dashboard)
    options_window.title("Students Options")
    options_window.geometry("400x300")

    tk.Label(options_window, text="Students Options", font=("Arial", 14)).pack(pady=10)

    tk.Button(options_window, text="Register Student", command=student_registration, width=20).pack(pady=10)
    tk.Button(options_window, text="Update Student TimeIn", command=update_student_timein_window, width=20).pack(pady=10)
    tk.Button(options_window, text="View Student Logs", command=view_student_logs, width=20).pack(pady=10)
    tk.Button(options_window, text="Delete Student", command=delete_student, width=20).pack(pady=10)

def view_incidents():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch incidents along with the reporter's name from the Users table
    cursor.execute("""
        SELECT IncidentID, Description, ReportedBy, TimeReported, Status
        FROM Incidents
        JOIN Users ON Incidents.ReportedBy = Users.UserID
        ORDER BY TimeReported DESC
    """)
    incidents = cursor.fetchall()

    conn.close()

    # Display incidents in a new window
    incidents_window = tk.Toplevel()
    incidents_window.title("Incident Reports")
    incidents_window.geometry("600x400")

    tree = ttk.Treeview(incidents_window, columns=("IncidentID", "Description", "ReportedBy", "TimeReported", "Status"), show="headings")
    tree.heading("IncidentID", text="Incident ID")
    tree.heading("Description", text="Description")
    tree.heading("ReportedBy", text="Reported By")
    tree.heading("TimeReported", text="Time Reported")
    tree.heading("Status", text="Status")
    tree.pack(fill=tk.BOTH, expand=True)

    # Insert incident rows into Treeview
    for incident in incidents:
        tree.insert("", tk.END, values=incident)

def view_users():
    # Create a new window to display users
    users_window = tk.Toplevel()
    users_window.title("View Users")
    users_window.geometry("600x400")

    # Label for role filter
    tk.Label(users_window, text="Select Role to Filter Users", font=("Arial", 14)).pack(pady=10)

    # Dropdown to select the role
    role_combobox = ttk.Combobox(users_window, values=["All", "Admin", "Security", "Student", "Other"])
    role_combobox.set("All")  # Default value
    role_combobox.pack(pady=10)

    # Button to fetch users based on selected role
    def fetch_users():
        selected_role = role_combobox.get()
        fetch_and_display_users(selected_role, users_window)

    tk.Button(users_window, text="View Users", command=fetch_users).pack(pady=10)

def fetch_and_display_users(selected_role, users_window):
    # Connect to the database
    conn = connect_to_db()
    cursor = conn.cursor()

    # Modify the query to filter by role, or show all users if "All" is selected
    if selected_role == "All":
        query = "SELECT UserID, Name, Role, Contact, Email FROM Users"
    else:
        query = "SELECT UserID, Name, Role, Contact, Email FROM Users WHERE Role = %s"

    cursor.execute(query, (selected_role,) if selected_role != "All" else ())
    rows = cursor.fetchall()

    conn.close()

    # Clear previous Treeview if it exists
    for widget in users_window.winfo_children():
        if isinstance(widget, ttk.Treeview):
            widget.destroy()

    # Create Treeview to display the users
    tree = ttk.Treeview(users_window, columns=("UserID", "Name", "Role", "Contact", "Email"), show="headings")
    tree.heading("UserID", text="UserID")
    tree.heading("Name", text="Name")
    tree.heading("Role", text="Role")
    tree.heading("Contact", text="Contact")
    tree.heading("Email", text="Email")
    tree.pack(fill=tk.BOTH, expand=True)

    # Insert fetched rows into the Treeview
    for row in rows:
        tree.insert("", tk.END, values=row)

# Function to view access points for Admin
def view_access_points():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch access points from the AccessPoints table
    cursor.execute("""
        SELECT AccessPointID, LocationName, Description, 
               (SELECT Name FROM Users WHERE UserID = SecurityGuardID) AS SecurityGuard
        FROM AccessPoints
    """)
    rows = cursor.fetchall()

    conn.close()

    # Create a new window to display access points
    access_window = tk.Toplevel()
    access_window.title("Access Points")
    access_window.geometry("600x400")

    tree = ttk.Treeview(access_window, columns=("ID", "Location", "Description", "SecurityGuard"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Location", text="Location")
    tree.heading("Description", text="Description")
    tree.heading("SecurityGuard", text="Security Guard")
    tree.pack(fill=tk.BOTH, expand=True)

    # Insert rows into the Treeview widget
    for row in rows:
        tree.insert("", tk.END, values=row)

def delete_visitor():
    def confirm_deletion(visitor_id):
        # Confirm deletion with the user
        result = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete Visitor ID {visitor_id}?")
        if result:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Visitors WHERE VisitorID = %s", (visitor_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Visitor record deleted successfully.")
            view_visitors()  # Refresh the visitor list window

    # Create a window to select the visitor to delete
    delete_window = tk.Toplevel()
    delete_window.title("Delete Visitor")
    delete_window.geometry("400x300")

    tk.Label(delete_window, text="Enter Visitor ID to delete:").pack(pady=10)
    visitor_id_entry = tk.Entry(delete_window)
    visitor_id_entry.pack(pady=10)
    
    # Function to delete the selected visitor
    def delete_selected():
        visitor_id = visitor_id_entry.get()
        if visitor_id.isdigit():
            confirm_deletion(int(visitor_id))
        else:
            messagebox.showwarning("Invalid ID", "Please enter a valid Visitor ID.")
    
    tk.Button(delete_window, text="Delete Visitor", command=delete_selected).pack(pady=10)
    tk.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=10)

def delete_student():
    def confirm_deletion(student_id):
        # Confirm deletion with the user
        result = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete Student ID {student_id}?")
        if result:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Students WHERE StudentID = %s", (student_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Student record deleted successfully.")
            view_students()  # Refresh the student list window

    # Create a window to select the student to delete
    delete_window = tk.Toplevel()
    delete_window.title("Delete Student")
    delete_window.geometry("400x300")

    tk.Label(delete_window, text="Enter Student ID to delete:").pack(pady=10)
    student_id_entry = tk.Entry(delete_window)
    student_id_entry.pack(pady=10)
    
    # Function to delete the selected student
    def delete_selected():
        student_id = student_id_entry.get()
        if student_id.isdigit():
            confirm_deletion(int(student_id))
        else:
            messagebox.showwarning("Invalid ID", "Please enter a valid Student ID.")
    
    tk.Button(delete_window, text="Delete Student", command=delete_selected).pack(pady=10)
    tk.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=10)
        
# Initialize Tkinter
root = tk.Tk()
root.geometry("400x300")
login_screen()
root.mainloop()
