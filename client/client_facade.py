from .ftp_client import FTPClient
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
        self.ftp_thread.start()
    
    def enqueue(self, func):
        self.command_queue.put(func)
        self.commands_ready.set()

    def close(self):
        self.shutdown.set()
        self.commands_ready.set()
        self.ftp_thread.join()
        self.client.close()
        print("Facade closed")

    def handle_commands(self):
        while self.commands_ready.wait():
            if self.shutdown.is_set():
                return
            try:
                func = self.command_queue.get(block=False)
                func()
            except queue.Empty:
                self.commands_ready.clear()

    # Functions passed by GUI, called by handler
    def login(self, server_ip='127.0.0.1', server_port=21, username='anonymous', password='pass', callback=lambda x: x):
        self.client.connect_cmd(server_ip, server_port)
        callback(self.client.auth_user(username, password))
    
    def logout(self, callback=lambda x:x):
        callback(self.client.close())

    def get_initial_data(self, callback= lambda x:x):
        # Get current directory and list its contents
        cur_dir, dir_list, sys_info = '', [], ''
        responses = []
        def push_response(response):
            responses.append(response)
        if self.client.send_pwd(callback=push_response):
            _, _, dir = responses.pop().partition(' ')
            cur_dir = dir

        dir_list = self.client.list_dir()
        if self.client.send_syst(callback=push_response):
            _, _, info = responses.pop().partition(' ')
            sys_info =  info
        callback((cur_dir, dir_list, sys_info))

    def change_dir(self, dir):
        # Change the current directory
        return self.client.change_directory(dir)

    def upload_file(self, local_file_path, remote_file_path, mode, callback=lambda x:x):
        ret = self.client.upload_file(local_file_path, remote_file_path, mode)
        callback(ret)
        return ret
    
    def download_file(self, remote_file_path, local_file_path):
        # Download a file from the server
        return self.client.download_file(remote_file_path, local_file_path)
    
    def delete_file(self, remote_file_name, callback=lambda x:x):
        ret = self.client.delete_file(remote_file_name)
        callback(ret)
        return ret
    
    def set_remote_dir(self, remote_dir, callback=lambda x:x):
        ret = self.client.set_remote_dir(remote_dir)
        callback(ret)
        return ret
    
    def set_local_dir(self, local_dir, callback=lambda x:x):
        ret = self.client.set_local_dir(local_dir)
        callback(ret)
        return ret
