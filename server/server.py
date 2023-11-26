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
        self.credentials={'user':'pass', 'anonymous':''}
        self.jail_dir = jail_dir or os.path.join(os.path.curdir, './ftp/') 
        self.bufsiz = bufsiz
        self.can_connect = threading.Lock()

    def listen(self):
        print(f'Server listening at {HOST}:{CMD_PORT}')

        while True:
            cmd_socket, client_address = self.connection_socket.accept()
            print(f'Connection attempt from {client_address}')

            if not self.can_connect.acquire(blocking=False):
                cmd_socket.sendall('421 Service not available, closing control connection.\r\n'.encode('ascii'))
                cmd_socket.close()
                continue

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
                client_session.commands_ready.set()
                if data.startswith('ABOR'):
                    client_session.abort_flag.set()
        except ConnectionError:
            print('Connection error occurred.')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        finally:
            client_session.shutdown_flag.set()
            client_session.commands_ready.set()
            handler_thread.join()
            self.cleanup(client_session)

    def handle_commands(self, client_session):
        parser = FTPCommandParser(client_session, self)
        while client_session.commands_ready.wait():
            if client_session.shutdown_flag.is_set():
                break
            try:
                if client_session.abort_flag.is_set():
                    # Clear the queue through the ABOR command (this should always just send 225, none of the rest of this code should be required)
                    client_session.abort_flag.clear()
                    while not client_session.command_queue.get(block=False).startswith('ABOR'):
                        continue
                    if client_session.data_conn_ready:
                        client_session.send_response('225 Data connection open; no transfer in progress.\r\n')
                    else:
                        client_session.send_response('226 Closing data connection.\r\n')
                command = client_session.command_queue.get(block=False)
                if not parser.parse_command(command):
                    client_session.shutdown_flag.set()
                    break
            except queue.Empty:
                client_session.commands_ready.clear()
    
    def cleanup(self, client_session):
        client_session.close()
        self.can_connect.release()
        print('Cleanup complete, server ready for new connection.')


if __name__ == '__main__':
    server = FTPServer()
    server.listen()