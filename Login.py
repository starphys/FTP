import tkinter as tk
from tkinter import messagebox

class Login:
    def __init__(self, root):
        self.root = root
        root.title("Login Page")
        # Set the window size
        window_width = 500
        window_height = 500
        root.geometry(f"{window_width}x{window_height}")

        # Create and place the project label and entry
        project_label = tk.Label(root, text="FTP by Team 9", font=('Arial 24 bold italic'), fg="purple")
        project_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Create and place the port label and entry
        port_label = tk.Label(root, text="Port number:")
        port_label.place(relx=0.2, rely=0.2, anchor="center")

        self.port_entry = tk.Entry(root, width=20)
        self.port_entry.place(relx=0.3, rely=0.2, anchor="w")
        
        # Create and place the host label and entry
        host_label = tk.Label(root, text="Hostname:")
        host_label.place(relx=0.2, rely=0.3, anchor="center")

        self.host_entry = tk.Entry(root, width=45)
        self.host_entry.place(relx=0.3, rely=0.3, anchor="w")
        
        # Create and place the username label and entry
        username_label = tk.Label(root, text="Username:")
        username_label.place(relx=0.2, rely=0.4, anchor="center")

        self.username_entry = tk.Entry(root, width=45)
        self.username_entry.place(relx=0.3, rely=0.4, anchor="w")

        # Create and place the password label and entry
        password_label = tk.Label(root, text="Password:")
        password_label.place(relx=0.2, rely=0.5, anchor="center")

        self.password_entry = tk.Entry(root, show="*", width=45)
        self.password_entry.place(relx=0.3, rely=0.5, anchor="w")

        # Create and place the email label and entry
        email_label = tk.Label(root, text="Email:")
        email_label.place(relx=0.2, rely=0.6, anchor="center")

        self.email_entry = tk.Entry(root, width=45)
        self.email_entry.place(relx=0.3, rely=0.6, anchor="w")

        # Create and place the login button
        login_button = tk.Button(root, text="Login", command=self.login, width=10, height=1)
        login_button.place(relx=0.5, rely=0.7, anchor="center")

        # Create and place the check button for signing in anonymously
        self.sign_in_anonymously_var = tk.BooleanVar()
        sign_in_anonymously_checkbox = tk.Checkbutton(root, padx=10, text="Sign in Anonymously", variable=self.sign_in_anonymously_var, font=("Arial, 10"), command=self.toggle_user_fields)
        sign_in_anonymously_checkbox.place(relx=0.5, rely=0.8, anchor="center")

        # Initially disable the Email fields
        self.toggle_user_fields()

    def login(self):
        portnumber = self.port_entry.get()
        hostname = self.host_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        if self.sign_in_anonymously_var.get():
            # Login anonymously
            messagebox.showinfo("Login", "Login successful (Anonymously)")
        elif username == "admin" and password == "password" and portnumber == "148" and hostname == "NASA":
            messagebox.showinfo("Login", "Login successful")
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    def toggle_user_fields(self):
        # Toggle the state of Username and Password fields based on checkbox state
        username_state = tk.NORMAL if not self.sign_in_anonymously_var.get() else tk.DISABLED
        password_state = tk.NORMAL if not self.sign_in_anonymously_var.get() else tk.DISABLED
        email_state = tk.NORMAL if self.sign_in_anonymously_var.get() else tk.DISABLED
        
        self.username_entry.config(state=username_state)
        self.password_entry.config(state=password_state)
        self.email_entry.config(state=email_state)

if __name__ == "__main__":
    root = tk.Tk()
    login_app = Login(root)
    root.mainloop()
