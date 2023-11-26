import os
import socket

# Manages the internal state of the client and runs the 
class FTPClient:
    def __init__(self, bufsiz):
        self.bufsiz = bufsiz
        self.cmd_socket = None
        self.data_socket = None
        self.encoding_mode = 'A'
        self.local_dir = os.path.expanduser('~')
        self.remote_dir = '.' #This is just the string we get back from PWD, let the server resolve it to a true path
    
    def close(self):
        if self.data_socket:
            try:
                self.data_socket.close()
            except Exception as e:
                print(f"Error closing data socket: {e}")
            finally:
                self.data_socket = None
        
        if self.cmd_socket:
            try:
                self.send_quit()
            except Exception as e:
                print(f"Error sending QUIT command: {e}")
            finally:
                try:
                    self.cmd_socket.close()
                except Exception as e:
                    print(f"Error closing control socket: {e}")
                finally:
                    self.cmd_socket = None

        print("Client closed.")
        return True, '', ''


    def connect_cmd(self, server_address, server_port, ):
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cmd_socket.connect((server_address, server_port))

            welcome_message = self.cmd_socket.recv(self.bufsiz).decode('ascii').strip()
            print(welcome_message)

            if not welcome_message.startswith('220'):
                raise ConnectionError('Failed to connect to the FTP server.')
        except Exception as e:
            print(f'An error occurred: {e}')
            self.cmd_socket.close()
            self.cmd_socket = None
            raise
        return True
    
    def connect_pasv(self): 
        ret, code, message, pasv_ip, pasv_port = self.send_pasv()
        if ret:
            try:
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.connect((pasv_ip, pasv_port))
                self.pasv_mode = True
                
            except Exception as e:
                print(f'An error occurred: {e}')
                self.data_socket.close()
                self.data_socket = None
                self.pasv_mode = False
                raise
        return ret, code, message

    def send_command(self, command='', argument='', success_code=''):
        if self.cmd_socket:
            argument = ' '+ argument if argument != '' else ''
            self.cmd_socket.sendall(f'{command}{argument}\r\n'.encode('ascii'))

            code, _, message = self.recv_response().partition(' ')
            if code.startswith(success_code):
                return True, code, message
            else:
                return False, code, message
        else:
            raise ConnectionError("No command connection")
    
    def recv_response(self):
        if self.cmd_socket:
            return self.cmd_socket.recv(self.bufsiz).decode('ascii')
        else:
            raise ConnectionError("No command connection")

    def send_data(self, message):
        if self.data_socket:
            if self.encoding_mode == 'A':
                self.data_socket.sendall(message.encode('ascii'))
            else:
                self.data_socket.sendall(message)
        else:
            raise ConnectionError("No data connection")
        
    def recv_data(self):
        if self.data_socket:
            data = []
            while True:
                chunk = self.data_socket.recv(self.bufsiz)
                if not chunk:
                    break
                if self.encoding_mode == 'A':
                    data.append(chunk.decode('ascii'))
                else:
                    data.append(chunk)
            # Close the data connection as we've received all the data
            self.data_socket.close()
            self.data_socket = None
            self.pasv_mode = False
            
            return ''.join(data)
        else:
            raise ConnectionError("No data connection")

