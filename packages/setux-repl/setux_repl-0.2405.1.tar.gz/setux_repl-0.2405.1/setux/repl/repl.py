import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

from cmd import Cmd

from setux.main import banner


class Repl(Cmd):
    def __init__(self, target, command):
        self.command = command
        user = target.login.name
        host = target.system.hostname
        self.prompt = f'{user}@{host}: '
        super().__init__()

    def do_help(self, line):
        try:
            self.command(f'help {line}')
        except Exception as x:
            print(f' ! {x}')

    def default(self, line):
        try:
            self.command(line)
        except Exception as x:
            print(f' ! {x}')

    def preloop(self):
        print(banner)
        self.onecmd('infos')

    def do_EOF(self, arg):
        return True


def repl(target, cmd):
    Repl(target, cmd).cmdloop()
