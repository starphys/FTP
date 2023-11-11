import os
import socket
import threading
from client_session import ClientSession
from command_parser import FTPCommandParser

HOST = '127.0.0.1'
CMD_PORT = 21
BUFSIZ = 4096

class FTPServer:
    def __init__(self, host=HOST, port=CMD_PORT, jail_dir=None):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.bind((host, port))
        self.connection_socket.listen()
        self.credentials={'user':'pass'}
        self.jail_dir = jail_dir or os.path.join(os.path.curdir, './ftp/') 
        self.can_connect = threading.Event()
        self.can_connect.set()

    def listen(self):
        print(f'Server listening at {HOST}:{CMD_PORT}')

        while True:
            cmd_socket, client_address = self.connection_socket.accept()
            print(f'Connection attempt from {client_address}')

            if not self.can_connect.is_set():
                cmd_socket.sendall('421 Service not available, closing control connection.\r\n'.encode('ascii'))
                cmd_socket.close()
                continue

            self.can_connect.clear()
            cmd_socket.sendall('220 Service ready for new user.\r\n'.encode('ascii'))
            client_session = ClientSession(cmd_socket, self.jail_dir)
            transfer_thread = threading.Thread(target=self.handle_client, args=(client_session,))
            transfer_thread.start()

    def handle_client(self, client_session):
        parser = FTPCommandParser(client_session, self)
        try:
            while True:
                data = client_session.cmd_socket.recv(BUFSIZ).decode()
                # If recv() returns an empty string, the client has closed the connection
                if not data:
                    print("Client disconnected gracefully.")
                    break
                if not parser.parse_command(data):
                    break
        except ConnectionError:
            print("Connection error occurred.")
        # except Exception as e:
        #     print(f"An unexpected error occurred: {e}")
        finally:
            self.cleanup(client_session)

    def cleanup(self, client_session):
        client_session.close()
        self.can_connect.set()
        print('Cleanup complete, server ready for new connection.')


if __name__ == '__main__':
    server = FTPServer()
    server.listen()