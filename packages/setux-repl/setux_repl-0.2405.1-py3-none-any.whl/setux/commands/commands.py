from pybrary.command import Command, Param

from ..cmd.cmd import get_commands


class Pattern(Param):
    '''Filter pattern
    '''
    name = 'commands_pattern'
    positional = True


class Commands(Command):
    '''List commands
    '''
    Params = [
        Pattern,
    ]

    def run(self):
        target = self.get('target')
        pattern = self.get('commands_pattern')
        commands = get_commands()
        print('commands')
        print('--------')
        width = len(max(commands.keys(), key=len))+4
        for name, command in sorted(commands.items()):
            doc = command.__doc__
            first = doc.split('\n')[0]
            if (
                not pattern
                or pattern in name
                or pattern in first.lower()
            ): print(f'{name:>{width}} {first}')
