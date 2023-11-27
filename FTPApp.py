from client import FTPClientFacade
from gui import LoginView, MainView
import os
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

        self.request_remote_data()
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

    def request_remote_data(self):
        self.ftp.get_initial_data(self.on_remote_data_received)

    def on_remote_data_received(self, data):
        # Successfully got data
        if data[0]:
            self.main_view.remote_path = data[1]
            self.main_view.update_remote_files(data[2])
        # Failed to get data
        else:
            # TODO: handle list error
            pass

    def set_remote_directory(self, directory_name):
        # TODO: handle change dir error
        self.ftp.set_remote_dir(directory_name, lambda result: self.request_remote_data() if result[0] else result)
    
    def set_local_directory(self, directory_name):
        self.ftp.set_local_dir(directory_name)
    
    def delete_local_item(self, current_dir, item_name):
        try:
            os.remove(os.path.join(current_dir, item_name))
            self.main_view.display_local_files()
        except OSError as e:
            print(e)
            # TODO: handle failure here, this will come up a lot

    def delete_remote_directory(self, item_name):
        self.ftp.delete_remote_dir(item_name, lambda result: self.request_remote_data() if result[0] else result)
        # TODO: handle failure

    def delete_remote_file(self, item_name):
        self.ftp.delete_file(item_name, lambda result: self.request_remote_data() if result[0] else result)
        # TODO: handle failure
    
    def rename_local_file(self, local_path, old_name, new_name):
        old_path = os.path.join(local_path, old_name)
        new_path = os.path.join(local_path, new_name)
        try:
            os.rename(old_path, new_path)
            self.main_view.display_local_files()
        except OSError as e:
            print(e)
            # TODO: handle failure here, this will come up a lot
    
    def rename_remote_file(self, old_name, new_name):
        self.ftp.rename_remote_file(old_name, new_name, lambda result: self.request_remote_data() if result[0] else result)

    def create_local_directory(self, local_path, dir_name):
        new_dir_path = os.path.join(local_path, dir_name)
        try:
            os.makedirs(new_dir_path, exist_ok=True)
            self.main_view.display_local_files()
        except OSError as e:
            print(e)
            # TODO: handle failure here, this will come up a lot

    def create_remote_directory(self, dir_name):
        self.ftp.make_remote_dir(dir_name, lambda result: self.request_remote_data() if result[0] else result)
        # TODO: handle failure here, this will come up a lot

    def upload_file(self, file_path, destination_name, action):
        if action == 'overwrite':
            self.ftp.upload_file(file_path, destination_name, 'w', lambda result: self.request_remote_data() if result[0] else result)
        else:
            self.ftp.upload_file(file_path, destination_name, 'a', lambda result: self.request_remote_data() if result[0] else result)

    def download_file(self, file_path, destination_name):
        self.ftp.download_file(file_path, destination_name, callback=lambda result: self.main_view.display_local_files() if result[0] else result)


if __name__ == "__main__":
    ftp = FTPClientFacade()  # Initialize your FTPClientFacade
    ftp.run()
    app = FTPApp(ftp)
    app.mainloop()
    ftp.close()