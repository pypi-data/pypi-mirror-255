from pybrary.command import Command, Param


class Pattern(Param):
    '''Filter pattern
    '''
    name = 'managers_pattern'
    positional = True


class Managers(Command):
    '''List managers.
    '''
    Params = [
        Pattern,
    ]

    def run(self):
        target = self.get('target')
        pattern = self.get('managers_pattern')
        managers = target.managers
        print('managers')
        print('-------')
        width = len(max(managers.keys(), key=len))+4
        for name, manager in sorted(managers.items()):
            hlp = manager.help()
            first = hlp.split('\n')[0]
            if (
                not pattern
                or pattern in name
                or pattern in first.lower()
            ): print(f'{name:>{width}} {first}')
