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

    def enqueue_operation(func):
        def wrapper(self, *args, **kwargs):
            operation = lambda: func(self, *args, **kwargs)
            self.enqueue(operation)
        return wrapper

    def close(self):
        self.shutdown.set()
        self.commands_ready.set()
        self.ftp_thread.join()
        self.client.close()
        print("Facade closed")
        return True, '', ''

    def handle_commands(self):
        while self.commands_ready.wait():
            if self.shutdown.is_set():
                return
            try:
                func = self.command_queue.get(block=False)
                func()
            except queue.Empty:
                self.commands_ready.clear()
            except Exception as e:
                print(f'An {type(e).__name__} error occurred. Arguments:\n{e.args}')
                self.client.close()


    # Functions passed by GUI, called by handler
    @enqueue_operation
    def login(self, server_ip='127.0.0.1', server_port=21, username='anonymous', password='pass', callback=lambda x: x):
        if self.client.connect_cmd(server_ip, server_port):
            callback(self.client.auth_user(username, password))
    
    @enqueue_operation
    def logout(self, callback=lambda x:x):
        callback(self.client.close())

    @enqueue_operation
    def get_initial_data(self, callback= lambda x:x):
        # Get current directory and list its contents
        pwd_ret, pwd_code, cur_dir = self.client.send_pwd()
        if not pwd_ret:
            callback((pwd_ret, pwd_code, cur_dir))

        list_ret, list_code, list_message, dir_list = self.client.list_dir()
        if not list_ret:
            callback((list_ret, list_code, list_message))
        syst_ret, syst_code, syst_info = self.client.send_syst()
        if not syst_ret:
            callback((syst_ret, syst_code, syst_info))
        callback((True, cur_dir, dir_list, syst_info))

    @enqueue_operation
    def upload_file(self, local_file_path, remote_file_path, mode, callback=lambda x:x):
        callback(self.client.upload_file(local_file_path, remote_file_path, mode))
    
    @enqueue_operation
    def download_file(self, remote_file_path, local_file_path, restart_offset=0, callback=lambda x:x):
        callback(self.client.download_file(remote_file_path, local_file_path, restart_offset))
    
    @enqueue_operation
    def delete_file(self, remote_file_name, callback=lambda x:x):
        callback(self.client.delete_file(remote_file_name))
    
    @enqueue_operation
    def set_remote_dir(self, remote_dir, callback=lambda x:x):
        callback(self.client.set_remote_dir(remote_dir))

    @enqueue_operation
    def make_remote_dir(self, remote_dir, callback=lambda x:x):
        callback(self.client.send_mkd(remote_dir))

    @enqueue_operation
    def delete_remote_dir(self, remote_dir, callback=lambda x:x):
        callback(self.client.send_rmd(remote_dir))
    
    @enqueue_operation
    def set_local_dir(self, local_dir, callback=lambda x:x):
        callback(self.client.set_local_dir(local_dir))

    @enqueue_operation
    def rename_remote_file(self, old_name, new_name, callback=lambda x:x):
        ret, code, message = self.client.send_rnfr(old_name)
        if ret:
            callback(self.client.send_rnto(new_name))
        callback((ret, code, message))
    
