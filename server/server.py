import os
import queue
import socket
import threading
from client_session import ClientSession
from command_parser import FTPCommandParser

HOST = '127.0.0.1'
CMD_PORT = 21
BUFSIZ = 4096

class FTPServer:
    def __init__(self, host=HOST, port=CMD_PORT, jail_dir=None, bufsiz=BUFSIZ):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.bind((host, port))
        self.connection_socket.listen()
        self.credentials={'user':'pass'}
        self.jail_dir = jail_dir or os.path.join(os.path.curdir, './ftp/') 
        self.bufsiz = bufsiz
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
        handler_thread = threading.Thread(target=self.handle_commands, args=(client_session,))
        handler_thread.start()

        try:
            while not client_session.shutdown_flag.is_set():
                data = client_session.cmd_socket.recv(self.bufsiz).decode()
                # If recv() returns an empty string, the client has closed the connection
                if not data:
                    print('Client disconnected gracefully.')
                    break

                client_session.command_queue.put(data)
                if data.startswith('ABOR'):
                    client_session.abort_flag.set()
        except ConnectionError:
            print('Connection error occurred.')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        finally:
            client_session.shutdown_flag.set()
            handler_thread.join()
            self.cleanup(client_session)


    def handle_commands(self, client_session):
        parser = FTPCommandParser(client_session, self)
        while not client_session.shutdown_flag.is_set():
            try:
                if client_session.abort_flag.is_set():
                    # Clear the queue through the ABOR command
                    client_session.abort_flag.clear()
                    client_session.send_response('226 Closing data connection.\r\n')
                    while not client_session.command_queue.empty() and not client_session.command_queue.get(timeout=.1).startswith('ABOR'):
                        continue
                command = client_session.command_queue.get(timeout=1)  # Adjust timeout as needed
                if not parser.parse_command(command):
                    client_session.shutdown_flag.set()
                    break
            except queue.Empty:
                continue  # No command received, continue the loop
    
    def cleanup(self, client_session):
        client_session.close()
        self.can_connect.set()
        print('Cleanup complete, server ready for new connection.')


if __name__ == '__main__':
    server = FTPServer()
    server.listen()