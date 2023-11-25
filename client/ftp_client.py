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
        return True


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
        try:
            pasv_dest = self.send_pasv()
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.connect(pasv_dest)
            self.pasv_mode = True
        except Exception as e:
            print(f'An error occurred: {e}')
            self.data_socket.close()
            self.data_socket = None
            self.pasv_mode = False
            raise
        return True

    # TODO: refactor this to remove the callback, this is a bad design
    def send_command(self, command='', argument='', success_code='', callback=None):
        if self.cmd_socket:
            argument = ' '+ argument if argument != '' else ''
            self.cmd_socket.sendall(f'{command}{argument}\r\n'.encode('ascii'))

            response = self.recv_response()
            if callback:
                callback(response)
            if response.startswith(success_code):
                return True
            else:
                return False
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
    def send_user(self, username, callback=None):
        return self.send_command('USER', username, '331', callback)
    
    def send_pass(self, password, callback=None):
        return self.send_command('PASS', password, '230', callback)
    
    def send_quit(self, callback=None):
        return self.send_command('QUIT', '', '', callback)

    def send_pwd(self, callback=None):
        responses = []
        def set_response(response):
            responses.append(response)
        ret = self.send_command('PWD', '', '257', set_response)
        # Always update the client to reflect the server's folder
        if ret:
            print(responses)
            _, _, dir = responses.pop().partition(' ')
            self.remote_dir = dir
            print(self.remote_dir)
        return ret
    
    def send_syst(self, callback=None):
        return self.send_command('SYST', '', '215', callback)
    
    def send_type(self, type, callback=None):
        return self.send_command('TYPE', type, '200', callback)
    
    def send_pwd(self, callback=None):
        return self.send_command('PWD', '', '257', callback)

    def send_pasv(self, callback=None):
        pasv_info = { 'ip':'','port':0 }
        def set_pasv_info(response):
            ip_port_data = response[response.index('(')+1:response.index(')')].split(',')
            pasv_info['ip'] = '.'.join(ip_port_data[:4])
            pasv_info['port'] = (int(ip_port_data[4]) << 8) + int(ip_port_data[5])
        if self.send_command('PASV', '', '227', set_pasv_info):
            if callback: callback((pasv_info['ip'], pasv_info['port']))
            return (pasv_info['ip'], pasv_info['port'])
        if callback: callback((None, None))
        return (None, None)
    
    def send_cwd(self, new_dir, callback=None):
        if self.send_command('CWD', new_dir, '250', callback):
            self.remote_dir = new_dir
            print(self.remote_dir)
            return True
        return False
    
    def send_rest(self, offset, callback=None):
        return self.send_command('REST', offset, '350', callback)

    def send_rnfr(self, old_name, callback=None):
        return self.send_command('RNFR', old_name, '350', callback)
    
    def send_rnto(self, new_name, callback=None):
        return self.send_command('RNTO', new_name, '250', callback)
    
    def send_feat(self, callback=None):
        return self.send_command('FEAT', '', '211', callback)
    
    def send_stat(self, path=None, callback=None):
        if not path:
            return self.send_command('STAT', '', '211', callback)
        return self.send_command('STAT', path, '213', callback)
    
    def send_dele(self, file_path, callback=None):
        return self.send_command('DELE', file_path, '250', callback)
    
    def send_rmd(self, file_path, callback=None):
        return self.send_command('RMD', file_path, '250', callback)
    
    def send_mkd(self, file_path, callback=None):
        return self.send_command('MKD', file_path, '257', callback)
    
    def send_dele(self, file_path, callback=None):
        return self.send_command('DELE', file_path, '250', callback)
    
    def send_list(self, file_path, callback=None):
        return self.send_command('LIST', file_path, '150', callback)
    
    def send_retr(self, file_path, callback=None):
        return self.send_command('RETR', file_path, '150', callback)
    
    def send_stor(self, file_path, callback=None):
        return self.send_command('STOR', file_path, '150', callback)
    
    def send_appe(self, file_path, callback=None):
        return self.send_command('APPE', file_path, '150', callback)
    
    def auth_user(self, username, password):
        if self.send_user(username):
            return self.send_pass(password)
        return False

    def send_file_mux(self, file_path, mode, callback=None):
        if mode == 'a':
            return self.send_appe(file_path, callback)
        return self.send_stor(file_path, callback)
    
    def upload_file(self, local_file_path, remote_file_path, mode, restart_offset=0, callback=None):
        if not os.path.isabs(local_file_path):
            local_file_path = os.path.join(self.local_dir, local_file_path)

        if not os.path.isfile(local_file_path):
            if callback: callback(False)
            return False

        _, extension = os.path.splitext(local_file_path)
        if extension in {'.txt', '.csv'}:
            self.encoding_mode = 'A'
        else:
            self.encoding_mode = 'I'
        
        if not self.send_type(self.encoding_mode):
            # TODO: this needs to actually be handled
            return False

        # Open passive connection
        self.connect_pasv()
        # TODO: handle connection exceptions

        if restart_offset:
            self.send_rest(restart_offset)
            # TODO: Check that this was successful

        cmd_sent = self.send_file_mux(remote_file_path, mode, callback)
        if cmd_sent:
             # Open the file in the appropriate mode based on the current encoding mode
            mode = 'r' if self.encoding_mode == 'A' else 'rb'
            with open(local_file_path, mode) as file:
                # Move to the restart offset if specified
                if restart_offset:
                    file.seek(restart_offset)

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

                if not self.recv_response().startswith('226'):
                    # Something went wrong
                    # TODO: transfer may have failed due to type, try a second time with different type    
                    return False
            if callback: callback(True)
            return True
        if callback: callback(False)
        return False
    
    # def retr_file():
    #     None
    
    def delete_file(self, file_path, callback=None):
        # The client and server should match folder locations, so no further handling is required
        return self.send_dele(file_path)

    def list_dir(self, file_path='', callback=None):
        # Establish a passive connection
        self.connect_pasv()
        # Next send list on the command channel and check for 150
        if self.send_list(file_path):
            # We were successful, get the data
            data = self.recv_data()
            self.recv_response() # wait for final confirmation TODO: handle bad responses
            if callback: callback(data)
            return data
        else:
            if callback: callback([])
            return []
    
    def set_local_dir(self, path):
        # If relative path, combine with current local_dir value
        if not os.path.isabs(path):
            path = os.path.join(self.local_dir, path)

        # Check if the path is valid (exists and is a directory)
        if os.path.isdir(path):
            self.local_dir = path
            return True
        return False
    
    def set_remote_dir(self, path):
        # If relative path, combine with current remote_dir value
        if not os.path.isabs(path):
            path = os.path.join(self.remote_dir, path)

        return self.send_cwd(path)