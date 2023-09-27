import os
import socket
import threading


HOST = '127.0.0.1'
CMD_PORT = 21
DAT_PORT = 2020
BUFSIZ = 4096
credentials = {'user':'pass'}

class FTPServer:
    def __init__(self, host=HOST, port=CMD_PORT):
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_socket.bind((host, port))
        self.command_socket.listen()
        self.can_connect = threading.Event()
        self.can_connect.set()

    def listen(self):
        print(f"Server listening at {HOST}:{CMD_PORT}")
        while True:
            client_socket, client_address = self.command_socket.accept()
            print("Connection initiated")
            if not self.can_connect.is_set():
                client_socket.send("421 Service not available, closing control connection.\r\n".encode())
                client_socket.close()
            
            self.can_connect.clear()
            client_socket.send('220 Service ready for new user.\r\n'.encode())
            
            transfer_thread = threading.Thread(target=self.handle_transfer, args=(client_socket,))
            transfer_thread.start()
    
    def handle_transfer(self, client_socket):
        auth = False
        username = ''
        
        while True:
            data = client_socket.recv(BUFSIZ).decode()
            if not data:
                self.can_connect.set()
                return

            cmd, _, arg = data.partition(' ')
            cmd, arg = cmd.strip(), arg.strip()
            print(cmd, arg)
            
            if cmd == 'QUIT':
                client_socket.send('221 Service closing control connection.\r\n'.encode())
                client_socket.close()
                self.can_connect.set()
                return
            elif not auth:
                if cmd == 'USER':
                    username = arg
                    client_socket.send('331 User name okay, need password\r\n'.encode())
                elif cmd == 'PASS':
                    if credentials[username] == arg:
                        client_socket.send('230 User logged in, proceed.\r\n'.encode())
                        auth = True
                        continue
                    else:
                        client_socket.send('530 Not logged in.\r\n'.encode())
                else:
                    client_socket.send('530 Not logged in.\r\n'.encode())
            else:
                client_socket.send('202 Command not implemented, superfluous at this site.\r\n'.encode())
    

if __name__ == '__main__':
    ftp_server = FTPServer()
    ftp_server.listen()