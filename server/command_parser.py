from command_handler import FTPCommandHandler

class FTPCommandParser:
    def __init__(self, client_session, server):
        self.handler = FTPCommandHandler(client_session, server)
        self.client_session = client_session
        self.unauth_command_map = {
            'USER': self.handler.handle_user,
            'PASS': self.handler.handle_pass,
            'QUIT': self.handler.handle_quit
        }
        self.command_map = {
            'SYST': self.handler.handle_syst,
            'PWD' : self.handler.handle_pwd,
            'TYPE': self.handler.handle_type,
            'PASV': self.handler.handle_pasv,
            'CWD' : self.handler.handle_cwd
            # ['REST', 'RNFR', 'RNTO', 'FEAT', 'DELE', 'RMD', 'MKD', 'STAT']
        }
        self.data_command_map = {
            'LIST':self.handler.handle_list
            # ['RETR', 'STOR', 'STOU', 'APPE', 'NLST']
        }

    def parse_command(self, data):
        command, _, argument = data.partition(' ')
        command, argument = command.strip(), argument.strip()
        print(command, argument)

        # Execute commands that don't need authentication or reject
        handler = self.unauth_command_map.get(command.upper())
        if handler:
            return handler(argument)
        if not self.client_session.authenticated:
            return self.handler.handle_no_auth()

        # Execute commands that don't need data connection or reject
        handler = self.command_map.get(command.upper())
        if handler:
            return handler(argument)
        if not self.client_session.data_conn_ready:
            return self.handler.handle_no_data()

        # Execute valid commands or reject
        handler = self.data_command_map.get(command.upper())
        if handler:
            return handler(argument)
        else:
            return self.handler.handle_unknown()