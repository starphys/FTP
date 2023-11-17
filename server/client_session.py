import os
import queue
import threading

class ClientSession:
    def __init__(self, cmd_socket, jail_dir):
        self.cmd_socket = cmd_socket
        self.data_socket = None
        self.data_conn_ready = False
        self.username = None
        self.authenticated = False
        self.jail_dir = os.path.normpath(jail_dir)  # Ensure the path is normalized
        self.current_working_directory = self.jail_dir
        self.encoding_mode = 'A'
        self.restart_offset = 0
        self.rename_from_path = None

        self.command_queue = queue.Queue()
        self.abort_flag = threading.Event()
        self.shutdown_flag = threading.Event()

        self.abort_flag.clear()
        self.shutdown_flag.clear()


    def send_response(self, message):
        if self.cmd_socket:
                self.cmd_socket.sendall(message.encode('ascii'))

    def send_data(self, message):
        if self.data_socket:
            if self.encoding_mode == 'A':
                self.data_socket.sendall(message.encode('ascii'))
            else:
                self.data_socket.sendall(message)

    def receive_data(self, bufsiz):
        if self.data_socket:
            data = self.data_socket.recv(bufsiz)
            if self.encoding_mode == 'A':
                return data.decode('ascii')
            return data
            
    def close(self):
        if self.cmd_socket:
            self.cmd_socket.close()
        if self.data_socket:
            self.close_data()

    def close_data(self):
        if self.data_socket:
            self.data_conn_ready = False
            self.data_socket.close()
            self.data_socket = None

    def change_directory(self, path):
        # Change the current working directory, ensuring it's within the jail directory
        if path in ['\\', '/']:
            # Reset to jail directory
            self.current_working_directory = self.jail_dir
            return True

        # Normalize the path to prevent directory traversal
        normalized_path = os.path.normpath(os.path.join(self.current_working_directory, path))
        
        # Ensure the new path is within the jail directory
        if not os.path.realpath(normalized_path).startswith(os.path.realpath(self.jail_dir)):
            return False

        # Check if the directory exists and is accessible
        if os.path.isdir(normalized_path):
            self.current_working_directory = normalized_path
            return True
        else:
            return False

    def get_relative_path(self):
        # Get the current working directory relative to the jail directory
        if self.current_working_directory == self.jail_dir:
            return '.'  # User is at the top of their jail directory
        else:
            return os.path.relpath(self.current_working_directory, start=self.jail_dir)
    
    def resolve_path(self, user_input, if_exists=True):
        # If the input is an option (e.g., starts with '-'), use the current working directory
        if user_input.startswith('-'):
            return self.current_working_directory
        
        # Attempt to resolve the provided path
        user_path = os.path.normpath(os.path.join(self.current_working_directory, user_input))
        
        # Check if the path is within the jail directory and if it exists
        print(user_path)
        if (os.path.commonprefix([self.jail_dir, user_path]) == self.jail_dir) and (if_exists == os.path.exists(user_path)):
            return user_path
        else:
            return None