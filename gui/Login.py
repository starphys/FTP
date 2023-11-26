import tkinter as tk
from tkinter import messagebox, filedialog

class LoginView(tk.Frame):
    def __init__(self, parent, controller, on_attempt, on_success):
        super().__init__(parent, borderwidth=2, relief="groove")
        self.controller = controller
        self.on_attempt = on_attempt
        self.on_success = on_success

        # Project label
        project_label = tk.Label(self, text="FTP by Team 9", font=('Arial 24 bold italic'), fg="purple")
        project_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Port label and entry
        port_label = tk.Label(self, text="Port number:")
        port_label.place(relx=0.2, rely=0.2, anchor="center")

        self.port_entry = tk.Entry(self, width=20)
        self.port_entry.place(relx=0.3, rely=0.2, anchor="w")
        
        # Host label and entry
        host_label = tk.Label(self, text="Hostname:")
        host_label.place(relx=0.2, rely=0.3, anchor="center")

        self.host_entry = tk.Entry(self, width=45)
        self.host_entry.place(relx=0.3, rely=0.3, anchor="w")
        
        # Username label and entry
        username_label = tk.Label(self, text="Username:")
        username_label.place(relx=0.2, rely=0.4, anchor="center")

        self.username_entry = tk.Entry(self, width=45)
        self.username_entry.place(relx=0.3, rely=0.4, anchor="w")

        # Password label and entry
        password_label = tk.Label(self, text="Password:")
        password_label.place(relx=0.2, rely=0.5, anchor="center")

        self.password_entry = tk.Entry(self, show="*", width=45)
        self.password_entry.place(relx=0.3, rely=0.5, anchor="w")

        # Email label and entry
        email_label = tk.Label(self, text="Email:")
        email_label.place(relx=0.2, rely=0.6, anchor="center")

        self.email_entry = tk.Entry(self, width=45)
        self.email_entry.place(relx=0.3, rely=0.6, anchor="w")

        # Login button
        login_button = tk.Button(self, text="Login", command=self.login, width=10, height=1)
        login_button.place(relx=0.5, rely=0.7, anchor="center")

        # Check button for anonymous sign-in
        self.sign_in_anonymously_var = tk.BooleanVar()
        sign_in_anonymously_checkbox = tk.Checkbutton(self, text="Sign in Anonymously", variable=self.sign_in_anonymously_var, font=("Arial, 10"), command=self.toggle_user_fields)
        sign_in_anonymously_checkbox.place(relx=0.5, rely=0.8, anchor="center")

        # Initially disable the Email fields
        self.toggle_user_fields()
    
    def show(self):
        self.place(relx=0.5, rely=0.5, anchor="center", height=450, width=500)
        self.tkraise()
        self.grab_set()

    def hide(self):
        self.place_forget()
        self.grab_release() 

    def login(self):
        portnumber = self.port_entry.get()
        hostname = self.host_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        self.on_attempt(hostname, portnumber, username, password, email, self.login_result)

    def login_result(self, response):
        result, code, message = response
        if result:
            self.on_success()
        else:
            # TODO: show error
            pass

    def toggle_user_fields(self):
        is_anonymous = self.sign_in_anonymously_var.get()

        # Clear the contents of the fields when the checkbox state changes
        if is_anonymous:
            # Clear Username and Password fields if signing in anonymously
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            # Clear Email field if not signing in anonymously
            self.email_entry.delete(0, tk.END)

        # Toggle the state of Username, Password, and Email fields based on checkbox state
        self.username_entry.config(state=tk.NORMAL if not is_anonymous else tk.DISABLED)
        self.password_entry.config(state=tk.NORMAL if not is_anonymous else tk.DISABLED)
        self.email_entry.config(state=tk.NORMAL if is_anonymous else tk.DISABLED)