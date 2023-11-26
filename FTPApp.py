from client import FTPClientFacade
from gui import LoginView, MainView
import tkinter as tk

class FTPApp(tk.Tk):
    def __init__(self, ftp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ftp = ftp

        self.title("FTP Application")
        self.geometry("800x600")

        # Initialize the MainView
        self.main_view = MainView(self, self, self.logout)
        self.main_view.pack(fill=tk.BOTH, expand=True)

        # Initialize the Login view
        self.login_view = LoginView(self, self, self.attempt_login, self.on_login_success)
        self.show_login()

    def show_login(self):
        self.login_view.show()

    def on_login_success(self):
        self.login_view.hide()

        # TODO: get data from ftp and os for initial display, pass to mainview

        self.main_view.tkraise()
    
    def attempt_login(self, ip, port, username, password, email, callback):
        try:
            port = int(port)
        except ValueError:
            callback((False, '', 'Port is not an integer'))
            return 
        
        if email:
            self.ftp.login(ip, port, 'anonymous', email, callback)
        else:
            self.ftp.login(ip, port, username, password, callback)

    def logout(self):
        self.ftp.logout()
        self.show_login()

if __name__ == "__main__":
    ftp = FTPClientFacade()  # Initialize your FTPClientFacade
    ftp.run()
    app = FTPApp(ftp)
    app.mainloop()
    ftp.close()