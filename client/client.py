import socket

# Manages the internal state of the client and runs the 
class FTPClient:
    def __init__(self, bufsize):
        self.bufsize = bufsize
        self.cmd_socket = None
        self.data_socket = None
        self.encoding_mode = 'A'
    
    def close(self):
        if self.data_socket:
            try:
                self.data_socket.close()
            except Exception as e:
                print(f"Error closing data socket: {e}")
            finally:
                self.data_socket = None
        
        if self.control_socket:
            try:
                self.send_quit()
            except Exception as e:
                print(f"Error sending QUIT command: {e}")
            finally:
                try:
                    self.control_socket.close()
                except Exception as e:
                    print(f"Error closing control socket: {e}")
                finally:
                    self.control_socket = None

        print("Connections closed.")
        return True


    def connect_cmd(self, server_address, server_port, ):
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cmd_socket.connect((server_address, server_port))

            welcome_message = self.cmd_socket.recv(self.bufsize).decode('ascii')
            print(welcome_message)

            if not welcome_message.startswith('220'):
                raise ConnectionError('Failed to connect to the FTP server.')
        except Exception as e:
            print(f'An error occurred: {e}')
            self.cmd_socket.close()
            self.cmd_socket = None
            raise
        return True
    
    # TODO: finish and test this
    def connect_pasv(self, ip, port): 
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cmd_socket.connect((ip, port))

            welcome_message = self.cmd_socket.recv(self.bufsize).decode('ascii')
            print(welcome_message)

            if not welcome_message.startswith('220'):
                raise ConnectionError('Failed to connect to the FTP server.')
        except Exception as e:
            print(f'An error occurred: {e}')
            self.cmd_socket.close()
            self.cmd_socket = None
            raise
        return True

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
            return self.cmd_socket.recv(self.bufsize).decode('ascii')
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
            data = self.data_socket.recv(self.bufsiz)
            if self.encoding_mode == 'A':
                return data.decode('ascii')
            return data
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
        return self.send_command('PWD', '', '257', callback)
    
    def send_syst(self, callback=None):
        return self.send_command('SYST', '', '215', callback)
    
    def send_type(self, type, callback=None):
        return self.send_command('TYPE', type, '200', callback)
    
    def send_pwd(self, callback=None):
        return self.send_command('PWD', '', '257', callback)

    def send_pasv(self, callback=None):
        return self.send_command('PASV', '', '227', callback)
    
    def send_cwd(self, new_dir, callback=None):
        return self.send_command('CWD', new_dir, '250', callback)
    
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
    
    # def auth_user():
    #     None

    # def send_file():
    #     None
    
    # def appe_file():
    #     None
    
    # def retr_file():
    #     None
    
    # def list_dir():
    #     None


def main():
    # Replace these with the actual server address and credentials
    server_address = '127.0.0.1'
    server_cmd_port = 21
    bufsize = 4096
    username = 'user'
    password = 'pass'

    # Initialize the FTP client instance
    ftp_client = FTPClient(server_address, server_cmd_port, bufsize)
    
    try:
        # Connect to the FTP server
        print('Connecting to FTP server...')
        ftp_client.connect()
        print('Connected to FTP server.')

        # Authenticate with the FTP server
        print(f'Authenticating as {username}...')
        if ftp_client.authenticate(username, password):
            print('Authentication successful.')
        else:
            print('Authentication failed.')
            return

        # Enter passive mode
        print('Entering passive mode...')
        ftp_client.enter_passive_mode()
        print('Passive mode entered successfully.')

        # List directory contents
        print('Listing directory contents...')
        directory_listing = ftp_client.list_directory()  # Call with no argument to list the current directory
        print('Directory listing received:')
        print(directory_listing)

        # If you've reached this point, all the operations have been successful
        print('All tests passed successfully.')

    except ConnectionError as e:
        print(f'Connection error: {e}')
    except PermissionError as e:
        print(f'Authentication error: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
    finally:
        # Ensure the client is closed properly
        ftp_client.close()

if __name__ == '__main__':
    main()