# Basic command functions
    def send_user(self, username):
        return self.send_command('USER', username, '331')
    
    def send_pass(self, password):
        return self.send_command('PASS', password, '230')
    
    def send_quit(self):
        return self.send_command('QUIT', '', '')

    def send_pwd(self):
        ret, code, message = self.send_command('PWD', '', '257')
        # Always update the client to reflect the server's folder
        if ret:
            self.remote_dir = message
        return ret, code, message
    
    def send_syst(self):
        return self.send_command('SYST', '', '215')
    
    def send_type(self, type):
        return self.send_command('TYPE', type, '200')
    
    def send_pwd(self):
        return self.send_command('PWD', '', '257')

    def send_pasv(self):
        ret, code, message = self.send_command('PASV', '', '227')
        ip = None
        port = None
        
        if ret:
            ip_port_data = message[message.index('(')+1:message.index(')')].split(',')
            ip = '.'.join(ip_port_data[:4])
            port = (int(ip_port_data[4]) << 8) + int(ip_port_data[5])

        return ret, code, message, ip, port
    
    def send_cwd(self, new_dir):
        ret, code, message = self.send_command('CWD', new_dir, '250')
        if ret:
            self.remote_dir = new_dir
        return ret, code, message
    
    def send_rest(self, offset):
        return self.send_command('REST', offset, '350')

    def send_rnfr(self, old_name):
        return self.send_command('RNFR', old_name, '350')
    
    def send_rnto(self, new_name):
        return self.send_command('RNTO', new_name, '250')
    
    def send_feat(self):
        return self.send_command('FEAT', '', '211')
    
    def send_stat(self, path=None):
        if not path:
            return self.send_command('STAT', '', '211')
        return self.send_command('STAT', path, '213')
    
    def send_dele(self, file_path):
        return self.send_command('DELE', file_path, '250')
    
    def send_rmd(self, file_path):
        return self.send_command('RMD', file_path, '250')
    
    def send_mkd(self, file_path):
        return self.send_command('MKD', file_path, '257')
    
    def send_dele(self, file_path):
        return self.send_command('DELE', file_path, '250')
    
    def send_list(self, file_path):
        return self.send_command('LIST', file_path, '150')
    
    def send_retr(self, file_path):
        return self.send_command('RETR', file_path, '150')
    
    def send_stor(self, file_path):
        return self.send_command('STOR', file_path, '150')
    
    def send_appe(self, file_path):
        return self.send_command('APPE', file_path, '150')
    
    def auth_user(self, username, password):
        ret, code, message = self.send_user(username)
        if ret:
            return self.send_pass(password)
        return ret, code, message

    def send_file_mux(self, file_path, mode):
        if mode == 'a':
            return self.send_appe(file_path)
        return self.send_stor(file_path)
    
    def upload_file(self, local_file_path, remote_file_path, mode, restart_offset=0):
        if not os.path.isabs(local_file_path):
            local_file_path = os.path.join(self.local_dir, local_file_path)

        if not os.path.isfile(local_file_path):
            return False, '', 'File does not exist'

        _, extension = os.path.splitext(local_file_path)
        if extension in {'.txt', '.csv'}:
            self.encoding_mode = 'A'
        else:
            self.encoding_mode = 'I'
        
        type_ret, type_code, type_message = self.send_type(self.encoding_mode)
        if not type_ret:
            # Let the caller decide to retry if they wish
            return type_ret, type_code, type_message 

        # Open passive connection
        pasv_ret, pasv_code, pasv_message = self.connect_pasv()
        if not pasv_ret:
            return pasv_ret, pasv_code, pasv_message
        
        if restart_offset:
            rest_ret, rest_code, rest_message = self.send_rest(restart_offset)
            if not rest_ret:
                return rest_ret, rest_code, rest_message

        cmd_ret, cmd_code, cmd_message = self.send_file_mux(remote_file_path, mode)
        if cmd_ret:
            code, message = '', ''
             # Open the file in the appropriate mode based on the current encoding mode
            mode = 'r' if self.encoding_mode == 'A' else 'rb'
            with open(local_file_path, mode) as file:
                # Move to the restart offset if specified
                if restart_offset:
                    file.seek(restart_offset)

                # TODO: this whole thing should be in a try catch for OS and Connection errors
                # Read and send the file in chunks
                while True:
                    file_data = file.read(self.bufsiz)  # Use the same buffer size as for the command socket
                    if not file_data:
                        break  # End of file

                    # If in ASCII mode, replace newline characters with CRLF
                    if self.encoding_mode == 'A':
                        file_data = file_data.replace(os.linesep, '\r\n')

                    # Send data
                    self.send_data(file_data)

                # Done sending, close socket
                self.data_socket.close()
                self.data_socket = None
                self.pasv_mode = False

                data_resp = self.recv_response()
                code, _, message = data_resp.partition(' ')
                if not data_resp.startswith('226'):   
                    return False, code, message
            return True, code, message
        return cmd_ret, cmd_code, cmd_message
    
    def download_file(self, remote_file_path, local_file_path, restart_offset):
        if not os.path.isabs(local_file_path):
            local_file_path = os.path.join(self.local_dir, local_file_path)

        _, extension = os.path.splitext(local_file_path)
        if extension in {'.txt', '.csv'}:
            self.encoding_mode = 'A'
        else:
            self.encoding_mode = 'I'
        
        type_ret, type_code, type_message = self.send_type(self.encoding_mode)
        if not type_ret:
            # Let the caller decide to retry if they wish
            return type_ret, type_code, type_message 

        # Open passive connection
        pasv_ret, pasv_code, pasv_message = self.connect_pasv()
        if not pasv_ret:
            return pasv_ret, pasv_code, pasv_message

        if restart_offset:
            rest_ret, rest_code, rest_message = self.send_rest(restart_offset)
            if not rest_ret:
                return rest_ret, rest_code, rest_message

        # Next send list on the command channel and check for 150
        cmd_ret, cmd_code, cmd_message = self.send_retr(remote_file_path)
        if cmd_ret:
            # We were successful, get the data
            data = self.recv_data()

            data_resp = self.recv_response()
            code, _, message = data_resp.partition(' ')
            if not data_resp.startswith('226'):   
                return False, code, message
            
            mode = 'a' if restart_offset else 'w'
            mode += '' if self.encoding_mode == 'A' else 'b'
            with open(local_file_path, mode) as file:
                if restart_offset:
                    file.seek(restart_offset)
                file.write(data)

            return True, code, message
        return cmd_ret, cmd_code, cmd_message
    
    def delete_file(self, file_path):
        return self.send_dele(file_path)

    def list_dir(self, file_path=''):
        # Open passive connection
        pasv_ret, pasv_code, pasv_message = self.connect_pasv()
        if not pasv_ret:
            return pasv_ret, pasv_code, pasv_message, []
        
        # Next send list on the command channel and check for 150
        cmd_ret, cmd_code, cmd_message = self.send_list(file_path)
        if cmd_ret:
            # We were successful, get the data
            data = self.recv_data()
            
            data_resp = self.recv_response()
            code, _, message = data_resp.partition(' ')
            if not data_resp.startswith('226'):   
                return False, code, message
            return True, code, message, data
        return cmd_ret, cmd_code, cmd_message, []
    
    def set_local_dir(self, path):
        # If relative path, combine with current local_dir value
        if not os.path.isabs(path):
            path = os.path.join(self.local_dir, path)

        # Check if the path is valid (exists and is a directory)
        if os.path.isdir(path):
            self.local_dir = path
            return True, '', f'Local dir set to {path}'
        return False, '', 'Local dir not changed'
    
    def set_remote_dir(self, path):
        # If relative path, combine with current remote_dir value
        if not os.path.isabs(path):
            path = os.path.join(self.remote_dir, path)
        ret, code, message = self.send_cwd(path)
        if ret:
            return self.list_dir()
        return ret, code, message, []