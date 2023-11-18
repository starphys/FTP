from command_handler import FTPCommandHandler

class FTPCommandParser:
    def __init__(self, client_session, server):
        self.handler = FTPCommandHandler(client_session, server)
        self.client_session = client_session
        self.unauth_command_map = {
            'USER': self.handler.handle_user,
            'PASS': self.handler.handle_pass,
            'QUIT': self.handler.handle_quit
            # [NOOP, HELP, SITE]
        }
        self.command_map = {
            'SYST': self.handler.handle_syst,
            'PWD' : self.handler.handle_pwd,
            'TYPE': self.handler.handle_type,
            'PASV': self.handler.handle_pasv,
            'CWD' : self.handler.handle_cwd,
            'REST': self.handler.handle_rest,
            'RNFR': self.handler.handle_rnfr,
            'RNTO': self.handler.handle_rnto,
            'FEAT': self.handler.handle_feat,
            'STAT': self.handler.handle_stat,
            'DELE': self.handler.handle_dele,
            'RMD' : self.handler.handle_rmd,
            'MKD' : self.handler.handle_mkd
            # [ACCT, CDUP, REIN, MODE, STRU, PORT, ALLO]
        }
        self.data_command_map = {
            'LIST': self.handler.handle_list,
            'RETR': self.handler.handle_retr,
            'STOR': self.handler.handle_stor,
            'APPE': self.handler.handle_appe
            # [NLST,STOU]
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