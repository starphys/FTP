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
           self.client_session.username == 'anonymous' or \
           self.server.credentials.get(self.client_session.username) == password:
            self.client_session.authenticated = True
            response = '230 User logged in, proceed.\r\n'
        else:
            response = '530 Not logged in.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_quit(self, arg=None):
        response = '221 Service closing control connection.\r\n'
        self.client_session.send_response(response)
        return False
    
    def handle_pwd(self, arg=None):
        response = f'257 {self.client_session.get_relative_path()}\r\n'
        self.client_session.send_response(response)
        return True

    def handle_syst(self, arg=None):
        response = f'215 {platform.system()} {platform.release()}\r\n'
        self.client_session.send_response(response)
        return True

    def handle_type(self, mode):
        if mode.upper() == 'A':
            self.client_session.encoding_mode = 'A'
            response = '200 Switching to ASCII mode.\r\n'
        elif mode.upper() == 'I':
            self.client_session.encoding_mode = 'I'
            response = '200 Switching to binary mode.\r\n'
        else:
            response = '504	Command not implemented for that parameter.\r\n'
        self.client_session.send_response(response)
        return True

    def handle_pasv(self, arg=None):
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
    
    def handle_cwd(self, dir_path):
        if self.client_session.change_directory(dir_path):
            self.client_session.send_response('250 Directory successfully changed.\r\n')
        else:
            self.client_session.send_response('550 Failed to change directory.\r\n')
        return True

    def handle_rest(self, offset):
        if self.client_session.encoding_mode == 'A':
            self.client_session.send_response('504 Command not implemented for that parameter in ASCII mode.\r\n')
        try:
            self.client_session.restart_offset = int(offset)
            self.client_session.send_response(f'350 Restarting at {offset}. Send STOR or RETR to initiate transfer.\r\n')
        except ValueError:
            self.client_session.send_response('501 Syntax error in parameters or arguments.\r\n')

    def handle_rnfr(self, path):
        resolved_path = self.client_session.resolve_path(path)
        if resolved_path and os.path.exists(resolved_path):
            self.client_session.rename_from_path = resolved_path
            self.client_session.send_response('350 Requested file action pending further information.\r\n')
        else:
            self.client_session.send_response('550 File or directory not found.\r\n')
        return True

    def handle_rnto(self, new_name):
        if not self.client_session.rename_from_path:
            self.client_session.send_response('503 Bad sequence of commands.\r\n')
            return True

        new_path = self.client_session.resolve_path(new_name)
        if not new_path:
            self.client_session.send_response('553 Invalid path name.\r\n')
            return True

        try:
            os.rename(self.client_session.rename_from_path, new_path)
            self.client_session.send_response('250 File renamed successfully.\r\n')
        except OSError as e:
            self.client_session.send_response(f'550 Rename failed: {e.strerror}\r\n')
        finally:
            self.client_session.rename_from_path = None  # Reset the path

        return True

    def handle_feat(self, arg=None):
        # Add additional features here when implemented i.e. TLS support
        features = ['']
        response = '211 System status, or system help reply.\r\n' #+ '\r\n'.join(features) + '\r\n'
        self.client_session.send_response(response)
        return True

    def handle_stat(self, arg=None):
        if not arg:
            # Server status information
            response = ('211 System status, or system help reply.\r\n' +
                        ' Version: MyFTPServer 1.0\r\n' +
                        f' Current user: {self.client_session.username or "None"}\r\n' +
                        f' Mode: {self.client_session.encoding_mode}\r\n' +
                        '211 End of status\r\n')
            self.client_session.send_response(response)
            return True
        else:
            resolved_path = self.client_session.resolve_path(arg)
            if resolved_path and os.path.exists(resolved_path):
                file_info = format_file_stat(resolved_path)
                response = (f'213 File status.\r\n' +
                            'Status of {arg}:\r\n' +
                            f'{file_info}\r\n' +
                            '213 End of status\r\n')
            else:
                response = '550 File or directory not found.\r\n'

        self.client_session.send_response(response)
        return True
    
    def handle_dele(self, file_path):
        resolved_path = self.client_session.resolve_path(file_path)
        if resolved_path is None or not os.path.isfile(resolved_path):
            self.client_session.send_response('550 File not found.\r\n')
            return True

        try:
            os.remove(resolved_path)
            self.client_session.send_response('250 File deleted successfully.\r\n')
        except PermissionError:
            self.client_session.send_response('550 Permission denied.\r\n')
        except Exception as e:
            self.client_session.send_response(f'550 Error deleting file: {e}\r\n')

        return True

    def handle_rmd(self, dir_path):
        resolved_path = self.client_session.resolve_path(dir_path)
        if resolved_path is None or not os.path.isdir(resolved_path):
            self.client_session.send_response('550 Directory not found.\r\n')
            return True

        try:
            os.rmdir(resolved_path)  # Only removes empty directories
            self.client_session.send_response('250 Directory removed successfully.\r\n')
        except OSError as e:
            self.client_session.send_response(f'550 Remove directory failed: {e.strerror}\r\n')

        return True

    def handle_mkd(self, dir_path):
        resolved_path = self.client_session.resolve_path(dir_path)
        if resolved_path is None:
            self.client_session.send_response('550 Invalid path.\r\n')
            return True

        try:
            os.makedirs(resolved_path, exist_ok=True)
            self.client_session.send_response('257 Directory created successfully.\r\n')
        except OSError as e:
            self.client_session.send_response(f'550 Create directory failed: {e.strerror}\r\n')

        return True
    
    def handle_list(self, dir_path):
        list_dir = self.client_session.resolve_path(dir_path)
        if not list_dir:
            self.client_session.send_response('550	Requested action not taken. File unavailable.\r\n')
        self.client_session.send_response('150	File status okay; about to open data connection.\r\n')

        if self.client_session.abort_flag.is_set():
            self.client_session.send_response('426 Connection closed; transfer aborted.\r\n')
            self.client_session.close_data()
            self.client_session.send_response('226 Closing data connection.\r\n')
            return True

        try:
            files = os.listdir(list_dir) + ['.', '..']
            return_data = [format_file_stat(list_dir, file) for file in files]
            response = '\r\n'.join(return_data) + '\r\n'
            self.client_session.send_data(response)
            self.client_session.send_response('226	Closing data connection. Requested file action successful.\r\n')
        except Exception as e:
            print(e)
            self.client_session.send_response('550	Requested action not taken. File unavailable.\r\n')
        
        self.client_session.close_data()
        return True
    
    def handle_retr(self, file_path):
        # Resolve the path to ensure it's within the jail directory
        resolved_path = self.client_session.resolve_path(file_path)
        if resolved_path is None:
            self.client_session.send_response('550 File not found.\r\n')
            return True

        # Ensure the data connection is ready
        if not self.client_session.data_conn_ready:
            self.client_session.send_response('425 Cannot open data connection.\r\n')
            return True

        try:
            # Open the file in the appropriate mode based on the current encoding mode
            mode = 'r' if self.client_session.encoding_mode == 'A' else 'rb'
            with open(resolved_path, mode) as file:
                # Move to the restart offset if specified
                if self.client_session.restart_offset:
                    file.seek(self.client_session.restart_offset)
                    self.client_session.restart_offset = 0  # Reset the offset after use

                self.client_session.send_response('150 Opening data connection.\r\n')

                # Read and send the file in chunks
                while True:
                    if self.client_session.abort_flag.is_set():
                        self.client_session.send_response('426 Connection closed; transfer aborted.\r\n')
                        self.client_session.close_data()
                        self.client_session.send_response('226 Closing data connection.\r\n')
                        return True

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

    def handle_stor(self, file_path):
        if not self.client_session.data_conn_ready:
            self.client_session.send_response('425 Cannot open data connection.\r\n')
            return True
        resolved_path = self.client_session.resolve_path(file_path, False)
        if resolved_path is None:
            self.client_session.send_response('550 Invalid path.\r\n')
            return True

        try:
            mode = 'w' if self.client_session.encoding_mode == 'A' else 'wb'
            with open(resolved_path, mode) as file:
                if self.client_session.restart_offset:
                    file.seek(self.client_session.restart_offset)
                    self.client_session.restart_offset = 0

                self.client_session.send_response('150 Ok to send data.\r\n')

                while True:
                    if self.client_session.abort_flag.is_set():
                        raise RuntimeError("Transfer aborted by ABOR command.")
                    
                    data = self.client_session.receive_data(self.server.bufsiz)
                    if not data:
                        break
                    file.write(data)
        except OSError as e:
            self.client_session.send_response(f'550 File unavailable: {e.strerror}\r\n')
            try: 
                os.remove(resolved_path)
            except OSError as cleanup_error:
                print(f"Failed to clean up file: {cleanup_error}")
        except RuntimeError as e:
            self.client_session.send_response('426 Connection closed; transfer aborted.\r\n')
        finally:
            self.client_session.close_data()
            self.client_session.send_response('226 Closing data connection.\r\n')
        return True

    def handle_appe(self, file_path):
        if not self.client_session.data_conn_ready:
            self.client_session.send_response('425 Cannot open data connection.\r\n')
            return True
        resolved_path = self.client_session.resolve_path(file_path, False)
        if resolved_path is None:
            self.client_session.send_response('550 Invalid path.\r\n')
            return True

        try:
            mode = 'a' if self.client_session.encoding_mode == 'A' else 'ab'
            with open(resolved_path, mode) as file:
                if self.client_session.restart_offset:
                    file.seek(self.client_session.restart_offset)
                    self.client_session.restart_offset = 0

                self.client_session.send_response('150 Ok to send data.\r\n')

                while True:
                    if self.client_session.abort_flag.is_set():
                        raise RuntimeError("Transfer aborted by ABOR command.")
                    
                    data = self.client_session.receive_data(self.server.bufsiz)
                    if not data:
                        break
                    file.write(data)
        except OSError as e:
            self.client_session.send_response(f'550 File unavailable: {e.strerror}\r\n')
            try: 
                os.remove(resolved_path)
            except OSError as cleanup_error:
                print(f"Failed to clean up file: {cleanup_error}")
        except RuntimeError as e:
            self.client_session.send_response('426 Connection closed; transfer aborted.\r\n')
        finally:
            self.client_session.close_data()
            self.client_session.send_response('226 Closing data connection.\r\n')
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




