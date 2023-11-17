import socket

class FTPClient:
    def __init__(self, server_address, server_port, bufsize):
        self.server_address = server_address
        self.server_port = server_port
        self.bufsize = bufsize
        self.control_socket = None
        self.data_socket = None
        self.pasv_mode = False

    def connect(self):
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.control_socket.connect((self.server_address, self.server_port))
            # Receive the banner message from the server
            welcome_message = self.control_socket.recv(self.bufsize).decode('ascii')
            print(welcome_message)
            if not welcome_message.startswith('220'):
                # Start of the 220 reply indicates service ready for new user.
                raise ConnectionError("Failed to connect to the FTP server.")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.control_socket.close()
            self.control_socket = None
            raise
        return True

    def authenticate(self, username, password):
        if not self.control_socket:
            raise ConnectionError("Not connected to FTP server.")
        
        # Send the USER command
        self.send_command(f'USER {username}')
        
        # Wait for the password prompt (response code 331)
        user_response = self.control_socket.recv(self.bufsize).decode('ascii')
        print(user_response)
        if not user_response.startswith('331'):
            raise PermissionError("Credentials not accepted by the server.")
        
        # Send the PASS command
        self.send_command(f'PASS {password}')
        
        # Wait for the login response
        pass_response = self.control_socket.recv(self.bufsize).decode('ascii')
        print(pass_response)
        if not pass_response.startswith('230'):
            raise PermissionError("Credentials not accepted, authentication failed.")
        return True

    def enter_passive_mode(self):
        if not self.control_socket:
            raise ConnectionError("Control connection is not established.")

        # Send the PASV command
        self.send_command('PASV')
        
        # Receive and parse the server response
        pasv_response = self.control_socket.recv(self.bufsize).decode('ascii')
        print(pasv_response)
        if not pasv_response.startswith('227'):
            raise ConnectionError("Server did not enter passive mode.")
        
        # Extract the IP address and port from the response
        ip_port_data = pasv_response[pasv_response.index('(')+1:pasv_response.index(')')].split(',')
        pasv_ip = '.'.join(ip_port_data[:4])
        pasv_port = (int(ip_port_data[4]) << 8) + int(ip_port_data[5])  # Convert port to decimal
        
        # Establish the data connection
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.connect((pasv_ip, pasv_port))
        self.pasv_mode = True
        return True

    def list_directory(self, path=""):
        if not self.pasv_mode:
            raise ConnectionError("Not in passive mode. Please enter passive mode before listing directory.")

        # If a path is specified, send it with the LIST command
        if path:
            self.send_command(f"LIST {path}")
        else:
            self.send_command("LIST")
        
        # Read the response from the server on the control connection
        list_response = self.control_socket.recv(self.bufsize).decode('ascii')
        print("Server response:", list_response)
        
        # Check if the server is ready to send the directory list
        if not (list_response.startswith('150') or list_response.startswith('125')):
            raise ConnectionError("Server failed to start transfer.")

        # Receive the directory listing from the data connection
        directory_listing = self.receive_data()

        # Read the final response from the server on the control connection
        final_response = self.control_socket.recv(self.bufsize).decode('ascii')
        print("Final server response:", final_response)
        
        # Check the final response
        if not final_response.startswith('226'):
            raise ConnectionError("Did not receive proper final response from server.")

        return directory_listing

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
                # Send QUIT command to properly close the session
                self.send_command('QUIT')
                # A response is expected but we're closing anyway
                self.control_socket.recv(self.bufsize)
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

    def send_command(self, command):
        if not self.control_socket:
            raise ConnectionError("Not connected to FTP server.")
        
        try:
            command_line = f"{command}\r\n".encode('ascii')
            self.control_socket.sendall(command_line)
        except Exception as e:
            print(f"An error occurred while sending command: {e}")
            raise
        return True

    def receive_data(self):
        if not self.data_socket:
            raise ConnectionError("Data connection not established.")
        
        data = []
        while True:
            chunk = self.data_socket.recv(self.bufsize)
            if not chunk:
                break
            data.append(chunk.decode('ascii'))
        
        # Close the data connection as we've received all the data
        self.data_socket.close()
        self.data_socket = None
        self.pasv_mode = False
        
        return ''.join(data)


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
        print("Connecting to FTP server...")
        ftp_client.connect()
        print("Connected to FTP server.")

        # Authenticate with the FTP server
        print(f"Authenticating as {username}...")
        if ftp_client.authenticate(username, password):
            print("Authentication successful.")
        else:
            print("Authentication failed.")
            return

        # Enter passive mode
        print("Entering passive mode...")
        ftp_client.enter_passive_mode()
        print("Passive mode entered successfully.")

        # List directory contents
        print("Listing directory contents...")
        directory_listing = ftp_client.list_directory()  # Call with no argument to list the current directory
        print("Directory listing received:")
        print(directory_listing)

        # If you've reached this point, all the operations have been successful
        print("All tests passed successfully.")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except PermissionError as e:
        print(f"Authentication error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the client is closed properly
        ftp_client.close()

if __name__ == '__main__':
    main()