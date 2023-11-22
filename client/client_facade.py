from client import FTPClient
import threading
import queue

BUFSIZ = 4096

# Facade manages a command queue and a command processing thread. Calls to facade functions push 
# functions to the queue, and they are processed in order by the processing thread.
# Nothing is returned from the facade, instead all feedback is passed through callback functions
class FTPClientFacade:
    # Functions called by GUI
    def __init__(self):
        self.command_queue = queue.Queue()
        self.commands_ready = threading.Event()
        self.shutdown = threading.Event()
        self.client = FTPClient(BUFSIZ)
        self.ftp_thread = threading.Thread(target=self.handle_commands)
    
    def run(self):
        self.ftp_thread.run()
    
    def enqueue(self, func):
        self.command_queue.put(func)
        self.commands_ready.set()

    def close(self):
        self.shutdown.set()
        self.commands_ready.set()
        self.ftp_thread.join()
        self.client.close()

    def handle_commands(self):
        while self.commands_ready.wait():
            if self.shutdown.is_set():
                return
            try:
                func = self.command_queue.get(timeout=1)
                func()
            except queue.Empty:
                self.commands_ready.clear()

    # Functions passed by GUI, called by handler
    def login(self, server_ip='127.0.0.1', server_port=21, username='anonymous', password='pass', callback=lambda x: x):
        self.client.connect_cmd(server_ip, server_port)
        callback(self.client.auth_user(username, password))
    
    def logout(self, callback=lambda x:x):
        callback(self.client.close())

    def get_initial_data(self):
        # Get current directory and list its contents
        current_dir = self.client.get_current_directory()
        directory_list = self.client.list_directory()
        system_info = self.client.get_system_info()
        return current_dir, directory_list, system_info

    def change_dir(self, dir):
        # Change the current directory
        return self.client.change_directory(dir)

    def upload_file(self, local_file_path, remote_file_path):
        # Upload a file to the server
        return self.client.upload_file(local_file_path, remote_file_path)
    
    def download_file(self, remote_file_path, local_file_path):
        # Download a file from the server
        return self.client.download_file(remote_file_path, local_file_path)
    

