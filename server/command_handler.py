import os
import platform
import socket
from utils import format_file_stat

class FTPCommandHandler:
    def __init__(self, client_session, server):
        self.client_session = client_session
        self.server = server

    def handle_user(self, username):
        if username == '':
            response = '501 Syntax error in parameters or arguments.\r\n'
        elif username in self.server.credentials:
            self.client_session.username = username
            response = '331 User name okay, need password.\r\n'
        else:
            response = '530 Not logged in.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_pass(self, password):
        if self.client_session.username and \
           self.server.credentials.get(self.client_session.username) == password:
            self.client_session.authenticated = True
            response = '230 User logged in, proceed.\r\n'
        else:
            response = '530 Not logged in.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_quit(self, arg):
        response = '221 Service closing control connection.\r\n'
        self.client_session.send_response(response)
        return False
    
    def handle_pwd(self, arg):
        response = f'257 {self.client_session.get_relative_path()}\r\n'
        self.client_session.send_response(response)
        return True

    def handle_syst(self, arg):
        response = f'215 {platform.system()} {platform.release()}\r\n'
        self.client_session.send_response(response)
        return True

    def handle_type(self, arg):
        if arg.upper() == 'A':
            self.client_session.encoding_mode = 'A'
            response = '200 Switching to ASCII mode.\r\n'
        elif arg.upper() == 'I':
            self.client_session.encoding_mode = 'I'
            response = '200 Switching to binary mode.\r\n'
        else:
            response = '504	Command not implemented for that parameter.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_pasv(self, arg):
        if self.client_session.data_socket is not None:
            self.client_session.data_socket.close()
            self.client_session.data_socket = None
            self.client_session.data_conn_ready = False
        # Setup socket on any available port
        pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pasv_socket.bind(('127.0.0.1', 0))
        pasv_socket.listen(1)
        
        ip, port = pasv_socket.getsockname()
        h1, h2, h3, h4 = ip.split('.')
        p1, p2 = port >> 8, port & 0xff
        self.client_session.send_response(f'227 Entering Passive Mode ({h1},{h2},{h3},{h4},{p1},{p2})\r\n')

        try:
            # Wait for the client to establish a data connection
            self.client_session.data_socket, _ = pasv_socket.accept()
            self.client_session.data_conn_ready = True
        except socket.timeout:
            self.client_session.send_response('421 No connection was established within the timeout period.\r\n')
        finally:
            pasv_socket.close()
        return True

    def handle_list(self, arg):
        list_dir = self.client_session.resolve_path(arg)
        if not list_dir:
            self.client_session.send_response('550	Requested action not taken. File unavailable.\r\n')
        self.client_session.send_response('150	File status okay; about to open data connection.\r\n')

        try:
            files = os.listdir(list_dir) + [".", ".."]
            print(files)
            return_data = [format_file_stat(list_dir, file) for file in files]
            response = '\r\n'.join(return_data) + '\r\n'
            print(response)
            self.client_session.send_data(response)
            self.client_session.send_response('226	Closing data connection. Requested file action successful.\r\n')
        except Exception as e:
            print(e)
            self.client_session.send_response('550	Requested action not taken. File unavailable.\r\n')
        
        self.client_session.close_data()
        return True
    
    def handle_cwd(self, arg):
        if self.client_session.change_directory(arg):
            self.client_session.send_response('250 Directory successfully changed.\r\n')
        else:
            self.client_session.send_response('550 Failed to change directory.\r\n')
        return True

    def handle_retr(self, file_path):
        # Resolve the path to ensure it's within the jail directory
        resolved_path = self.client_session.resolve_path(file_path)
        if resolved_path is None:
            self.client_session.send_response('550 File not found.\r\n')
            return True

        try:
            # Open the file in the appropriate mode based on the current encoding mode
            mode = 'r' if self.client_session.encoding_mode == 'A' else 'rb'
            with open(resolved_path, mode) as file:
                # Ensure the data connection is ready
                if not self.client_session.data_conn_ready:
                    self.client_session.send_response('425 Can\'t open data connection.\r\n')
                    return True

                self.client_session.send_response('150 Opening data connection.\r\n')

                # Read and send the file in chunks
                while True:
                    file_data = file.read(self.server.bufsiz)  # Use the same buffer size as for the command socket
                    if not file_data:
                        break  # End of file

                    # If in ASCII mode, replace newline characters with CRLF
                    if self.client_session.encoding_mode == 'A':
                        file_data = file_data.replace(os.linesep, '\r\n')

                    # Send data
                    self.client_session.send_data(file_data)

            self.client_session.send_response('226 Transfer complete.\r\n')
        except FileNotFoundError:
            self.client_session.send_response('550 File not found.\r\n')
        except PermissionError:
            self.client_session.send_response('550 Permission denied.\r\n')
        finally:
            # Clean up the data connection
            self.client_session.close_data()

        return True

    def handle_no_auth(self, arg=None):
        response = '530 Not logged in.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_no_data(self, arg=None):
        response = '426 Connection closed; transfer aborted.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_unknown(self, arg=None):
        response = '502 Command not implemented, superfluous at this site.\r\n'
        self.client_session.send_response(response)
        return True




