import os
import platform
import socket
import threading
import time


HOST = '127.0.0.1'
CMD_PORT = 21
DAT_PORT = 2020
BUFSIZ = 4096
credentials = {'user':'pass'}
jail_dir = os.path.join(os.path.curdir, 'ftp/')

class FTPServer:
    def __init__(self, host=HOST, port=CMD_PORT):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.bind((host, port))
        self.connection_socket.listen()
        self.can_connect = threading.Event()
        self.can_connect.set()

    def listen(self):
        print(f'Server listening at {HOST}:{CMD_PORT}')

        while True:
            cmd_socket, client_address = self.connection_socket.accept()
            print('Connection initiated')
            if not self.can_connect.is_set():
                cmd_socket.sendall('421 Service not available, closing control connection.\r\n'.encode('ascii'))
                cmd_socket.close()
            
            self.can_connect.clear()
            cmd_socket.sendall('220 Service ready for new user.\r\n'.encode('ascii'))
            
            transfer_thread = threading.Thread(target=self.handle_transfer, args=(cmd_socket,))
            transfer_thread.start()
    
    def handle_transfer(self, cmd_socket):
        auth = False
        username = ''
        cur_dir = jail_dir
        
        pasv_socket = None
        data_socket = None
        data_conn_ready = False

        while True:
            request = cmd_socket.recv(BUFSIZ).decode()
            if not request:
                self.can_connect.set()
                return

            cmd, _, arg = request.partition(' ')
            cmd, arg = cmd.strip(), arg.strip()
            print(cmd, arg)
            
            # We can respond to these before login
            if cmd == 'QUIT':
                cmd_socket.sendall('221 Service closing control connection.\r\n'.encode('ascii'))
                cmd_socket.close()
                self.can_connect.set()
                return
            elif cmd == 'USER':
                    username = arg
                    auth = False
                    if data_socket is not None:
                        data_socket.close()
                        data_socket = None
                        data_conn_ready = False

                    if pasv_socket is not None:
                        pasv_socket.close()
                        pasv_socket = None
                        data_conn_ready = False
                    cmd_socket.sendall('331 User name okay, need password\r\n'.encode('ascii'))
            elif cmd == 'PASS':
                if credentials[username] == arg:
                    cmd_socket.sendall('230 User logged in, proceed.\r\n'.encode('ascii'))
                    auth = True
                else:
                    cmd_socket.sendall('530 Not logged in.\r\n'.encode('ascii'))
            # elif cmd == 'HELP':
            #     # However we want to support help.
            # elif cmd == 'NOOP':
            #     # Noop noop
            
            # Everything else requires login 
            elif auth:
                if cmd == 'PASV':
                    # One passive connection at a time
                    if data_socket is not None:
                        data_socket.close()
                        data_socket = None
                        data_conn_ready = False

                    if pasv_socket is not None:
                        pasv_socket.close()
                        pasv_socket = None
                        data_conn_ready = False

                    # Setup socket on any available port
                    pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pasv_socket.bind(('127.0.0.1', 50888))
                    pasv_socket.listen(1)
                    
                    ip, port = pasv_socket.getsockname()
                    h1, h2, h3, h4 = ip.split('.')
                    p1, p2 = port >> 8, port & 0xff
                    cmd_socket.sendall(f'227 Entering Passive Mode ({h1},{h2},{h3},{h4},{p1},{p2})\r\n'.encode('ascii'))

                    # Wait for data connection
                    data_socket, data_address = pasv_socket.accept()
                    data_conn_ready = True
                # elif cmd == 'ABOR':
                    # Handle aborting data transfer...
                # Optimize this by making dictionaries of commands and helper functions and just indexing into the dictionaries.
                elif cmd in ['REST', 'RNFR', 'RNTO', 'FEAT', 'DELE', 'RMD', 'MKD', 'PWD', 'SYST', 'STAT', 'TYPE']:
                    if cmd == 'SYST':
                        cmd_socket.sendall(f'215 {platform.system()} {platform.release()}\r\n'.encode('ascii'))
                    elif cmd == 'PWD':
                        cmd_socket.sendall(f'257 {os.path.relpath(cur_dir, start=jail_dir)}\r\n'.encode('ascii'))
                    elif cmd == 'TYPE':
                        if arg == 'A':
                            cmd_socket.sendall('200 ASCII supported.\r\n'.encode('ascii'))
                        else:
                            cmd_socket.sendall('504	Command not implemented for that parameter.\r\n'.encode('ascii'))
                    else:
                        cmd_socket.sendall('502 Command not implemented, superfluous at this site.\r\n'.encode('ascii'))   

                elif not data_conn_ready:                   
                    cmd_socket.sendall('426	Connection closed; transfer aborted.\r\n'.encode('ascii'))

                elif cmd in ['RETR', 'STOR', 'STOU', 'APPE', 'LIST', 'NLST']: #At this point we know we have a data connection
                    # These are all data transfer operations.
                    if cmd == 'LIST':
                        cmd_socket.sendall('125 Data connection already open; transfer starting.\r\n'.encode('ascii'))
                        self.handle_list(arg, cmd_socket, data_socket, cur_dir)
                        print("Finished listing, time to shutdown the data socket.")
                        
                    data_socket.close()
                    data_socket = None
                    data_conn_ready = False
                    pasv_socket.close()
                    pasv_socket = None
                else:
                    cmd_socket.sendall('502 Command not implemented, superfluous at this site.\r\n'.encode('ascii'))   
            else:
                cmd_socket.sendall('530 Not logged in.\r\n'.encode('ascii'))

    def handle_list(self, arg, cmd_socket, data_socket, cur_dir):
        list_dir = os.path.realpath(os.path.join(cur_dir, arg)) if arg == '' or arg[0] != '-' else cur_dir

        try:
            files = os.listdir(list_dir) + [".", ".."]
            print(files)
            return_data = [self.format_file_stat(list_dir, file) for file in files]
            response = '\r\n'.join(return_data) + '\r\n'
            print(response)
            data_socket.sendall(response.encode('ascii'))
            cmd_socket.sendall('226	Closing data connection. Requested file action successful.\r\n'.encode('ascii'))
        except Exception as e:
            print(e)
            cmd_socket.sendall('550	Requested action not taken. File unavailable.\r\n'.encode('ascii'))

    def format_file_stat(self, path, name):
        full_path = os.path.join(path, name)
        stats = os.stat(full_path)
        
        # File type
        file_type = '-' if os.path.isfile(full_path) else 'd'
        
        # Permissions
        permissions = {
            '7': 'rwx',
            '6': 'rw-',
            '5': 'r-x',
            '4': 'r--',
            '3': '-wx',
            '2': '-w-',
            '1': '--x',
            '0': '---'
        }
        mode = oct(stats.st_mode)[-3:]
        perm = ''.join([permissions[digit] for digit in mode])
        
        # Number of links
        nlink = stats.st_nlink

        # User and group name
        uid_name = os.getlogin()
        gid_name = os.getlogin()
        
        # File size
        size = stats.st_size
        
        # Date format: 'Month Day HH:MM'
        mtime = time.strftime('%b %d %H:%M', time.gmtime(stats.st_mtime))
        
        return f'{file_type}{perm} {nlink} {uid_name} {gid_name} {size} {mtime} {name}'

        
if __name__ == '__main__':
    ftp_server = FTPServer()
    ftp_server.listen()